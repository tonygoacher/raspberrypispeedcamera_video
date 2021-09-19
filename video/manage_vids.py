import glob
import os
import time


maxFiles = 100

dir_name = '/home/pi/speedVideo/'
# Get list of all files only in the given directory
list_of_files = filter( os.path.isfile,
                        glob.glob(dir_name + '*.h264') )
# Sort list of files based on last modification time in ascending order
list_of_files = sorted( list_of_files,
                        key = os.path.getmtime)
# Iterate over sorted list of files and print file path 
# along with last modification time of file 

if(len(list_of_files) > maxFiles):
	for x in range(0, len(list_of_files) - maxFiles):
		os.remove(list_of_files[x])

