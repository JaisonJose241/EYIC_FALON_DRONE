"""
*
* Project Name: 	FALON drone - stranded people detection using UAV
* Author List: 		Sarang Chouguley
* Filename: 		serial.py
* Functions: 		init_port_forward(), init_serial(), create_frame()
* Global Variables:	config, conn
"""

# ------------ Load modules ----------- #
import serial
import time
import socket
import json

# ---------- Global Variables ---------- #
# load envVariable.json 
with open('./envVariable.json') as f:
  jsonFile = json.load(f)
config = json.loads(json.dumps(jsonFile))

"""
*
* Function Name: 	init_port_forward
* Input: 		test boolean
* Output: 		None
* Logic: 		Function to start socket server, for communication with serial js client
* Example Call:		int_port_forward()
*
"""
def init_port_forward(test=False):
    print("starting port from server")
    HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
    PORT = config["serialSocketPort"]     # Port to listen on (non-privileged ports are > 1023)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    global conn
    conn, addr = s.accept()
    print(f'connected :{addr}')
    # if test then test socket connection
    if(test):
        while True:
            time.sleep(2)
            conn.sendall(bytes('serial python working\n', encoding='utf-8'))
    else:
        # else initialise telemetry
        init_serial()

"""
*
* Function Name: 	init_serial
* Input: 		None
* Output: 		None
* Logic: 		Initialises serial communication with NRF module
* Example Call:		int_serial()
*
"""
def init_serial():
    global conn

    ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=9600,
        timeout=4,
        parity=serial.PARITY_ODD,
        stopbits=serial.STOPBITS_TWO,
        bytesize=serial.EIGHTBITS,
        xonxoff=True
    )

    while True:
        rcvData = conn.recv(1024)
        if rcvData != b' ':
            # ser.write(rcvData)
            dataArray = create_frame(rcvData)
            for i in range(2):
                for element in dataArray:
                    time.sleep(3)
                    ser.write(bytes(element, encoding='utf-8'))
                    print(element)

"""
*
* Function Name: 	create_frame
* Input: 		data
* Output: 		formatted data
* Logic: 		Function to split data and format it
* Example Call:		create_frame()
*
"""
def create_frame(data):
    decoded = data.decode('utf-8')
    e = decoded.splitlines()
    return e

init_port_forward()
