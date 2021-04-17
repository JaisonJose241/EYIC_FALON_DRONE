#!/usr/bin/env python

'''
Project Name:      FALON drone - stranded person detection using UAV.
Author List: 	   Sarang Chouguley, Akshay Wararkar, Jaison Jose, Sahil Dandekar
Filename: 		   launch.py
Functions: 		   None
Global Variables:  None
'''
# Importing os for executiong terminal commands
# Importing time for generating delay
import os, time

# Generating 10 seconds delay for Jetson Nano to boot and stabilize the peripherals
time.sleep(10)

# OS command
# Giving permission to access the wired communication of PixHawk flight controller on "/dev/ttyTHS1"
# Starting State.py launch file with 14550 port no. for mavproxy connection
# Starting rtl.py launch file exclusively for emergency return to launch function with 14551 port no. for mavproxy connection
# Starting basic_mission.py launch file with 14552 port no. for mavproxy connection to start the mission 
# Starting serial_connect_pub.py for connecting all files by socket to the telemetry and thereby transfering commands
# Starting mydetection.py for person detection using pi CAM
# Starting mavproxy.py server and its ports for communicating with drone by telemetry 2
os.system("sudo chmod 777 /dev/ttyTHS1 & python /home/eyic/Documents/eyicDrone/drone_start/state.py --connect 127.0.0.1:14550 & python /home/eyic/Documents/eyicDrone/drone_start/rtl.py --connect 127.0.0.1:14551 & python /home/eyic/Documents/eyicDrone/drone_start/basic_mission.py --connect 127.0.0.1:14552 & python3 /home/eyic/Downloads/serial_connect_pub.py & python3 /home/eyic/Documents/eyicDrone/humanDetection/mydetection.py & python3 /home/eyic/.local/bin/mavproxy.py --daemon --master=/dev/ttyTHS1 --out 127.0.0.1:14550 --out 127.0.0.1:14551 --out 127.0.0.1:14552")
