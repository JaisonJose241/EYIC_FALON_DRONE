#!/usr/bin/env python

'''
Project Name:      FALON drone - stranded person detection using UAV.
Author List: 	   Sarang Chouguley, Sahil Dandekar
Filename: 		   mydetection.py
Functions: 		   calculateDistance(actualHeight, detectedHeight), main()
Global Variables:  UDP_IP, UDP_PORT, sock
'''

import jetson.inference
import jetson.utils
import numpy as np
import time
import random
import datetime
import socket

# wating for 2 seconds for starting the UDP port
print("2sec fr detect")
time.sleep(2)

# Intialising UDP IP and PORT at 127.0.0.1:5005
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# Connecting socket with internal network and intializing sock object
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP


'''
Function Name: 	calculateDistance
Input: 		    actualHeight   -> the approximate human height eg. 64.8 in inches
                detectedHeight -> height detcted by the detection model from bounding box.
Output: 		Approximate distance between the person detected and drone in meters.
Logic: 		    takes the height and uses the focal length, using the formula calculates the distance
Example Call:	calculateDistance(64.8, 10)
'''

def calculateDistance(actualHeight, detectedHeight):
    focalL = 1168.2852930943877
    inches = actualHeight * focalL / detectedHeight
    meter = inches / 39.37
    return meter


'''
Function Name: 	main
Input: 		    None
Output: 	    Displays the video, sends person detected message with distance 
                and side(which side on screen: left, middle, right) of person on the socket.
Logic: 		    Uses Jetson library for object detection and looks for person, if person detected the bounding
                box appears on screen and the distance between the camera and person with angle is sent to the
                remote response team and the basic_mission.py file by socket.
Example Call:	main()
'''

def main():

    global UDP_IP, UDP_PORT, sock
    # initialise mobileNet for human detection
    net = jetson.inference.detectNet("ssd-mobilenet-v2",threshold=0.6)

    # initialise camera
    # camera = jetson.utils.videoSource("csi://0")
    camera = jetson.utils.gstCamera(640,480,"0")

    # initialise file name
    name = "outputVideo" + str(int(random.random()*100)) + ".avi"
    
    # Saving video
    f = jetson.utils.videoOutput(name)
    
    while True:
        # capture image
        img= camera.Capture()

        # run detection
        detections = net.Detect(img)

        #save video
        f.Render(img)
        
        # Checking for any detection
        for d in detections:

            # Checking for person detection as for human the: id = 1
            if d.ClassID == 1:

                # Variable MESSAGE: The message for transmission to be converted to bytes and in format of "what: TRUE/FALSE"
                MESSAGE = b"Person detected: TRUE"

                # Sending the message on UDP - 127.0.0.1:5005 to serial_connect_pub.py then to telemetry
                sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

                # Varible distance: Storing the approx. distance between camera and person detected
                distance = calculateDistance(64.8, d.Height)

                # Printing distance, and both height
                print(f"Distance : {distance} meters")
                print(f"Actual Height : 5 foot")
                print(f"Detected height : {d.Height} pixels")

                # Converting distance to distance message for socket
                distance = "Distance:"+str(distance)
                
                # Checking for the person presence on which side of the screen so as to change thw YAW of drone
                # here 640 is the screen width
                # 0  -> Center/Middle and high priority if multiple person is present
                # -1 -> Left side
                # 1  -> Right side
                if((d.Right - d.Left)/2 > 640/3) and ((d.Right - d.Left)/2 < (640 - 640/3)):
                    side = 0
                elif((d.Right - d.Left)/2 < 640/3):
                    side = -1
                elif((d.Right - d.Left)/2 < (640 - 640/3)):
                    side = 1    

                # Variable angle: prepares message format for socket to send the angle value (-1, 0, 1) 
                angle = "Angle:"+str(side)

                # Sending the distance and angle data over scket via UDP to basic_mission.py
                sock.sendto(bytes(distance, 'utf-8'), (UDP_IP, UDP_PORT))
                sock.sendto(bytes(angle, 'utf-8'), (UDP_IP, UDP_PORT))

                # Print "Done." for confirmation on terminal
                print("Done.")
            
        # If no person detected
        # Variable MESSAGE: formarting message for person detection
        MESSAGE = b"Person detected: FALSE"

        # Sending above data MESSAGE over socket through the serial_connect_pub.py to the telemetry
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

        # Printing "..."for confirmation on terminal
        print("...")
        
if __name__ == "__main__":
    main()

    


  


