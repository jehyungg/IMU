import paho.mqtt.client as mqtt
import json
import matplotlib.pyplot as plt
import numpy as np
import math
from time import sleep, time
from math import sin, cos, tan, pi
from matplotlib.animation import FuncAnimation

data = []

username = "nmail"
password = "74269"

# Iterations and sleep time
N = 1000
sleep_time = 0.01

# Filter coefficient
alpha = 0.1

# Complimentary filter estimates
phi_hat = 0.0
theta_hat = 0.0

#gyro bias
count_bias = 0
bias_x = 0.0
bias_y = 0.0
bias_z = 0.0

#time
dt = 0.0
start_time = 0

def complementary_filter(data_array):
	global start_time
	global phi_hat
	global theta_hat
	dt = time() - start_time
	start_time = time()

	[phi_hat_acc, theta_hat_acc] = get_acc_angles(data_array) 

	# Get raw gyro data and subtract biases
	[p, q, r] = get_gyro(data_array)


	p -= bias_x
	q -= bias_y
	r -= bias_z

	# Calculate Euler angle derivatives 
	phi_dot = p + sin(phi_hat) * tan(theta_hat) * q + cos(phi_hat) * tan(theta_hat) * r
	theta_dot = cos(phi_hat) * q - sin(phi_hat) * r

	# Update complimentary filter
	phi_hat = (1 - alpha) * (phi_hat + dt * phi_dot) + alpha * phi_hat_acc
	theta_hat = (1 - alpha) * (theta_hat + dt * theta_dot) + alpha * theta_hat_acc   

	return np.array([phi_hat_acc, phi_hat, theta_hat_acc, theta_hat])

	# # rad/s
	# def get_gyro_bias(N, data_array):
	#         bx = 0.0
	#         by = 0.0
	#         bz = 0.0
			
	#         for i in range(N):
	#             [gx, gy, gz] = data_array[3:]
	#             bx += gx
	#             by += gy
	#             bz += gz
	#             sleep(0.01)
				
	#         return [bx / float(N), by / float(N), bz / float(N)]        


def get_acc_angles(data_array):
	[get_acc_angles_ax, get_acc_angles_ay, get_acc_angles_az] = data_array[:3]
	get_acc_angles_ax /= 16384.0 
	get_acc_angles_ay /= 16384.0
	get_acc_angles_az /= 16384.0
	# get roll
	phi = math.atan2(get_acc_angles_ay, math.sqrt(get_acc_angles_ax ** 2.0 + get_acc_angles_az ** 2.0))
	# get pitch
	theta = math.atan2(-get_acc_angles_ax, math.sqrt(get_acc_angles_ay ** 2.0 + get_acc_angles_az ** 2.0))
	
	return np.array([phi, theta])

def get_gyro(data_array):
	[p, q, r] = data_array[3:]
	gx = p * math.pi /(180.0 * 131.0)
	gy = q * math.pi /(180.0 * 131.0)
	gz = r * math.pi /(180.0 * 131.0)

	return [gx, gy, gz]
	


	


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
	global data
	global count_bias
	global bias_x
	global bias_y
	global bias_z
	y = json.loads(msg.payload.decode("utf-8"))
	
	# aX = float(y["imu"]["aX"])
	# aY = float(y["imu"]["aY"])
	# aZ = float(y["imu"]["aZ"])
	# gX = float(y["imu"]["gX"])
	# gY = float(y["imu"]["gY"])
	# gZ = float(y["imu"]["gZ"])

	aX = y["imu"]["aX"]
	gX = y["imu"]["gX"]
	aY = y["imu"]["aY"]
	gZ = y["imu"]["gZ"]
	aZ = y["imu"]["aZ"]
	gY = y["imu"]["gY"]

	data.append(complementary_filter([aX, aY, aZ, gX, gY, gZ]))

	# get gyro bias
	
	while(count_bias < 40):
		count_bias += 1
		bias_x += gX
		bias_y += gY
		bias_z += gZ

	if(count_bias==40):
		bias_x /= 40
		bias_y /= 40
		bias_z /= 40
	
	

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
plt_roll_cmp = plt.subplot(232)
plt_roll_raw_cmp = plt.subplot(233)
plt_pitch_raw = plt.subplot(234)
plt_pitch_cmp = plt.subplot(235)
plt_pitch_raw_cmp = plt.subplot(236)

fig.suptitle('Comeplementary Filter')

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
	
	# plot roll_cmp
	plt_roll_cmp.cla()
	plt_roll_cmp.set_ylim(-roll_ylimit,roll_ylimit)
	plt_roll_cmp.plot(temp_data[:,1], label='roll_cmp', color = 'g')
	plt_roll_cmp.set_xlabel('roll_cmp')
	plt_roll_cmp.set_ylabel('(rad)')
	
	# plot roll_raw_cmp
	plt_roll_raw_cmp.cla()
	plt_roll_raw_cmp.set_ylim(-roll_ylimit,roll_ylimit)
	plt_roll_raw_cmp.plot(temp_data[:,0], label='roll_cmp', color = 'r')
	plt_roll_raw_cmp.plot(temp_data[:,1], label='roll_raw_cmp', color = 'g')
	plt_roll_raw_cmp.set_xlabel('roll_raw_cmp')
	plt_roll_raw_cmp.set_ylabel('(rad)')

	pitch_ylimit = 3
	# plot pitch_raw
	plt_pitch_raw.cla()
	plt_pitch_raw.set_ylim(-pitch_ylimit,pitch_ylimit)
	plt_pitch_raw.plot(temp_data[:,2], label='pitch_raw', color = 'y')
	plt_pitch_raw.set_xlabel('pitch_raw')
	plt_pitch_raw.set_ylabel('(rad)')
	
	# plot pitch_cmp
	plt_pitch_cmp.cla()
	plt_pitch_cmp.set_ylim(-pitch_ylimit,pitch_ylimit)
	plt_pitch_cmp.plot(temp_data[:,3], label='pitch_cmp', color = 'b')
	plt_pitch_cmp.set_xlabel('pitch_cmp')
	plt_pitch_cmp.set_ylabel('(rad)')
	
	# plot pitch_raw_cmp
	plt_pitch_raw_cmp.cla()
	plt_pitch_raw_cmp.set_ylim(-pitch_ylimit,pitch_ylimit)
	plt_pitch_raw_cmp.plot(temp_data[:,2], label='pitch_cmp', color = 'y')
	plt_pitch_raw_cmp.plot(temp_data[:,3], label='pitch_raw_cmp', color = 'b')
	plt_pitch_raw_cmp.set_xlabel('pitch_raw_cmp')
	plt_pitch_raw_cmp.set_ylabel('(rad)')




ani = FuncAnimation(fig, plot_data, interval = 0.01, cache_frame_data=False)


plt.show()


subscriber.loop_stop()