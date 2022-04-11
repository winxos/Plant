#! /bin/bash
. /etc/profile
sleep 5
python /home/pi/plant/plant.py>>/home/pi/log.txt>&1

