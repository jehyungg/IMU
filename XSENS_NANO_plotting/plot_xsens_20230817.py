import matplotlib.pyplot as plt
import csv
import numpy as np
import math
import serial
import csv
from time import sleep, time
from math import sin, cos, tan, pi
from datetime import datetime

class ZoomPan:
    def __init__(self):
        self.press = None
        self.cur_xlim = None
        self.cur_ylim = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xpress = None
        self.ypress = None


    def zoom_factory(self, ax, base_scale = 2.):
        def zoom(event):
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            xdata = event.xdata # get event x location
            ydata = event.ydata # get event y location

            if event.button == 'down':
                # deal with zoom in
                scale_factor = 1 / base_scale
            elif event.button == 'up':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1
                print(event.button)

            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0])

            relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])

            ax.set_xlim([xdata - new_width * (1-relx), xdata + new_width * (relx)])
            ax.set_ylim([ydata - new_height * (1-rely), ydata + new_height * (rely)])
            ax.figure.canvas.draw()

        fig = ax.get_figure() # get the figure of interest
        fig.canvas.mpl_connect('scroll_event', zoom)

        return zoom

    def pan_factory(self, ax):
        def onPress(event):
            if event.inaxes != ax: return
            self.cur_xlim = ax.get_xlim()
            self.cur_ylim = ax.get_ylim()
            self.press = self.x0, self.y0, event.xdata, event.ydata
            self.x0, self.y0, self.xpress, self.ypress = self.press

        def onRelease(event):
            self.press = None
            ax.figure.canvas.draw()

        def onMotion(event):
            if self.press is None: return
            if event.inaxes != ax: return
            dx = event.xdata - self.xpress
            dy = event.ydata - self.ypress
            self.cur_xlim -= dx
            self.cur_ylim -= dy
            ax.set_xlim(self.cur_xlim)
            ax.set_ylim(self.cur_ylim)

            ax.figure.canvas.draw()

        fig = ax.get_figure() # get the figure of interest

        # attach the call back
        fig.canvas.mpl_connect('button_press_event',onPress)
        fig.canvas.mpl_connect('button_release_event',onRelease)
        fig.canvas.mpl_connect('motion_notify_event',onMotion)

        #return the function
        return onMotion
class Serial_Reader:
    def __init__(self, arduino_port, baud, fileName):
        self.arduino_port = arduino_port
        self.baud = baud
        self.fileName = fileName
        
    def read_serial(self, samples):
        ser = serial.Serial(self.arduino_port, self.baud)
        file = open(self.fileName, "a")
        
        line = 0 #start at 0 because our header is 0 (not real data)
        self.sensor_data = [] #store data

        start = datetime.now()
        start_time = start.strftime("%H:%M:%S")
        print("Start Time =", start_time)
        # collect the samples
        while line < samples:
            getData=ser.readline()
            dataString = getData.decode('utf-8')
            data=dataString[0:][:-2]

            readings = data.split(",")

            self.sensor_data.append(readings)
            if(line%(samples/10) == 0):
                print("Progress: ", line/(samples/100), "%")
            line = line+1
        print("Progress: 100%")
        print("Data collection complete!")
        end = datetime.now()
        end_time = end.strftime("%H:%M:%S")
        print("Finish Time =", end_time)
        
        
        # create the CSV
        with open(self.fileName, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(self.sensor_data)

        file.close()
            
    def print_data(self):
        print("Sensor data:")
        print(self.sensor_data)    
class Kalman:
    def __init__(self):
        self.Q_angle = 0.01
        self.Q_bias = 0.03
        self.R_measure = 0.0003

        self.angle = 0.0
        self.bias = 0.0

        self.P = [[0.0, 0.0], [0.0, 0.0]]

    def getAngle(self, newAngle, newRate, dt):
        rate = newRate - self.bias
        self.angle += dt * rate

        self.P[0][0] += dt * (dt * self.P[1][1] - self.P[0][1] - self.P[1][0] + self.Q_angle)
        self.P[0][1] -= dt * self.P[1][1]
        self.P[1][0] -= dt * self.P[1][1]
        self.P[1][1] += self.Q_bias * dt

        S = self.P[0][0] + self.R_measure
        K = [self.P[0][0] / S, self.P[1][0] / S]

        y = newAngle - self.angle
        self.angle += K[0] * y
        self.bias += K[1] * y

        P00_temp = self.P[0][0]
        P01_temp = self.P[0][1]

        self.P[0][0] -= K[0] * P00_temp
        self.P[0][1] -= K[0] * P01_temp
        self.P[1][0] -= K[1] * P00_temp
        self.P[1][1] -= K[1] * P01_temp

        return self.angle

    def setAngle(self, angle):
        self.angle = angle

    def getRate(self):
        return self.rate

    def setQangle(self, Q_angle):
        self.Q_angle = Q_angle

    def setQbias(self, Q_bias):
        self.Q_bias = Q_bias

    def setRmeasure(self, R_measure):
        self.R_measure = R_measure

    def getQangle(self):
        return self.Q_angle

    def getQbias(self):
        return self.Q_bias

    def getRmeasure(self):
        return self.R_measure

data = []
data_kalman = []
start_time = None
kalmanX = Kalman()
kalmanY = Kalman()
# convert constants
RAD_TO_DEG = 180/math.pi
DEG_TO_RAD = math.pi/180
kalAngleX = None
kalAngleY = None

def roll_pitch_calculator(filename, xsens_file):
    index = []
    time = []
    acc_x = []
    acc_y = []
    acc_z = []
    gyro_x = []
    gyro_y = []
    gyro_z = []

    roll = []
    pitch = []
    
    # reading data from a xsens csv file 'Data.csv'
    with open(filename, newline='') as file:
        
        reader = csv.reader(file, delimiter = ',')
        
        # if xsens_file == True:
        #     # store the headers in a separate variable,
        #     # move the reader object to point on the next row
        #     headings = next(reader)
        #     headings = next(reader)
        #     headings = next(reader)
        #     headings = next(reader)
        #     headings = next(reader)
        #     headings = next(reader)
        #     headings = next(reader)
        #     headings = next(reader)
        
        for row in reader:
            index.append(float(row[0]))
            if xsens_file == True:
                time.append(int(row[1]))
                acc_x.append(float(row[2]))
                acc_y.append(float(row[3]))
                acc_z.append(float(row[4]))
                gyro_x.append(float(row[5]))
                gyro_y.append(float(row[6]))
                gyro_z.append(float(row[7]))
            else:
                acc_x.append(float(row[1]))
                acc_y.append(float(row[2]))
                acc_z.append(float(row[3]))
                gyro_x.append(float(row[4]))
                gyro_y.append(float(row[5]))
                gyro_z.append(float(row[6]))
        
        # if xsens_file == True:
        #     index = list_half(index)
        #     time = list_half(time)
        #     acc_x = list_half(acc_x)
        #     acc_y = list_half(acc_y)
        #     acc_z = list_half(acc_z)
        #     gyro_x = list_half(gyro_x)
        #     gyro_y = list_half(gyro_y)
        #     gyro_z = list_half(gyro_z)  
                
    for i in range(len(acc_x)):
        roll.append(math.atan2(acc_y[i], math.sqrt(acc_x[i] ** 2.0 + acc_z[i] ** 2.0)))
        pitch.append(math.atan2(-acc_x[i], math.sqrt(acc_y[i] ** 2.0 + acc_z[i] ** 2.0)))

    return index, roll, pitch
def delete_first_n_rows(input_file, output_file, delete_lines):
    with open(input_file, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        data = list(csvreader)
    
    if len(data) <= delete_lines:
        print("The CSV file contains fewer than five rows. Nothing to delete.")
        return
    
    data = data[delete_lines:]  # Skip the first five rows
    
    with open(output_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(data)
def write_matrix_to_csv_with_index(matrix, file_path):
    with open(file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for idx, row in enumerate(matrix, start=1):
            csvwriter.writerow([idx] + row)     
def make_length_same(input_file_1, input_file_2, output_file_1, output_file_2):
    with open(input_file_1, newline='') as file:
        reader = csv.reader(file, delimiter = ',')
        data_1 = list(reader)
    with open(input_file_2, newline='') as file:
        reader = csv.reader(file, delimiter = ',')
        data_2 = list(reader)
        
    if len(data_1) > len(data_2):
        data_1 = data_1[:len(data_2)]
    elif len(data_1) < len(data_2):
        data_2 = data_2[:len(data_1)]
        
    with open(output_file_1, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(data_1)
    with open(output_file_2, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(data_2)
def get_csv_row_without_first_column(file_path, row_index):
    with open(file_path, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        rows = list(csvreader)
    
    if row_index < 0 or row_index >= len(rows):
        raise IndexError("Row index is out of range.")
    
    row_data = rows[row_index][1:]  # Excluding the first column
    
    return row_data
def get_first_column(csv_file, xsens_file):
    first_column = []
    with open(csv_file, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter = ',')
        # print(csvreader)
        # first_data = list(csvreader)[0][0]
        # print("type of first data: ", type(first_data))
        for row in list(csvreader):
            if row:  # Check if the row is not empty
                first_column.append(int(row[0]))
    first_index = first_column[0]
    for i in range(len(first_column)):
        first_column[i] = first_column[i] - first_index
        
    # if xsens_file == True:
    #     first_column = first_column[:len(first_column)//2]
    return first_column
def count_csv_rows(file_path):
    with open(file_path, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        row_count = sum(1 for _ in csvreader)
    return row_count
def list_half(list):
    result = []
    for i in range(len(list)//2):
        result.append((list[i*2]+list[i*2+1])/2)
    return result
def calculate_rms(data1, data2):
    if len(data1) != len(data2):
        raise ValueError("Data sets must have the same length.")
    
    squared_diffs = [(d1 - d2)**2 for d1, d2 in zip(data1, data2)]
    mean_squared_diff = sum(squared_diffs) / len(data1)
    rms = np.sqrt(mean_squared_diff)
    return rms
def kalman_filter_loop(data_array):
    global start_time, kalmanX, kalmanY, kalAngleX, kalAngleY
    # global start_time, kalmanX_angle
    # global dt, start_time, gyroXrate, gyroYrate, gyroXangle, gyroYangle, kalAngleX, kalAngleY
    data_array = [float(x) for x in data_array]
    if start_time is None:
        dt = 1/20
    else:
        dt = time() - start_time
    start_time = time()

    roll = math.atan2(data_array[1], data_array[2])
    pitch = math.atan(-data_array[0] / math.sqrt(data_array[1] * data_array[1] + data_array[2] * data_array[2]))

    if kalAngleY is None or kalAngleX is None:
        kalAngleX = roll
        kalAngleY = pitch

    gyroXangle = roll
    gyroYangle = pitch

    gyroXrate = data_array[3] * math.pi /(180.0 * 131.0)
    gyroYrate = data_array[4] * math.pi /(180.0 * 131.0)

    if ((roll < -90 * DEG_TO_RAD and kalAngleX > 90 * DEG_TO_RAD) or (roll > 90 * DEG_TO_RAD and kalAngleX < -90 * DEG_TO_RAD)):
        kalmanX.setAngle(roll)
        kalAngleX = roll
        gyroXangle = roll
    else:
        kalAngleX = kalmanX.getAngle(roll, gyroXrate, dt) # // Calculate the angle using a Kalman filter

    if (abs(kalAngleX) > 90 * DEG_TO_RAD):
        gyroYrate = -gyroYrate 

    kalAngleY = kalmanY.getAngle(pitch, gyroYrate, dt)

    gyroXangle += gyroXrate * dt
    gyroYangle += gyroYrate * dt

    if (gyroXangle < -180 * DEG_TO_RAD or gyroXangle > 180 * DEG_TO_RAD):
        gyroXangle = kalAngleX
    if (gyroYangle < -180 * DEG_TO_RAD or gyroYangle > 180 * DEG_TO_RAD):
        gyroYangle = kalAngleY

    return np.array([roll, kalAngleX, pitch, kalAngleY])
##

################## Parameters ##################
starting_index_arduino = 0
starting_index_xsens = 2*19


################## File Name ##################
xsens_raw_file = '15_20230721_152126_091.csv'
arduino_raw_file = 'serial_data_230721_2.csv'
################################################
# sr = Serial_Reader("COM3", 9600, "analog-data.csv")
# sr.read_serial(length_of_arduino_data)


delete_first_n_rows(arduino_raw_file, 'arduino_data.csv', starting_index_arduino)
delete_first_n_rows(xsens_raw_file, 'xsens_data.csv', 13+starting_index_xsens)
make_length_same('arduino_data.csv', 'xsens_data.csv', 'arduino_data.csv', 'xsens_data.csv')
for i in range(count_csv_rows('arduino_data.csv')):
    data_kalman.append(kalman_filter_loop(get_csv_row_without_first_column('arduino_data.csv', i)))
write_matrix_to_csv_with_index(data_kalman, 'data_kalman.csv')
roll_arduino_kal = [row[1] for row in data_kalman]
pitch_arduino_kal = [row[3] for row in data_kalman]
index_arduino, roll_arduino, pitch_arduino = roll_pitch_calculator('arduino_data.csv', False)
index_xsens, roll_xsens, pitch_xsens = roll_pitch_calculator('xsens_data.csv', True)
print("RMS of pitch: ", calculate_rms(pitch_arduino_kal, pitch_xsens))
print("RMS of roll: ", calculate_rms(roll_arduino_kal, roll_xsens))

# plotting
print("start plotting")
fig = plt.figure()
xsens = fig.add_subplot(111)
xsens.set_title("Roll")
xsens.plot(get_first_column('arduino_data.csv', False), roll_arduino_kal, label = 'roll_arduino_kalman', linewidth=0.7, color = 'b')
xsens.plot(get_first_column('arduino_data.csv', False), roll_arduino, label = 'roll_arduino', linewidth=0.7, color = 'r')
xsens.plot(get_first_column('xsens_data.csv', True), roll_xsens, label = 'roll_xsens', linewidth=0.7, color = 'g')
xsens.legend(['NANO 33 IOT Kalman', 'NANO 33 IOT', 'xsens'], loc='upper right')
plt.title('Plotting')
plt.xlabel('frame')
plt.ylabel('roll[rad]')

scale = 1.2
zp = ZoomPan()
figZoom = zp.zoom_factory(xsens, base_scale = scale)
figPan = zp.pan_factory(xsens)

plt.show()

def calculate_rms(data1, data2):
    if len(data1) != len(data2):
        raise ValueError("Data sets must have the same length.")
    
    squared_diffs = [(d1 - d2)**2 for d1, d2 in zip(data1, data2)]
    mean_squared_diff = sum(squared_diffs) / len(data1)
    rms = np.sqrt(mean_squared_diff)
    return rms