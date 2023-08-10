# mqtt plotting
Read Serior data by using Arduino.ino and transfer the data by using MQTT communication to handle it with python.

## Method
1. MQTT
   MQTT is a standards-based messaging protocol, or set of rules, used for machine-to-machine communication. Smart sensors, wearables, and other Internet of Things (IoT) devices typically have to transmit and receive data over a resource-constrained network with limited bandwidth. These IoT devices use MQTT for data transmission, as it is easy to implement and can communicate IoT data efficiently. MQTT supports messaging between devices to the cloud and the cloud to the device.
2. Read Serial data from Arduino NANO 33 IoT
3. Transfer by using MQTT communication
4. Read each data in real time and apply filters(Complementary, Madgwick Filter, Kalman Filter)
5. Plot each data in real time 

## Used Filters
- Complementary Filter
- Madgwick Filter
- Kalman Filter

## Result
1. Complementary Filter
   ![image](https://github.com/jehyunglee612/IMU/assets/96870521/a4e6880b-f114-4f92-a40f-fae9aaab0168)

2. Madgwick Filter
   ![image](https://github.com/jehyunglee612/IMU/assets/96870521/90a26795-dde1-4830-89fa-f27fe85122bd)

3. Kalman Filter
   ![image](https://github.com/jehyunglee612/IMU/assets/96870521/502294fd-d5e9-46ab-852d-905a9f6fb665)
