import paho.mqtt.client as mqtt


username = "nmail"
password = "74269"

# def on_connect(client, userdata, flags, rc):
# 	'''
#     Runs when client is connected to broker
#     '''
# 	print("Connected with result code "+str(rc))

def on_connect(client, userdata, flags, rc):
	'''
    Runs when client is connected to broker
    '''
	if rc==0:
		print("connected OK")
	else:
		print("Bad connection Returned code=",rc)

def on_publish(client, userdata, mid):
    print("In on_pub callback mid= ", mid)

publisher = mqtt.Client()
publisher.on_connect = on_connect
publisher.on_publish = on_publish

# publisher.connect("mqtt.pumpkinhouse.io")
publisher.username_pw_set(username, password)
publisher.connect("143.248.143.21")
publisher.loop_start()
publisher.publish("nmail/",'Hello world')
publisher.loop_stop()

