import paho.mqtt.client as mqtt
import json
import matplotlib.pyplot as plt
import numpy as np
import math
from time import sleep, time
from math import sin, cos, tan, pi
from matplotlib.animation import FuncAnimation
from ahrs.filters import Madgwick

# https://github.com/TKJElectronics/KalmanFilter/blob/master/examples/MPU6050/MPU6050.ino

data = []

username = "nmail"
password = "74269"


# Paramaeters
FREQUENCY = 20.  # Sampling rate (in Herz)

# convert constants
RAD_TO_DEG = 180/math.pi
DEG_TO_RAD = math.pi/180

madgwick_filter = Madgwick(frequency=FREQUENCY, gain=0.4)
Quaternion = np.array([1., 0., 0., 0.])
# Quaternion = np.array([0.7071, 0.0, 0.7071, 0.0])

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
	global data, Quaternion, madgwick_filter
	y = json.loads(msg.payload.decode("utf-8"))
	
	gyroscope = np.array([y["imu"]["gX"], y["imu"]["gY"], y["imu"]["gZ"]]) * DEG_TO_RAD
	acceleration = np.array([y["imu"]["aX"], y["imu"]["aY"], y["imu"]["aZ"]]) * 9.8

	# madgwick = Madgwick(gyr=gyroscope, acc=acceleration)
	Quaternion = madgwick_filter.updateIMU(Quaternion, gyroscope, acceleration)
    
	# Quaternion = madgwick_filter.updateIMU(q=[0.7071, 0.0, 0.7071, 0.0], gyr = gyroscope, acc = acceleration)
	# filtered_roll, filtered_pitch, _ = madgwick_filter.quaternion.to_euler(Quaternion)

	roll = math.atan2(y["imu"]["aY"], y["imu"]["aZ"])
	pitch = math.atan(-y["imu"]["aX"] / math.sqrt(y["imu"]["aY"] ** 2 + y["imu"]["aZ"] ** 2))
	
	print("this is madgwick filter: ")
	# print(madgwick_filter.Quaternion)
	print(Quaternion)
	#filtered_roll, filtered_pitch, _ = madgwick_filter.to_euler(Quaternion)
	#data.append([roll, filtered_roll, pitch, filtered_pitch])
	#data.append([roll, filtered_roll, pitch, filtered_pitch])
	
	[w, x, y, z] = Quaternion

    # Convert quaternion to Euler angles (roll, pitch, yaw)
	filtered_roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
	filtered_pitch = math.asin(2 * (w * y - z * x))
	yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))

	while len(data) > 20*2:
		data = data[1:]
	# print(aX, aY, aZ, gX, gY, gZ)
	data.append([roll, filtered_roll, pitch, filtered_pitch])



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
fig.suptitle('Madgwick Filter')
plt_roll_raw = plt.subplot(231)
plt_roll_kal = plt.subplot(232)
plt_roll_raw_kal = plt.subplot(233)
plt_pitch_raw = plt.subplot(234)
plt_pitch_kal = plt.subplot(235)
plt_pitch_raw_kal = plt.subplot(236)

plt.title('NANO 33 IOT')

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