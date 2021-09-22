#!/bin/sh
echo "Running " > /home/pi/tg.log
sleep 10
echo "Sleep over  " >> /home/pi/tg.log
cd /home/pi/rpi_speed_video_camera/speed/
/home/pi/rpi_speed_video_camera/speed/carspeed.py & >> /home/pi/tg.log

