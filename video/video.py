#!/usr/bin/python3
import serial
import os
import datetime
import shutil
import time

from enum import Enum
from picamera import PiCamera

ser = serial.Serial('/dev/ttyS0',115200, timeout=0.1)
rxIndex = 0
commandBuffer = bytearray(40)
speed = '00'

print(ser.name)


class RxState(Enum):
	GET_HEADER = 1
	GET_LENGTH = 2
	GET_DATA = 3
	GET_CHECKSUM = 4

class CommsResult(Enum):
	TIMEOUT = 1
	START_RECORDING = 2
	END_RECORDING = 3
	SAVE_VIDEO = 4

def ParsePacket():
	try:
		if(CommsResult(commandBuffer[2]) == CommsResult.END_RECORDING):
			# Just return
			print('COMMAND: END RECORDING')
			return CommsResult.END_RECORDING
		
		if(CommsResult(commandBuffer[2]) == CommsResult.START_RECORDING):
			print('COMMAND: START RECORDING')
			return CommsResult.START_RECORDING

		if(CommsResult(commandBuffer[2]) == CommsResult.SAVE_VIDEO):
			speed = ''
			speed += chr(commandBuffer[3])
			speed += chr(commandBuffer[4])
			return CommsResult.SAVE_VIDEO
	except:
		print('Parse failed')
		return CommsResult.TIMEOUT
		
	

def ReadCommand(timeoutValue):
	timeout = timeoutValue * 10	# Delay is in 0.1s steps
	state = RxState.GET_HEADER
	checksum = 0
	expectedLength = 0;

	while timeout != 0:
		x =ser.read()
		if(len(x)):
			for bValue in x:
				#print('Got data {:02X} State'.format(bValue), state)
			
				if(state == RxState.GET_HEADER):
					rxIndex =0
					if(bValue == 1):	# SOH is header start
						commandBuffer[rxIndex] = bValue
						rxIndex += 1
						state = RxState.GET_LENGTH
						#print('Got header')
						checksum = bValue	# Reset checksum
						continue

				if(state == RxState.GET_LENGTH):
					commandBuffer[rxIndex] = bValue
					rxIndex += 1
					expectedLength = bValue	# This is command + data
					#print('Got length {:02X}'.format(bValue))
					state = RxState.GET_DATA
					checksum += bValue
					continue

				if(state == RxState.GET_DATA):
					commandBuffer[rxIndex] = bValue
					#print('Placing data {:02X} into buffer at index {:02X}'.format(bValue,rxIndex))
					rxIndex += 1
					expectedLength -= 1
					checksum += bValue
					if(expectedLength == 0):
						state = RxState.GET_CHECKSUM
					continue

				if(state == RxState.GET_CHECKSUM):
					if(bValue == checksum):
						#print('Packet OK')
						print(commandBuffer.hex())
						
						return ParsePacket()
					else:
						print('Invalid checksum. Expected {:02x} Calculated {:02x}'.format(bValue, checksum))
						print(commandBuffer.hex())
						state = RxState.GET_HEADER
		timeout -= 1
	print('Timed out')
	return CommsResult.TIMEOUT

					
					
class CameraState(Enum):
	IDLE = 1
	RECORDING = 2
	
cameraState = CameraState.IDLE	
filename=''
fileTempPath='/mnt/ramdisk/'
fileFinalPath='/home/pi/speedVideo/'

def deleteVideo(fileToRemove):
	try:
		os.remove(fileToRemove)
	except:
		print('Failed to remove ',fileToRemove)

	
	
print('Camera init');
camera = PiCamera()
camera.resolution=(1280,1024)
time.sleep(2)
print('Camera init done')	
while True:


	result = CommsResult.TIMEOUT
	if(cameraState == CameraState.IDLE):
		result = ReadCommand(100)
		if(result == CommsResult.START_RECORDING):
			
			cameraState = CameraState.RECORDING
			timeNow = datetime.datetime.now()
			filename = timeNow.strftime("%y_%m_%d_%H_%M_%S.h264")
			print(fileTempPath+filename)
			camera.start_recording(fileTempPath+filename)


			
	if(cameraState == CameraState.RECORDING):
		result = ReadCommand(5)		# Max time is 5 seconds
		print('Got ', result)
		camera.stop_recording()
		if(result == CommsResult.TIMEOUT):
			print('Timed out awaiting recording result')
			deleteVideo(fileTempPath+filename)

		if(result == CommsResult.END_RECORDING):
			print('End recording command rexd')
			deleteVideo(fileTempPath+filename)

		if(result == CommsResult.SAVE_VIDEO):
			print('Keep video command')
			print(speed)
			shutil.move(fileTempPath+ filename, fileFinalPath+filename+"_Speed"+speed+".h264")
			
		cameraState = CameraState.IDLE
 
		
	
					
	
					

			
			

		
	
