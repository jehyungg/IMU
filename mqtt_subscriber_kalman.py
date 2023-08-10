import paho.mqtt.client as mqtt
import json
import matplotlib.pyplot as plt
import numpy as np
import math
from time import sleep, time
from math import sin, cos, tan, pi
from matplotlib.animation import FuncAnimation

# https://github.com/TKJElectronics/KalmanFilter/blob/master/examples/MPU6050/MPU6050.ino

data = []

username = "nmail"
password = "74269"

# Iterations and sleep time
N = 1000
sleep_time = 0.01

# Filter coefficient
alpha = 0.1

# Constant for set
c = 0

# Angle info
kalmanX_angle = 0.0
kalmanX_bias = 0.0

kalmanY_angle = 0.0
kalmanY_bias = 0.0

Q_angle = 0.001
Q_bias = 0.003
R_measure = 0.03

gyroXangle = 0.0
gyroYangle = 0.0
gyroXrate = 0.0
gyroYrate = 0.0
kalAngleX = 0.0
kalAngleY = 0.0

# matrix
P = [[0.0] * 2] * 2



# convert constants
RAD_TO_DEG = 180/math.pi
DEG_TO_RAD = math.pi/180

#time
dt = 0.0
start_time = 0

def kalman_filter_setup(data_array):
	global gyroXangle, gyroYangle, kalmanX_angle, kalmanY_angle

	roll = math.atan2(data_array[1], data_array[2])
	pitch = math.atan(-data_array[0] / math.sqrt(data_array[1] * data_array[1] + data_array[2] * data_array[2]))

	kalmanX_angle = roll
	kalmanY_angle = pitch
	gyroXangle = roll
	gyroYangle = pitch



def kalman_filter_loop(data_array):
	global start_time, kalmanX_angle
	global dt, start_time, gyroXrate, gyroYrate, gyroXangle, gyroYangle, kalAngleX, kalAngleY

	dt = time() - start_time
	start_time = time()
	
	roll = math.atan2(data_array[1], data_array[2])
	pitch = math.atan(-data_array[0] / math.sqrt(data_array[1] * data_array[1] + data_array[2] * data_array[2]))

	gyroXrate = data_array[3] * math.pi /(180.0 * 131.0)
	gyroYrate = data_array[4] * math.pi /(180.0 * 131.0)

	gyroXangle = roll
	gyroYangle = pitch

	if ((roll < -90 * DEG_TO_RAD and kalAngleX > 90 * DEG_TO_RAD) or (roll > 90 * DEG_TO_RAD and kalAngleX < -90 * DEG_TO_RAD)):
		kalmanX_angle = roll
		kalAngleX = roll
		gyroXangle = roll
	else:
		kalAngleX = kalmanX_getAngle(roll, gyroXrate, dt) # // Calculate the angle using a Kalman filter

	if (abs(kalAngleX) > 90 * DEG_TO_RAD):
		gyroYrate = -gyroYrate 
	
	kalAngleY = kalmanY_getAngle(pitch, gyroYrate, dt)

	gyroXangle += gyroXrate * dt
	gyroYangle += gyroYrate * dt

	if (gyroXangle < -180 * DEG_TO_RAD or gyroXangle > 180 * DEG_TO_RAD):
		gyroXangle = kalAngleX
	if (gyroYangle < -180 * DEG_TO_RAD or gyroYangle > 180 * DEG_TO_RAD):
		gyroYangle = kalAngleY
 

	return np.array([roll, kalAngleX, pitch, kalAngleY])


def kalmanX_getAngle(newAngle, newRate, dt):
	global kalmanX_bias, kalmanX_angle, P, Q_angle, Q_bias, R_measure
	rate = newRate - kalmanX_bias
	kalmanX_angle += dt * rate
    
	
	P[0][0] += dt * (dt*P[1][1] - P[0][1] - P[1][0] + Q_angle)
	P[0][1] -= dt * P[1][1]
	P[1][0] -= dt * P[1][1]
	P[1][1] += Q_bias * dt
    
	S = P[0][0] + R_measure

	K = [0] * 2
	K[0] = P[0][0] / S
	K[1] = P[1][0] / S

	y = newAngle - kalmanX_angle
	kalmanX_angle += K[0] * y
	kalmanX_bias += K[1] * y
    
	P00_temp = P[0][0]
	P01_temp = P[0][1]

	P[0][0] -= K[0] * P00_temp
	P[0][1] -= K[0] * P01_temp
	P[1][0] -= K[1] * P00_temp
	P[1][1] -= K[1] * P01_temp

	return kalmanX_angle


def kalmanY_getAngle(newAngle, newRate, dt):
	global kalmanY_bias, kalmanY_angle, P, Q_angle, Q_bias, R_measure
	rate = newRate - kalmanY_bias
	kalmanY_angle += dt * rate
    
	
	P[0][0] += dt * (dt*P[1][1] - P[0][1] - P[1][0] + Q_angle)
	P[0][1] -= dt * P[1][1]
	P[1][0] -= dt * P[1][1]
	P[1][1] += Q_bias * dt
    
	S = P[0][0] + R_measure

	K = [0] * 2
	K[0] = P[0][0] / S
	K[1] = P[1][0] / S

	y = newAngle - kalmanY_angle
	kalmanY_angle += K[0] * y
	kalmanY_bias += K[1] * y
    
	P00_temp = P[0][0]
	P01_temp = P[0][1]

	P[0][0] -= K[0] * P00_temp
	P[0][1] -= K[0] * P01_temp
	P[1][0] -= K[1] * P00_temp
	P[1][1] -= K[1] * P01_temp

	return kalmanY_angle
	


	


def on_connect(client, userdata, flags, rc):
	'''
    Runs when client is connected to broker
    '''
	if rc==0:
		print("connected OK")
	else:
		print("Bad connection Returned code=",rc)

def on_message(client, userdata, msg):
	# print(str(msg.payload.decode("utf-8")))
	global data, c
	y = json.loads(msg.payload.decode("utf-8"))
	
	# aX = float(y["imu"]["aX"])
	# aY = float(y["imu"]["aY"])
	# aZ = float(y["imu"]["aZ"])
	# gX = float(y["imu"]["gX"])
	# gY = float(y["imu"]["gY"])
	# gZ = float(y["imu"]["gZ"])

	aX = y["imu"]["aX"]
	aY = y["imu"]["aY"]
	aZ = y["imu"]["aZ"]

	gX = y["imu"]["gX"]
	gZ = y["imu"]["gZ"]
	gY = y["imu"]["gY"]

	if(c!=0):
		kalman_filter_setup([aX, aY, aZ, gX, gY, gZ])
		c += 1
	else:
		data.append(kalman_filter_loop([aX, aY, aZ, gX, gY, gZ]))

	

	while len(data) > 20*2:
		data = data[1:]
	# print(aX, aY, aZ, gX, gY, gZ)



subscriber = mqtt.Client()
subscriber.on_connect = on_connect
subscriber.on_message = on_message

# subscriber.connect("mqtt.pumpkinhouse.io")
subscriber.username_pw_set(username, password)
subscriber.connect("143.248.143.21")
subscriber.subscribe("nmail/")

subscriber.loop_start()

# Main Thread
# Figure Define
fig = plt.figure(figsize = (16,8), facecolor='#DEDEDE')
plt_roll_raw = plt.subplot(231)
plt_roll_kal = plt.subplot(232)
plt_roll_raw_kal = plt.subplot(233)
plt_pitch_raw = plt.subplot(234)
plt_pitch_kal = plt.subplot(235)
plt_pitch_raw_kal = plt.subplot(236)

plt.title('NANO 33 IOT')
fig.suptitle('Kalman Filter')

WindowSeconds = 2

def plot_data(_):
	if len(data)<WindowSeconds*20:
		return
	# temp = data.copy()
	temp_data = np.array(data)

	roll_ylimit = 3
	# plot roll_raw
	plt_roll_raw.cla()
	plt_roll_raw.set_ylim(-roll_ylimit,roll_ylimit)
	plt_roll_raw.plot(temp_data[:,0], label='roll_raw', color = 'r')
	plt_roll_raw.set_xlabel('roll_raw')
	plt_roll_raw.set_ylabel('(rad)')
	
	# plot roll_kal
	plt_roll_kal.cla()
	plt_roll_kal.set_ylim(-roll_ylimit,roll_ylimit)
	plt_roll_kal.plot(temp_data[:,1], label='roll_kal', color = 'g')
	plt_roll_kal.set_xlabel('roll_kal')
	plt_roll_kal.set_ylabel('(rad)')
	
	# plot roll_raw_kal
	plt_roll_raw_kal.cla()
	plt_roll_raw_kal.set_ylim(-roll_ylimit,roll_ylimit)
	plt_roll_raw_kal.plot(temp_data[:,0], label='roll_kal', color = 'r')
	plt_roll_raw_kal.plot(temp_data[:,1], label='roll_raw_kal', color = 'g')
	plt_roll_raw_kal.set_xlabel('roll_raw_kal')
	plt_roll_raw_kal.set_ylabel('(rad)')

	pitch_ylimit = 3
	# plot pitch_raw
	plt_pitch_raw.cla()
	plt_pitch_raw.set_ylim(-pitch_ylimit,pitch_ylimit)
	plt_pitch_raw.plot(temp_data[:,2], label='pitch_raw', color = 'y')
	plt_pitch_raw.set_xlabel('pitch_raw')
	plt_pitch_raw.set_ylabel('(rad)')
	
	# plot pitch_kal
	plt_pitch_kal.cla()
	plt_pitch_kal.set_ylim(-pitch_ylimit,pitch_ylimit)
	plt_pitch_kal.plot(temp_data[:,3], label='pitch_kal', color = 'b')
	plt_pitch_kal.set_xlabel('pitch_kal')
	plt_pitch_kal.set_ylabel('(rad)')
	
	# plot pitch_raw_kal
	plt_pitch_raw_kal.cla()
	plt_pitch_raw_kal.set_ylim(-pitch_ylimit,pitch_ylimit)
	plt_pitch_raw_kal.plot(temp_data[:,2], label='pitch_kal', color = 'y')
	plt_pitch_raw_kal.plot(temp_data[:,3], label='pitch_raw_kal', color = 'b')
	plt_pitch_raw_kal.set_xlabel('pitch_raw_kal')
	plt_pitch_raw_kal.set_ylabel('(rad)')




ani = FuncAnimation(fig, plot_data, interval = 0.01, cache_frame_data=False)


plt.show()


subscriber.loop_stop()