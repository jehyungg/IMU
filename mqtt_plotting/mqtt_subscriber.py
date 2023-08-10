import paho.mqtt.client as mqtt
import json
import matplotlib.pyplot as plt
import time
import numpy as np
from matplotlib.animation import FuncAnimation

data = []

username = "nmail"
password = "74269"

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

	data.append([aX, aY, aZ, gX, gY, gZ])

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
plt_acc_x = plt.subplot(241)
plt_acc_y = plt.subplot(242)
plt_acc_z = plt.subplot(243)
plt_gyro_x = plt.subplot(245)
plt_gyro_y = plt.subplot(246)
plt_gyro_z = plt.subplot(247)
plt_acc_xyz = plt.subplot(244)
plt_gyro_xyz = plt.subplot(248)

plt.title('NANO 33 IOT')

WindowSeconds = 2

def plot_data(_):
	if len(data)<WindowSeconds*20:
		return
	# temp = data.copy()
	temp_data = np.array(data)

	acc_plt_ylimit = 4
	# plot acc x
	plt_acc_x.cla()
	plt_acc_x.set_ylim(-acc_plt_ylimit,acc_plt_ylimit)
	plt_acc_x.plot(temp_data[:,0], label='Acc X', color = 'r')
	plt_acc_x.set_xlabel('acc x')
    # ax.scatter(len(acc_x)-1, acc_x[-1]) 

	# plot acc y
	plt_acc_y.cla()
	plt_acc_y.set_ylim(-acc_plt_ylimit,acc_plt_ylimit)
	plt_acc_y.plot(temp_data[:,1], label='Acc Y', color = 'g')
	plt_acc_y.set_xlabel('acc y')

	# plot acc z
	plt_acc_z.cla()
	plt_acc_z.set_ylim(-acc_plt_ylimit,acc_plt_ylimit)
	plt_acc_z.plot(temp_data[:,2], label='Acc Z', color = 'b')
	plt_acc_z.set_xlabel('acc z')

	# plot acc x, y, z
	plt_acc_xyz.cla()
	plt_acc_xyz.set_ylim(-acc_plt_ylimit,acc_plt_ylimit)
	# plt_acc_xyz.scatter(len(temp_data[:,0]-1, temp_data[-1:]))
	plt_acc_xyz.plot(temp_data[:,0], label='Acc X', color = 'r')
	plt_acc_xyz.plot(temp_data[:,1], label='Acc Y', color = 'g')
	plt_acc_xyz.plot(temp_data[:,2], label='Acc Z', color = 'b')
	plt_acc_xyz.set_xlabel('acc x, y, z')


	gyro_plt_ylimit = 500
	# plot gyro x
	plt_gyro_x.cla()
	plt_gyro_x.set_ylim(-gyro_plt_ylimit,gyro_plt_ylimit)
	plt_gyro_x.plot(temp_data[:,3], label='Gyro X', color = 'r')
	plt_gyro_x.set_xlabel('gyro x')

	# plot gyro y
	plt_gyro_y.cla()
	plt_gyro_y.set_ylim(-gyro_plt_ylimit,gyro_plt_ylimit)
	plt_gyro_y.plot(temp_data[:,4], label='Gyro Y', color = 'g')
	plt_gyro_y.set_xlabel('gyro y')

	# plot gyro z
	plt_gyro_z.cla()
	plt_gyro_z.set_ylim(-gyro_plt_ylimit,gyro_plt_ylimit)
	plt_gyro_z.plot(temp_data[:,5], label='Gyro Z', color = 'b')
	plt_gyro_z.set_xlabel('gyro z')

	# plot gyro x, y, z
	plt_gyro_xyz.cla()
	plt_gyro_xyz.set_ylim(-gyro_plt_ylimit,gyro_plt_ylimit)
	plt_gyro_xyz.plot(temp_data[:,3], label='Gyro X', color = 'r')
	plt_gyro_xyz.plot(temp_data[:,4], label='Gyro Y', color = 'g')
	plt_gyro_xyz.plot(temp_data[:,5], label='Gyro Z', color = 'b')
	plt_gyro_xyz.set_xlabel('gyro x, y, z')



ani = FuncAnimation(fig, plot_data, interval = 0.01)


plt.show()


subscriber.loop_stop()