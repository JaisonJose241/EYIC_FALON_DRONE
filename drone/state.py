#!/usr/bin/env python

'''
Project Name:      FALON drone - stranded person detection using UAV.
Author List: 	   Akshay Wararkar, Jaison Jose
Filename: 		   state.py
Functions: 		   main()
Global Variables:  UDP_IP, UDP_PORT, sock
'''

from __future__ import print_function
from dronekit import connect, VehicleMode
import time
import argparse 
import socket

# Generating a delay of 3 seconds for UDP socket
print("3sec for state")
time.sleep(3)

# Intializing variables UDP IP and PORT a 127.0.0.1:5006
UDP_IP = "127.0.0.1"
UDP_PORT = 5006

# Connecting socket to the internal network
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP


# Initialising the parser for getting the PORT of mavproxy
parser = argparse.ArgumentParser(description='Print out vehicle state information. Connects to SITL on local PC by default.')
parser.add_argument('--connect', 
                help="vehicle connection target string. If not specified, SITL automatically started and used.")

# Storing the parsed arg after --connect                
args = parser.parse_args()

# Storing the IP:port from mavproxy server
connection_string = args.connect
print("\nConnecting to vehicle on: %s" % connection_string)

# Initialising object for "connect" an instance of dronekit in order to read/write drone parameter
vehicle = connect(connection_string)
print("connected")

while True:

    # Sending the GPS data once in 10 times of loop i.e. once in 2 seconds
    for i in range(0, 10):
        if i == 1:
            frame = vehicle.location.global_relative_frame
        else:
            frame = "."    
        time.sleep(0.2)
    print(frame)

    # Sending the frame data over the socket for telemetry transmission after a message is prepared
    MESSAGE = bytes(str(frame).encode('utf-8'))
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
  