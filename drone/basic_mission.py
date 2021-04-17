#!/usr/bin/env python
'''
Project Name:      FALON drone - stranded person detection using UAV.
Author List: 	   Jaison Jose, Akshay Wararkar
Filename: 		   basic_mission.py
Functions: 		   get_distance_metres(aLocation1, aLocation2), distance_to_current_waypoint(), add_mission(),
                   arm_and_takeoff(aTargetAltitude)
Global Variables:  (UDP_IP, UDP_PORT, sock  :  for every port), mode, person_detected_waypoint, waypoint_no, waypoint_list, no_of_waypoint
'''

from __future__ import print_function
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
import time
import math
from pymavlink import mavutil
import socket
from playsound import playsound
import argparse  

# Variable mode: 1 :drone person detction and move on
#                2 :drone detects person; stops; hovers down and detects his/her pose 
mode = 0

# Variable person_detected_waypoint: On which waypoint the person was detected
person_detected_waypoint = 0

# Variable waypoint_no: Current waypoint no
waypoint_no = 0

# Variable waypoint_list: lsit of all the waypoints the drone has to transverse
waypoint_list = []

# Variable no_of_waypoint: total no of waypoints
no_of_waypoint = 0

# Generating delay of 3 sec for initializing the UDPs
print("3sec for takeoff")
time.sleep(3)


'''
# PORT socket for "serial_connect_pub.py" for "MODE" : sending and receiving data
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
# PORT socket for "mydetection.py" for angle and distance of person detected
# Intialising UDP IP and PORT at 127.0.0.1:5005
'''
UDP_IP2 = "127.0.0.1"
UDP_PORT2 = 5005
# Connecting socket with internal network and intializing sock object
sock2 = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock2.bind((UDP_IP2, UDP_PORT2))
# wait for a sec to intisalize next UDP        
print("wait for 1 sec")
time.sleep(1)


'''
# PORT socket for "serial_connect_pub.py" for "TAKEOFF" : receiving data
# Intialising UDP IP and PORT at 127.0.0.1:5009
'''
UDP_IP3 = "127.0.0.1"
UDP_PORT3 = 5009
# Connecting socket with internal network and intializing sock object
sock3 = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock3.bind((UDP_IP3, UDP_PORT3))
# wait for a sec to intisalize next UDP        
print("wait for 1 sec")
time.sleep(1)


'''
# PORT socket for "serial_connect_pub.py" for "WAYPOINTS" : seding and receiving data
# Intialising UDP IP and PORT at 127.0.0.1:50010
'''
UDP_IP4 = "127.0.0.1"
UDP_PORT4 = 5010
# Connecting socket with internal network and intializing sock object
sock4 = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock4.bind((UDP_IP4, UDP_PORT4))


'''
Function Name: 	get_distance_metres
Input: 		    currentLocation, targetWaypointLocation
Output: 	    returns the distance in meters between both waypoints
Logic: 		    uses the root(distance_between_latitude^2 + distance_between_longitude^2) * 1.113195e5 formula
                where 1.113195e5 is the error vales and multiply value; which is error(1.113195) and multiply value(10^5)
Example Call:	get_distance_metres(currentLocation, targetWaypointLocation)
'''
def get_distance_metres(aLocation1, aLocation2):
    # retriving lat and lon data from both location
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5


'''
Function Name: 	add_mission
Input: 		    None
Output: 	    None
Logic: 		    Downloads the cmds listfrom drone,
                Adds the waypoints list on the cmds parameter which is the command list of drone,
                uploads the new commands list to the drone and the "cmds" gets activated 
                when the flight mode of the drone changes to "AUTO"
Example Call:	add_mission()
'''
def add_mission():
    global waypoint_list, no_of_waypoint
    
    # declaring object of vehicle.commands and importing data simultaneously
    cmds = vehicle.commands
    
    # clearing data
    print(" Clear any existing commands")
    cmds.clear() 
    
    # Using for loop to add the command to cmds list
    print(" Define/add new commands.")
    for i in range(0, no_of_waypoint):

        # making the point variable as an instance of LocationGlobal and format for lat and lon
        point = LocationGlobal(waypoint_list[i][0], waypoint_list[i][1], 0)

        # Adding the GPS points after extraction over mavlink command
        # last 3 parameters are for lat, lon, alt
        cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, point.lat, point.lon, waypoint_list[i][2]))

    # Adding an RTL - Return to launch command at the end of the mission
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, 10))

    # uploading new commands to the drone
    print(" Upload new commands to vehicle")
    cmds.upload()


'''
Function Name: 	return_waypoint
Input: 		    wp1 - first waypoint  i.e. first point on square
                wp2 - second waypoint i.e. second point on square
                wp3 - third waypoint  i.e. third point on square
                wp4 - fourth waypoint i.e. fourth point on square
                height - altitude of drone hovering above the ground

                wp1                           wp2 lane1
                -------------------------------
                .                             .
                .                             .
                .                             .
                .                             .
                -------------------------------
                wp4                           wp3 lane2
Output: 	    returns all the waypoints needed for zig-zag path inside the square region

                wp1       p1       p4         wp2   lane 1
                ----->-------------------->----
                .          .        .         .
                .          .        .         .
                .         \/        /\        \/
                .          .        .         .
                --------------->---------------
                wp4       p2       p3         wp3  lane 2


Logic: 		    checks for distance between waypoints on lane1 and lane2.
                checks for ground area's width covered by camera depending on height and Field of vision of camera trigonometry.
                Appends the list  of lane1 and lane2 by using points on same lane math formula w.r.t distance of each point decided,
                by the width of area covered by drone of ground.
                Appends the list of waypoints of lane1 and lane2 in order of even and odd since the order should be,
                p1, p1', p2', p2, p3, p3', p4', p4 where: ' indicates order of point of lane2 so the set of 11', 2'2, 33' shall be solved
                by using for loop and check for index value to be odd or even.
Example Call:	return_waypoint(wp1, wp2, wp3, wp4, height)
'''
def return_waypoint(wp1, wp2, wp3, wp4, height):

    '''
    Function Name: 	distance
    Input: 		    a1 -> first coordinate
                    a2 -> second coordinate
    Output: 	    returns the distance
    Logic: 		    calculates the distance between two points using distance formula for 2D 
                    and multiplying with error of 1.113195
    Example Call:	distance(a1, a2)
    '''
    def distance(a1, a2):
        dlat = a2[0] - a1[0]
        dlong = a2[1] - a1[1]
        return (math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5)

    '''
    Function Name: 	width_on_Ground
    Input: 		    height -> altitude of the drone relative to launch point
                    fov    -> Field of Vision of camera
    Output: 	    returns the camera's covering ground area's width
    Logic: 		    using tan() function to find the ground area covered
                                    drone
                                    ;;;;;
                                     /|\    theta = FOV taking its half
                                    / | \
                                   /  |  \  height = altitude of drone
                                  /   |   \ 
                                  ---------  base = width of area covered by drone
    Example Call:	width_on_Ground(height, fov):
    '''
    def width_on_Ground(height, fov):
        width = 2*(height / math.tan((fov/2)*(math.pi/180)))
        return width
        
    # storing the width of area covered by camera of ground    
    new_wp = width_on_Ground(height, 60)
    
    # Declaring emplty list of lane1, lane2 and waypoint
    lane1 = []
    lane2 = []
    waypoint = []

    # Calculating distance of end-points of both lane
    dist1 = distance(wp1, wp2)
    dist2 = distance(wp3, wp4)

    # calculating the no. of waypoints by distance of end-point of lane
    # divided by the width of area covered by camera of ground
    no_wp1 = int(round((dist1/new_wp), 0))
    no_wp2 = int(round((dist2/new_wp), 0))

    # Stroing the lane1 waypoints
    for i in range(0, no_wp1):
        new_x = wp1[0] - (((new_wp*(i+1))*(wp1[0] - wp2[0]))/dist1)
        new_y = wp1[1] - (((new_wp*(i+1))*(wp1[1] - wp2[1]))/dist1)
        lane1.append([new_x, new_y, wp1[0][2]])

    # Stroing the lane2 waypoints
    for i in range(0, no_wp2):
        new_x = wp4[0] - (((new_wp*(i+1))*(wp4[0] - wp3[0]))/dist2)
        new_y = wp4[1] - (((new_wp*(i+1))*(wp4[1] - wp3[1]))/dist2)
        lane2.append([new_x, new_y, wp1[0][2]])

    # Appending the waypoints as stated on LOGIC of the parent function's description
    # for final waypoint list from lane1 and lane2 using odd-even logic
    for i in range(0, int((no_wp1 + no_wp2)/2)):
        if ((i % 2) == 0):
            waypoint.append(lane1[i])
            waypoint.append(lane2[i])
        else:
            waypoint.append(lane2[i])
            waypoint.append(lane1[i])    
    
    return waypoint


'''
Function Name: 	arm_and_takeoff
Input: 		    aTargetAltitude - the altitude at which the drone takesoff
Output: 	    None
Logic: 		    checks for armable condition, if yes ARMS the drone,
                and takes_off to the told altitude
Example Call:	arm_and_takeoff(10)
'''
def arm_and_takeoff(aTargetAltitude):

    # Checks if the drone is armable every 1 sec
    while not vehicle.is_armable:
        time.sleep(1)
    print("Arming motors")

    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")

    # Arming the vehicle
    vehicle.armed = True

    # If not armed then waits for arming
    while not vehicle.armed:      
        print(" Waiting for arming...")
        time.sleep(0.8)

    print("Taking off!")
    # Take off to target altitude
    vehicle.simple_takeoff(aTargetAltitude) 

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)      
        #Trigger just below target alt.
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


#Set up option parsing to get connection string
parser = argparse.ArgumentParser(description='Demonstrates basic mission operations.')
parser.add_argument('--connect', 
                   help="vehicle connection target string. If not specified, SITL automatically started and used.")
# Storing the parsed arg after --connect                    
args = parser.parse_args()

# Storing the IP:port from mavproxy server
connection_string = args.connect

# Connect to the Vehicle on the received arg port at 57600 baud rate
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, baud=57600) 

# Loops until it recieves a non-zero value of mode
while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print("received message: %s" % data)
    if data != "0":
        mode = int(data)
        for i in range(0, 5):
            # Sends feedback as "TRUE" back to the software by telemetry via socket 5 times
            sock.sendto(bytes("RECEIVED:TRUE", 'utf-8'), (UDP_IP, UDP_PORT))
        break
    sock.sendto(bytes("RECEIVED:FALSE", 'utf-8'), (UDP_IP, UDP_PORT))

# Loops until all four waypoints of square are not received
# data is in format of ( s.no, lat, lon, height)
while True:
    data4, addr4 = sock4.recvfrom(1024) # buffer size is 1024 bytes
    print("received message: %s" % data4)
    data4 = data4.strip("()")
    data4 = list(data4.split(","))

    if data4[3] != 0:
        no_of_waypoint = 4        
        while True:
            data4, addr4 = sock4.recvfrom(1024) # buffer size is 1024 bytes
            print("received message: %s" % data4)

            # seperating data by removing "()" and spliting data by ,
            data4 = data4.strip("()")
            data4 = list(data4.split(","))

            # converting s.no. and height into "int" and "lat and lon" to float value
            data4[0] = int(data4[0])
            data4[1] = float(data4[1])
            data4[2] = float(data4[2])
            data[3] = int(data4[3])

            # appends only if next waypoint is received
            if data4[0] == (waypoint_no + 1):
                waypoint_list.append([data4[1], data4[2], data4[3]])
                waypoint_no += 1
            
            # if 4 waypoints are received then break out of loop
            if (waypoint_no == 4) and (waypoint_no != 0):
                break

        # sending feedback confirmation 5 times
        for i in range(0, 5):
            sock4.sendto(bytes("RECEIVED:TRUE", 'utf-8'), (UDP_IP4, UDP_PORT4))

    sock.sendto(bytes("RECEIVED:FALSE", 'utf-8'), (UDP_IP, UDP_PORT))



# Waits  for takeoff command to continue the script from the socket by takeoff topic
while True:
    data3, addr3 = sock3.recvfrom(1024) # buffer size is 1024 bytes
    print("received message: %s" % data3)
    if data3 == "TRUE":
            break
       
# generate the waypoint list for zig-zag waypoints by proving corner points of square received from software
waypoint_list = return_waypoint(waypoint_list[0], waypoint_list[1], waypoint_list[2], waypoint_list[3], waypoint_list[0][2])

# add those waypoints on the mission commands of drone
print('create mission')
add_mission()

#Arm and takeoff to a given height here the thord element of every element
# in the waypoint list is the common height
arm_and_takeoff(waypoint_list[0][3])

print("Starting mission")
# Sets the waypoint list index to 0
vehicle.commands.next=0

# Set mode to AUTO to start mission
vehicle.mode = VehicleMode("AUTO")
time.sleep(1)
while vehicle.mode.name != "AUTO":
    vehicle.mode = VehicleMode("AUTO")
    print("Waiting for AUTO mode flight mode") 
    time.sleep(1)     

# Loop forever
while True:

    # store the nextwaypoint index
    nextwaypoint=vehicle.commands.next 

    # mode is 2 then execute else continue as planned   
    if mode == 2:

        # Check for myDetection.py messages
        data2, addr2 = sock2.recvfrom(1024) # buffer size is 1024 bytes
        print("received message: %s" % data2)
        
        # split the sentence by :
        words = data2.split(':')
        print(words)

        # If found distance as it Distance will be only available when the person is detected
        if words[0] == "Distance":

            # if the distance is less than 7 meter then the flight mode changes to GUIDED
            if int(words[1]) < 7:

                #Changing flight mode to GUIDED
                vehicle.mode = VehicleMode("GUIDED")
                time.sleep(0.4)
                while vehicle.mode.name != "GUIDED":
                    vehicle.mode = VehicleMode("GUIDED")
                    print("Waiting for GUIDED flight mode")
                
                # Adjustment in YAW w.r.t the person detected on the frame
                while True:
                    data2, addr2 = sock2.recvfrom(1024) # buffer size is 1024 bytes
                    print("received message: %s" % data2)
                    words = data2.split(':')
                    print(words)

                    if words[0] == "Angle":
                        # if: -1 then the person is on left side
                        #      0 then the person is in the middle
                        #      1 then the person is on the right side

                        # (0, 0, mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0, 5, 0, -1, 1, 0, 0, 0)
                        # 5  -> the degree of rotation                                 : 5th parameter
                        # -1 -> counter clockwise rotation 1-> for clockwise rotation  : 7th parameter
                        # 1  -> relative yaw change, relative to the previous yaw      : 8th parameter
                        if int(words[1]) == -1:
                            msg = vehicle.message_factory.command_long_encode(0, 0, mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0, 5, 0, -1, 1, 0, 0, 0)
                            vehicle.send_mavlink(msg)

                        if int(words[1]) == 1:
                            msg = vehicle.message_factory.command_long_encode(0, 0, mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0, 5, 0, 1, 1, 0, 0, 0)
                            vehicle.send_mavlink(msg)

                        if int(words[1]) == 0:
                            break

                # Store the GPS location 
                frame = vehicle.location.global_relative_frame 

                # Get the set of commands from the vehicle
                cmds = vehicle.commands
                cmds.download()
                cmds.wait_ready()

                # Save the vehicle commands to a missionlist
                missionlist=[]
                for cmd in cmds:
                    missionlist.append(cmd)
                
                # store while going to which waypoint the person is detected
                person_detected_waypoint = nextwaypoint

                # Modify the mission as needed. 
                missionlist.insert(nextwaypoint, missionlist[nextwaypoint].command)

                # Add the lower altitude waypoint with same lat and lon into the waypoint
                missionlist[nextwaypoint] = Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, frame.lat, frame.lon, frame.alt - 3)

                # Clear the current mission (command is sent when we call upload())
                cmds.clear()

                #Write the modified mission 
                for cmd in missionlist:
                    cmds.add(cmd)

                # upload the mission    
                cmds.upload()

                # Changing to AUTO mode to resume mission
                vehicle.mode = VehicleMode("AUTO")
                time.sleep(0.4)
                while vehicle.mode.name != "AUTO":
                    vehicle.mode = VehicleMode("AUTO")
                    print("Waiting for AUTO flight mode")

        # if the lower altitude waypoint i.e. in front of person is reached then
        # Change the flight mode to GUIDED to stop the drone on the position
        if nextwaypoint == person_detected_waypoint + 1:
            vehicle.mode = VehicleMode("GUIDED")
            time.sleep(0.4)
            while vehicle.mode.name != "GUIDED":
                vehicle.mode = VehicleMode("GUIDED")
                print("Waiting for GUIDED flight mode")

                # Play the audio and wait for 10 seconds
                playsound('audio.mp3')
                time.sleep(10)
                break

            # change the flight mode to AUTO to continue the mission
            vehicle.mode = VehicleMode("AUTO")
            time.sleep(0.4)
            while vehicle.mode.name != "AUTO":
                vehicle.mode = VehicleMode("AUTO")
                print("Waiting for AUTO flight mode") 

            #ignoring any person detection for 5 secs.
            time.sleep(5)    


#Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()
