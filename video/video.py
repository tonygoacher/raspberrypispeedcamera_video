#!/usr/bin/python
# -*- coding: utf-8 -*-

import serial
import os
import datetime
import shutil
import time

from enum import Enum
from picamera import PiCamera

print ('Camera init')
camera = PiCamera()
camera.resolution = (1280, 1024)
time.sleep(2)
print ('Camera init done')
recording = False
ser = serial.Serial('/dev/ttyS0', 115200, timeout=0.1)
rxIndex = 0
commandBuffer = bytearray(270)


print ('Using serial port ' + ser.name)

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
        if CommsResult(commandBuffer[2]) == CommsResult.END_RECORDING:

            # Just return

            print ('COMMAND: END RECORDING')
            return CommsResult.END_RECORDING

        if CommsResult(commandBuffer[2]) == CommsResult.START_RECORDING:
            print ('COMMAND: START RECORDING')
            return CommsResult.START_RECORDING

        if CommsResult(commandBuffer[2]) == CommsResult.SAVE_VIDEO:
        
            # Packet format = <hdr><len><command><data>....<data_n><checksum>
            global saveFilename
            saveFilename=''
            dataLen = commandBuffer[1] - 1 # Subtract 1 as first byte of data is the command
            for cpos in range(3, 3 + dataLen):
                saveFilename += chr(commandBuffer[cpos])
            print('Save file name is ' + saveFilename)
            return CommsResult.SAVE_VIDEO
    except:
        print ('Parse failed')
        return CommsResult.TIMEOUT


def ReadCommand(timeoutValue):
    timeout = timeoutValue * 10  # Delay is in 0.1s steps
    state = RxState.GET_HEADER
    checksum = 0
    expectedLength = 0

    while timeout != 0:
        x = ser.read()
        if len(x):
            for bValue in x:
                bValue = ord(bValue)
                print('State :' + str(state))
                print(bValue)

                if state == RxState.GET_HEADER:
                    rxIndex = 0
                    if bValue == 1:  # SOH is header start
                        commandBuffer[rxIndex] = bValue
                        rxIndex += 1
                        state = RxState.GET_LENGTH

                        print('Got header')

                        checksum = bValue  # Reset checksum
                        continue

                if state == RxState.GET_LENGTH:
                    commandBuffer[rxIndex] = bValue
                    rxIndex += 1
                    expectedLength = bValue  # This is command + data
                    print('Expected length is ' + str(expectedLength))

                    print('Got length ' + str(bValue))

                    state = RxState.GET_DATA
                    checksum += bValue
                    continue

                if state == RxState.GET_DATA:
                    commandBuffer[rxIndex] = bValue

                    # print('Placing data {:02X} into buffer at index {:02X}'.format(bValue,rxIndex))

                    rxIndex += 1
                    expectedLength -= 1
                    checksum += bValue
                    if expectedLength == 0:
                        state = RxState.GET_CHECKSUM
                    continue

                if state == RxState.GET_CHECKSUM:
                    checksum &= 0xff
                    if bValue == checksum:

                        print('Packet OK')


                        result = ParsePacket()
                        return result
                    else:
                        print ('Invalid checksum. Expected {:02x} Calculated {:02x}'.format(bValue,
                                checksum))
                        print([hex(no) for no in commandBuffer])
                        state = RxState.GET_HEADER
        timeout -= 1
    print ('Timed out ' + str(timeout))
    return CommsResult.TIMEOUT


class CameraState(Enum):

    IDLE = 1
    RECORDING = 2


cameraState = CameraState.IDLE
fileTempPath = '/mnt/ramdisk/tmp.h264'
fileFinalPath = '/home/pi/speedVideo/'


def deleteVideo(fileToRemove):
    try:
        os.remove(fileToRemove)
    except:
        print ('Failed to remove ', fileToRemove)



while True:

    result = CommsResult.TIMEOUT
    if cameraState == CameraState.IDLE:
        result = ReadCommand(1000)
        if result == CommsResult.START_RECORDING and recording == False:

            cameraState = CameraState.RECORDING
            print (fileTempPath)
            camera.start_recording(fileTempPath)
            recording = True

    if cameraState == CameraState.RECORDING:
        result = ReadCommand(10)  # Max time is 10 seconds
        print ('Got ', result)

        if result == CommsResult.TIMEOUT:
            camera.stop_recording()
            recording = False
            print ('Timed out awaiting recording result')
            deleteVideo(fileTempPath)

        if result == CommsResult.END_RECORDING:
            camera.stop_recording()
            recording = False
            print ('End recording command')
            deleteVideo(fileTempPath)

        if result == CommsResult.SAVE_VIDEO:
            print ('Keep video command' + saveFilename)
            
            time.sleep(3)  # This many seconds onto the end of the video
            camera.stop_recording()
            recording = False
            shutil.move(fileTempPath, fileFinalPath + saveFilename + '.h264')

        cameraState = CameraState.IDLE

