#!/usr/bin/python3

import glob
import os
import shutil
import sys

def get_disk_percentage():
    path = "/home/pi"
  
    # Get the disk usage statistics
    # about the given path
    stat = shutil.disk_usage(path)

    percentage = (stat.used / stat.total) * 100
    return int(percentage)

maxFiles = 100

if len(sys.argv) < 3:
    print('Usage: manage_vids.py <path> <filter>')
    quit()
else:
    dir_name = sys.argv[1]
    file_filter = sys.argv[2]

#dir_name = '/home/pi/speedVideo/'
#file_filter = '*.h264'
    
print('Trimming path ' + dir_name + file_filter)

# Get list of all files only in the given directory
list_of_files = filter( os.path.isfile,
                        glob.glob(dir_name + file_filter) )
# Sort list of files based on last modification time in ascending order
list_of_files = sorted( list_of_files,
                        key = os.path.getmtime)

		
while get_disk_percentage() >= 80 and len(list_of_files):
    os.remove(list_of_files[0])
    del list_of_files[0]
    
		


