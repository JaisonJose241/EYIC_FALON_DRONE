#!/usr/bin/env python

'''
Project Name:      FALON drone - stranded person detection using UAV.
Author List: 	   Jaison Jose, Akshay Wararkar
Filename: 		   state.py
Functions: 		   check_kill(program_name), main()
Global Variables:  UDP_IP, UDP_PORT, sock
'''

from __future__ import print_function
from dronekit import connect, VehicleMode
import time
import argparse 
import socket, os, signal


'''
Function Name: 	check_kill
Input: 		    the program name to be killed
Output: 	    None
Logic: 		    the function checks the pid of the program given then uses the pid to kill
                the program using os.kill()
Example Call:	check_kill("hello.py")
'''

def check_kill(pstring):

    # Check the program name on os.popen()
    for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):

        # split the line by using .split() for string of the list
        fields = line.split()

        # take the pid present in the first element of the list
        pid = fields[0]

        # kill the pid value 
        os.kill(int(pid), signal.SIGKILL)

# Give 3 seconds delay for starting the socket
print("3sec for takeoff")
time.sleep(3)

# Intialising UDP IP and PORT at 127.0.0.1:5008
UDP_IP = "127.0.0.1"
UDP_PORT = 5008

# Connecting socket with internal network and intializing sock object
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

# Bind the socket for listening on 127.0.0.1:5008                     
sock.bind((UDP_IP, UDP_PORT))

# Initialising the parser for getting the PORT of mavproxy
parser = argparse.ArgumentParser(description='Print out vehicle state information. Connects to SITL on local PC by default.')
parser.add_argument('--connect', 
                   help="vehicle connection target string. If not specified, SITL automatically started and used.")

# Storing the parsed arg after --connect                   
args = parser.parse_args()

# Storing the IP:port from mavproxy server
connection_string = args.connect

# Initialising object for "connect" an instance of dronekit in order to read/write drone parameter
print("\nConnecting to vehicle on: %s" % connection_string)
vehicle = connect(connection_string)

# the loop checks "TRUE" in the received message from the socket as this socket is dedicated
# for telemetry topic RTL
while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print("received message: %s" % data)
    print(data)
    
    # Loops until the data received is "TRUE"
    if data == "TRUE":
       break

# Aggressive change of drone flight mode as RTL
vehicle.mode = VehicleMode("RTL")
while vehicle.mode.name=="RTL":
     vehicle.mode = VehicleMode("RTL")
     time.sleep(0.3)  

# kills the following programs      
check_kill('basic_mission.py')
check_kill('state.py')
check_kill('mydetection.py')     

