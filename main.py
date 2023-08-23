import matplotlib.pyplot as plt
import csv
import numpy as np
import math
import csv
from time import sleep, time
from math import sin, cos, tan, pi
from datetime import datetime
from dataprocessing import *
from plotting import *

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

if __name__ == '__main__':
    ################## Parameters ##################
    name = '230721_2'
    starting_index_arduino = 0
    starting_index_xsens = 2*19
    ################################################
    
    # Set global variables
    data = []
    data_kalman = []
    start_time = None
    kalmanX = Kalman()
    kalmanY = Kalman()
    RAD_TO_DEG = 180/math.pi
    DEG_TO_RAD = math.pi/180
    kalAngleX = None
    kalAngleY = None

    # Set file names
    xsens_raw_file = './data/xsens_{}.csv'.format(name)
    arduino_raw_file = './data/arduino_{}.csv'.format(name)
    xsens_processed_file = './temp/xsens_processed_{}.csv'.format(name)
    arduino_processed_file = './temp/arduino_processed_{}.csv'.format(name)
    kalman_file = './temp/data_kalman_{}.csv'.format(name)
    
    # Prepare each file
    delete_first_n_rows(arduino_raw_file, arduino_processed_file, starting_index_arduino)
    delete_first_n_rows(xsens_raw_file, xsens_processed_file, 13+starting_index_xsens)
    make_length_same(arduino_processed_file, xsens_processed_file, arduino_processed_file, xsens_processed_file)

    # Apply Kalman filtering
    for i in range(count_csv_rows(arduino_processed_file)):
        data_kalman.append(kalman_filter_loop(get_csv_row_without_first_column(arduino_processed_file, i)))
    write_matrix_to_csv_with_index(data_kalman, kalman_file)

    # Calculate RMS
    roll_arduino_kal = [row[1] for row in data_kalman]
    pitch_arduino_kal = [row[3] for row in data_kalman]
    index_arduino, roll_arduino, pitch_arduino = roll_pitch_calculator(arduino_processed_file, False)
    index_xsens, roll_xsens, pitch_xsens = roll_pitch_calculator(xsens_processed_file, True)
    print("RMS of pitch: ", calculate_rms(pitch_arduino_kal, pitch_xsens))
    print("RMS of roll: ", calculate_rms(roll_arduino_kal, roll_xsens))

    # Plot the results
    print("start plotting")
    fig = plt.figure()
    xsens = fig.add_subplot(111)
    xsens.set_title("Roll")
    xsens.plot(get_first_column(arduino_processed_file, False), roll_arduino_kal, label = 'roll_arduino_kalman', linewidth=0.7, color = 'b')
    xsens.plot(get_first_column(arduino_processed_file, False), roll_arduino, label = 'roll_arduino', linewidth=0.7, color = 'r')
    xsens.plot(get_first_column(xsens_processed_file, True), roll_xsens, label = 'roll_xsens', linewidth=0.7, color = 'g')
    xsens.legend(['NANO 33 IOT Kalman', 'NANO 33 IOT', 'xsens'], loc='upper right')
    plt.title('Plotting')
    plt.xlabel('frame')
    plt.ylabel('roll[rad]')
    scale = 1.2
    zp = ZoomPan()
    figZoom = zp.zoom_factory(xsens, base_scale = scale)
    figPan = zp.pan_factory(xsens)
    plt.show()