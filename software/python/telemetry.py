
"""
*
* Project Name: 	FALON drone - stranded people detection using UAV
* Author List: 		Sarang Chouguley
* Filename: 		telemetry.py
* Functions: 		init_port_forward(), send_data_to_js(), take_off(), 
                    emergency_rtl(), send_waypoints(), send_mode(), 
                    init_telemetry(), main()
* Global Variables:	config, c, conn, transport, flag
*
"""

# --------- Import modules ---------- #
from pytelemetry import Pytelemetry
from pytelemetry.transports.serialtransport import *
import time
import socket
import json

# ---- Global Variables ---- #

# load envVariable.json
with open('./envVariable.json') as f:
    jsonFile = json.load(f)
config = json.loads(json.dumps(jsonFile))
transport = SerialTransport()
c = Pytelemetry(transport)

"""
*
* Function Name: 	init_port_forward
* Input: 		test boolean
* Output: 		None
* Logic: 		Initialises socket server, that communicates with js client
* Example Call:		int_port_forward()
*
"""
def init_port_forward(test=False):
    print("starting port from server")
    HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
    # Port to listen on (non-privileged ports are > 1023)
    PORT = config["telemetrySocketPort"]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    global conn
    conn, addr = s.accept()
    print("connected:", str(addr))
    # if test, then test socket connection by echoing something
    if(test):
        while True:
            time.sleep(2)
            conn.sendall(bytes('python telemetry working\n', encoding='utf-8'))
    else:
        # else initialise telemetry
        init_telemetry()


"""
*
* Function Name: 	printer
* Input: 		topic, data, options
* Output: 		Prints the data received from telemetry
* Logic: 		To print data for the topic (acts as a callback function)
* Example Call:		printer('data', 'hello')
*
"""
def printer(topic, data, opts):
    print(topic, " : ", data)


"""
*
* Function Name: 	send_data_to_js
* Input: 		topic, data, options
* Output: 		sends data to js clinet
* Logic: 		Function to send data to js client through socket
* Example Call:		send_data_to_js('data', 'hi')
*
"""
def send_data_to_js(topic, data, opts):
    print(topic, " : ", data)
    global conn
    global flag
    if(data.decode('utf-8') == ' '):
        flag = True
    conn.send(bytes(topic+' '+data, encoding='utf-8'))


"""
*
* Function Name: 	take_off
* Input: 		None
* Output: 		Send takeoff command to drone
* Logic: 		Function to send takeOff command to drone via telemetry
* Example Call:		take_off()
*
"""
def take_off():
    global c
    print("Drone Takeoff")
    for i in range(0, 5):
        c.publish('TAKE_OFF', 'TRUE', 'string')
        time.sleep(0.7)


"""
*
* Function Name: 	emergency_rtl
* Input: 		None
* Output: 		Sends return to land command to drone
* Logic: 		Function to send RTL command to drone via telemetry
* Example Call:		emergency_rtl()
*
"""
def emergency_rtl():
    global c
    print("Drone Stop")
    for i in range(0, 5):
        c.publish('RTL', 'TRUE', 'string')
        time.sleep(0.7)

"""
*
* Function Name: 	send_waypoint
* Input: 		waypoint
* Output: 		sends waypoint to drone
* Logic: 		Function to send waypoint to drone
* Example Call:		send_waypoint('(id: 3, lng: 34.34343, lat: 454543)')
*
"""
def send_waypoint(waypoint):
    global c
    print('Sending waypoint:', str(waypoint))
    c.publish('WAYPOINTS', waypoint, 'string')


"""
*
* Function Name: 	send_mode
* Input: 		mode
* Output: 		Sends operation mode to drone
* Logic: 		Function to send operation  mode to drone
* Example Call:		send_mode(2)
*
"""
def send_mode(mode):
    global c
    print('Sending mode:', mode)
    c.publish('MODE', mode, 'string')

"""
*
* Function Name: 	init_telemetry
* Input: 		None
* Output: 		None
* Logic: 		Function to Initialise telemetry connection
* Example Call:		init_telemetry
*
"""
def init_telemetry():
    global c
    global conn
    global flag
    options = dict()
    options['port'] = "/dev/ttyUSB1"
    options['baudrate'] = 57600

    transport.connect(options)
    c.subscribe('data', send_data_to_js)
    bad_frame = bytearray(b'0700736f6d65746f70696300626f6f7961613ecc')
    c.api._decode_frame(bad_frame)

    while True:
        c.update()
        rcvData = conn.recv(1024).decode('utf-8')
        print('received data from js client: ', str(rcvData))

        if flag == True:
            break
        if rcvData == 'START':
            take_off()
        if rcvData == 'STOP':
            emergency_rtl()
        if rcvData.startswith('WAYPOINT'):
            send_waypoint(rcvData)
        if rcvData.startswith('MODE'):
            send_mode(rcvData[5])

    transport.disconnect()
    print("Done.")


"""
*
* Function Name: 	main function
* Input: 		None
* Output: 		None
* Logic: 		main function of this file
* Example Call:		main()
*
"""
def main():
    global flag
    flag = False
    print("This is main function")
    init_port_forward()

main()
