import serial
import time
from datetime import datetime


ser = serial.Serial('/dev/ttyUSB0',115200)
for x in range(5000):
	data = [1,1,2,4]
	ser.write(data)
	time.sleep(6)
	data = [1,3,4]
	now = datetime.now()
	filename = now.strftime("%H:%M:%S")
	data += list(map(ord ,filename))

	data[1] = len(filename)+1 # Add one as command is counted in data length
	checksum = 0
	checksum = sum(bytearray(data))

	data.append(checksum & 0xff)
	print ([hex(no) for no in data])
	ser.write(data)
ser.close()
