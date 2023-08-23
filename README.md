# IMU
- Calibration for IMU Sensor
- IMU Fusion Algorithms
- IMU Sensor type: Arduino NANO 33 IoT, XSENS DOT
- Study at KAIST NMAIL

## mqtt_plotting
Collect data from Arduino NANO 33 IoT and transfer data by using mqtt communication.
Apply a filter implemented un python to calibrate IMU data.
Used filters: Complementary Filter, Madgwick Filter, Kalman Filter

## XSENS_NANO_plotting
Attatch XSENS DOT and Arduino NANO 33 IoT to compare two Arduino NANO 33 IoT datas from different quality of IMU sensor.

## Data Description
=========================================================
Data 1: 
    arduino_file: serial_data_230720_1.csv
    xsens_raw_file: 15_20230720_151055_577.csv

Data 2:
    arduino_file: serial_data_230720_2.csv
    xsens_raw_file: 15_20230720_161025_154.csv

Data 3:
    arduino_file: serial_data_230721_1.csv
    xsens_raw_file: 15_20230721_134758_096.csv


Data 3:
    arduino_file: serial_data_230721_2.csv
    xsens_raw_file: 15_20230721_152126_091.csv

    xsens 20 Hz, 
    Parameters = 0, 19


=========================================================
* Arduino Serial takes 3 ms more to send data 
* xsens
  60 Hz: 16.667 ms
  20 Hz: 50.001 ms
