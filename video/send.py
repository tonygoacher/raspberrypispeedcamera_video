import serial
import time

ser = serial.Serial('/dev/ttyUSB0',115200)
for x in range(5000):
	data = [1,1,2,4]
	ser.write(data)
	time.sleep(6)
	data=[1,3,4,0x30, 0x31,0x69]
	ser.write(data)
ser.close()
