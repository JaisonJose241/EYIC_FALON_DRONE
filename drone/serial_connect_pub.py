#!/usr/bin/env python
'''
Project Name:      FALON drone - stranded person detection using UAV.
Author List: 	   Sahil Dandekar, Jaison Jose, Akshay Wararkar
Filename: 		   serial_connect_pub.py
Functions: 		   take_off_callback(topic, data, opts), Mode_callback(topic, data, opts), 
                   Waypoints_callback(topic, data, opts), RTL_callback(topic, data, opts), main() 
Global Variables:  (UDP_IP, UDP_PORT, sock  :  for every port), flag
'''

from pytelemetry import Pytelemetry
from pytelemetry.transports.serialtransport import *
import time
import logging
from logging import getLogger
from logging import FileHandler
import datetime
import socket

# Variable flag: for marking the takeoff command execution so that RTL gets executed
flag = 0

# Wait for 3 seconds
print("wait for 3 sec")
time.sleep(3)


'''
# PORT socket for "basic_mission.py" for "MODE" : sending and receiving data
# Intialising UDP IP and PORT at 127.0.0.1:5007
'''
UDP_IP = "127.0.0.1"
UDP_PORT = 5007
# Connecting socket with internal network and intializing sock object
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))
# wait for a sec to intisalize next UDP        
print("wait for 1 sec")
time.sleep(1)


'''
# PORT socket for "state.py"
# Intialising UDP IP and PORT at 127.0.0.1:5006
'''
UDP_IP2 = "127.0.0.1"
UDP_PORT2 = 5006

# Connecting socket with internal network and intializing sock object
sock2 = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock2.bind((UDP_IP2, UDP_PORT2))
# wait for a sec to intisalize next UDP 
print("wait for 1 sec")
time.sleep(1)


'''
# PORT socket for "rtl.py"
# Intialising UDP IP and PORT at 127.0.0.1:5008
'''
UDP_IP3 = "127.0.0.1"
UDP_PORT3 = 5008
# Connecting socket with internal network and intializing sock object
sock3 = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
# wait for a sec to intisalize next UDP 
print("wait for 1 sec")
time.sleep(1)


'''
# PORT socket for "mydetection.py"
# Intialising UDP IP and PORT at 127.0.0.1:5005
'''
UDP_IP4 = "127.0.0.1"
UDP_PORT4 = 5005
# Connecting socket with internal network and intializing sock object
sock4 = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock4.bind((UDP_IP4, UDP_PORT4))
# wait for a sec to intisalize next UDP 
print("wait for 1 sec")
time.sleep(1)


'''
# PORT socket for "basic_mission.py" for "TAKEOFF" : sending data
# Intialising UDP IP and PORT at 127.0.0.1:5009
'''
UDP_IP5 = "127.0.0.1"
UDP_PORT5 = 5009
# Connecting socket with internal network and intializing sock object
sock5 = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
# wait for a sec to intisalize next UDP 
print("wait for 1 sec")
time.sleep(1)


'''
# PORT socket for "basic_mission.py" for "WAYPOINTS" : seding and receiving data
# Intialising UDP IP and PORT at 127.0.0.1:50010
'''
UDP_IP6 = "127.0.0.1"
UDP_PORT6 = 5010
# Connecting socket with internal network and intializing sock object
sock6 = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock6.bind((UDP_IP6, UDP_PORT6))


'''
Function Name: 	take_off_callback
Input: 		    topic: the name of topic
                data : the data to be transmitted over the specified socket
                opts : "NOT USED" 
Output: 	    None
Logic: 		    sets the takeoff flag = 1, sends the "TRUE" command 
                to the basic_mission.py file for TAKEOFF
Example Call:	take_off_callback - by pytelemtry object's second parameter while subscribing
'''
def take_off_callback(topic, data, opts):
    global flag
    print(topic," : ", data)
    sock5.sendto(bytes(data, 'utf-8'), (UDP_IP5, UDP_PORT5))
    flag = 1


'''
Function Name: 	RTL_callback
Input: 		    topic: the name of topic
                data : the data to be transmitted over the specified socket
                opts : "NOT USED" 
Output: 	    None
Logic: 		    checks the takeoff flag, if 1 then sends the "TRUE" command 
                to the rtl.py file for RTL - Return To Launch
Example Call:	RTL_callback - by pytelemtry object's second parameter while subscribing
'''
def RTL_callback(topic, data, opts):
    global flag
    print(topic," : ", data)
    print("flag:", flag)
    if flag == 1:
        
        # if the flag is 1 then the RTL command is send over socket to rtl.py
        sock3.sendto(bytes(data, 'utf-8'), (UDP_IP3, UDP_PORT3))
        print("RTL")


'''
Function Name: 	Mode_callback
Input: 		    topic: the name of topic
                data : the data to be transmitted over the specified socket
                opts : "NOT USED" 
Output: 	    None
Logic: 		    sends the mode over specified socket to the basic_mission.py file
Example Call:	Mode_callback - by pytelemtry object's second parameter while subscribing
'''    
def Mode_callback(topic, data, opts):
    print(topic," : ", data)
    sock.sendto(bytes(data, 'utf-8'), (UDP_IP, UDP_PORT))

'''
Function Name: 	Waypoints_callback
Input: 		    topic: the name of topic
                data : the data to be transmitted over the specified socket
                opts : "NOT USED" 
Output: 	    None
Logic: 		    sends the mode over specified socket to the basic_mission.py file
Example Call:	Mode_callback - by pytelemtry object's second parameter while subscribing
'''    
def Waypoints_callback(topic, data, opts):
    print(topic," : ", data)
    sock6.sendto(bytes(data, 'utf-8'), (UDP_IP6, UDP_PORT6))


'''
Function Name: 	main
Input: 		    None
Output: 	    None 
Logic: 		    Makes an object for pyTelemetry, subscribes and publishes topic over telemetry
                sends those received data over the callback function to particular sockets
                also checks for receiving data from sockets and publishes topic over telemetry.
Example Call:	main()
'''
def main():

    # object for SerialTransport for serial communication
    transport = SerialTransport()

    # object for Pytelemetry to publish and subscribe data over telemetry
    c = Pytelemetry(transport)

    # variable options: A dictionary for port and baudrate of telemetry
    options = dict()
    options['port'] = "/dev/ttyUSB0"
    options['baudrate'] = 57600
    
    # setting the parameter for serial communication of telemtry
    transport.connect(options)

    # Subscribing the listed topics with respective callback functions
    c.subscribe('TAKE_OFF', take_off_callback)
    c.subscribe('RTL', RTL_callback)
    c.subscribe('MODE', Mode_callback)
    c.subscribe('WAYPOINTS', Waypoints_callback)

    # Declaring a check varible for checking the accuracy of the data received
    bad_frame = bytearray(b'0700736f6d65746f70696300626f6f7961613ecc')

    # Sending the bad_frame constant to the decode_fame parametr of Pytelemetry
    c.api._decode_frame(bad_frame)


    '''
    # Loop for the MODE: send the subscribed data over the socket via callback function
    # also waits for any reply of received = TRUE over the same socket and again publishes
    # over the "MODE_RECEIVED" topic by telemetry
    '''
    while True:

        # Updates on every call the subscriber list
        c.update()
        
        # waits for the receive data from the socket
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        words = data.split(':')
        print(words)

        # After splitting data checks for the word "RECEIVED"
        if words[0] == "RECEIVED":
            print(words)
            
            if words[1] == "TRUE":
                # If TRUE then publishes "TRUE" over telemetry on the topic "MODE_RECEIVED"
                c.publish('MODE_RECEIVED',"TRUE",'string')

            else:
                # else it publishes "FALSE" over telemetry on the topic "MODE_RECEIVED"
                c.publish('MODE_RECEIVED',"FALSE",'string')


    '''
    # Loop for the WAYPOINTS: send the subscribed data over the socket via callback function
    # also waits for any reply of received = TRUE over the same socket and again publishes
    # over the "WAYPOINTS_RECEIVED" topic by telemetry
    '''
    while True:

        # Updates on every call the subscriber list
        c.update()       

        # waits for the receive data from the socket 
        data6, addr6 = sock6.recvfrom(1024) # buffer size is 1024 bytes
        words = data6.split(':')
        print(words)

        # After splitting data checks for the word "RECEIVED"
        if words[0] == "RECEIVED":
            print(words)

            if words[1] == "TRUE":
                # If TRUE then publishes "TRUE" over telemetry on the topic "MODE_RECEIVED"
                c.publish('WAYPOINTS_RECEIVED',"TRUE",'string')
            else:
                # else it publishes "FALSE" over telemetry on the topic "MODE_RECEIVED"
                c.publish('WAYPOINTS_RECEIVED',"FALSE",'string')
       

    '''
    # Loop for the GPS data on sock2 and person detected data on sock4
    # also publishes those received data over the topic:
    # DETECTION: for person detection
    # DATA     : for current GPS LOCATION 
    '''
    while True:

        # waits for the receive data from the socket
        data2, addr2 = sock2.recvfrom(1024) # buffer size is 1024 bytes
        data2 = data2.decode(encoding='utf-8')

        # waits for the receive data from the socket
        data4, addr4 = sock4.recvfrom(1024) # buffer size is 1024 bytes
        words = data4.split(':')
        print(words)

        # After splitting data checks for the word "Person detected"
        if words[0] == "Person detected":
            print(words)

            if words[1] == " TRUE":
                print(words[1])

                # If second word is " TRUE" then make the MESSAGE varible as "True"
                MESSAGE = "True"
                
            else :
                print("somethings wrong")

                # else it assigns the MESSAGE variable as "False"
                MESSAGE = "False"

        # Publishing the message of person detection over "DETECTION" topic by telemetry        
        c.publish('DETECTION',MESSAGE,'string')

        # Publishing the message of person detection over "DATA" topic by telemetry
        c.publish('DATA',data2,'string')

        # Updates on every call the subscriber list and publishing part
        c.update()

    # closing the serial communication instance -> "transport"
    transport.disconnect()

if __name__ == "__main__":
    main()
