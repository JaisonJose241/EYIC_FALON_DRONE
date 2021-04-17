/*
*
* Project Name: 	FALON drone - stranded people detection using UAV
* Author List: 		Sarang Chouguley
* Filename: 		telemetry.js
* Functions: 		start(), save_lnglat(), cal_gps_distance(), send_waypoints(),
                    save_gps()
* Global Variables:	distThreshold, receivedLngLat, gpsList, isModeReceived,
                    isWpReceived, isPersonDetected, modeType, client
*
*/

// Load modules
const net = require('net');
const path = require('path');
const portNumber = require(path.join(__dirname, '../envVariable.json')).telemetrySocketPort;
const plot_markers = require(path.join(__dirname, 'mapbox')).plot_markers;

// global variables
const distThreshold = 5;
var receivedLngLat = [];
var gpsList = [];
var isModeReceived = false;
var isWpReceived = false;
var isPersonDetected = false;
var modeType = 0;
const client = new net.Socket();

// define buttons
const startDroneBtn = document.getElementById('startDroneBtn');
const stopDroneBtn = document.getElementById('stopDroneBtn');

/*
*
* Function Name: 	start
* Input: 		None
* Output: 		Starts socket connection to python telemetry file
* Logic: 		This function initialises connection with python telemetry file using 
                socket
* Example Call:		start()
*
*/
function start() {
    alert('Connecting to telemetry.py server...')
    var isError = false;

    // connect to socket
    client.connect({ port: portNumber, host: '127.0.0.1' }, () => {
        console.log('connected to: ', client.remotePort);
        isError = false;
    });

    // receive data
    client.on('data', (dataBytes) => {
        const data = dataBytes.toString('utf-8');
        isPersonDetected = false;
        // received data from data topic
        if (data.startsWith('DETECTION')) {
            if (data.includes('TRUE')) {
                isPersonDetected = true;
                console.log('coordinates saved')
            } else {
                console.log('no coordinates received');
                isPersonDetected = false;
            }
        }

        // received data from modetopic
        if (data.includes('MODE_RECEIVED')) {
            if (data.includes('TRUE')) {
                isModeReceived = true;
                alert('Mode received by Drone');
            } else {
                isModeReceived = false;
            }
        }

        // received data from modetopic
        if (data.includes('WAYPOINTS_RECEIVED')) {
            if (data.includes('TRUE')) {
                isWpReceived = true;
                alert('Waypoints received by drone');
            } else {
                isWpReceived = false;
            }
        }

        // receive detection data from drone
        if (data.startsWith('DATA')) {
            save_gps(data)
        }

    });

    // on error print error
    client.on('error', (error) => {
        console.log('JS Socket Error', error);
        isError = true;
    })

    // start drone
    startDroneBtn.addEventListener('click', () => {
        console.log('Start Drone Btn clicked')
        client.write('START');
    })

    if (!isError) {
        // create custom event 
        const customEvent = new Event('waitForData');
        // Listen for the event.
        startDroneBtn.addEventListener('waitForData', function (e) {
            console.log('waiting for data')
            client.write('garbage');
        });
        // call custom event every 1 sec
        setInterval(() => {
            startDroneBtn.dispatchEvent(customEvent)
        }, 1000)
    }

    stopDroneBtn.addEventListener('click', () => {
        console.log("Stop Drone Btn clicked")
        client.write('STOP')
    })
}

/*
*
* Function Name: 	save_lnglat
* Input: 		gps coordinates
* Output: 		save gps coordinates
* Logic: 		This function extracts gps coordinates from string send by telemetry
                and stores the gps coordinates 
* Example Call:		save_lnglat('lon: 43.3434, lat: 65.5656')
*
*/
function save_lnglat(data) {
    // check for valid data
    const lng = data.slice(data.lastIndexOf('lon') + 4, data.lastIndexOf(','));
    const lat = data.slice(data.lastIndexOf('lat') + 4, data.indexOf(','));
    var  value = {}
    const personState = require(path.join(__dirname, 'detection')).get_person_state() 

    // check if lat and long are not empty
    if (lng !== '' && lat !== '') {
        if (modeType == 1 || modeType == 0) {
            value = { id: id, lng: lng, lat: lat, status: 4 }
        }else{
            value = { id: id, lng: lng, lat: lat, status: personState }
        }
        if (receivedLngLat.length > 0) {
            const len = receivedLngLat.length;
            const distance = cal_gps_distance(receivedLngLat[len - 1], value);
            console.log(distance)
            if (distance > distThreshold) {
                receivedLngLat.push(value)
                plot_markers(receivedLngLat)
                console.log(`coordinates saved: ${JSON.stringify(receivedLngLat)}`)
            } else {
                console.log('Distance between coordinates less than threshold')
            }
        } else {
            receivedLngLat.push(value)
            console.log(`1st coordinates received: ${JSON.stringify(receivedLngLat)}`)
            plot_markers(receivedLngLat)
        }
        console.log(receivedLngLat)
    } else {
        alert(`error in saving lat lng: lat lng empty`)
    }
}

/*
*
* Function Name: 	caL_gps_distance
* Input: 		2 gps coordinates
* Output: 		returns distance between 2 gps coordinates in meters
* Logic: 		This function calculates distance between 2 gps coordinates
* Example Call:		cal_gps_distance([34.9090, 58.5353], [59.4545, 23.4443])
*
*/
function cal_gps_distance(location1, location2) {
    /** 
    Returns the ground distance in metres between two LocationGlobal objects.
    This method is an approximation, and will not be accurate over large distances and close to the
    earth's poles. It comes from the ArduPilot test code: 
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    */
    dlat = parseFloat(location2.lng) - parseFloat(location1.lng);
    dlong = parseFloat(location2.lat) - parseFloat(location1.lat);
    return Math.sqrt((dlat * dlat) + (dlong * dlong)) * 1.113195e5
}

/*
*
* Function Name: 	send_waypoints
* Input: 		gps coordinates, altitude, mode
* Output: 		sends data to drone via telemetry
* Logic: 		This function sends initial waypoints along with altitude and mode
                type to drone via telemetry
* Example Call:		send_waypoints([34.5454, 65.4454], 10, 2)
*
*/
function send_waypoints(waypoints, altitude, mode) {
    var stringFrame = ``;
    modeType = parseInt(mode);

    // if mode is received by drone , send waypoints
    if (isModeReceived) {
        if (!isWpReceived) {
            if (waypoints.length > 1) {
                waypoints.map((element, index) => {
                    stringFrame = `(${index},${element.lng},${element.lat},${altitude},${waypoints.length})`;
                    client.write(stringFrame);
                })
                console.log('data sent to drone')
            } else {
                console.log('Error in sending to drone: waypoints list is empty')
            }
        }
    } else {
        // else send mode
        client.write(`MODE ${mode}`);
    }
}

/*
*
* Function Name: 	save_gps
* Input: 		gps coordinates
* Output: 		saves gps coordinates of drone
* Logic: 		This function stores gps coordinates of drone received via telemetry
* Example Call:		save_gps('lon: 34.4545, lat: 54.3433')
*
*/
function save_gps(gps) {
    // check for valid data
    const lng = gps.slice(gps.lastIndexOf('lon') + 4, gps.lastIndexOf(','));
    const lat = gps.slice(gps.lastIndexOf('lat') + 4, gps.indexOf(','));

    // check if lat and long are not empty
    if (lng !== '' && lat !== '') {
        const value = { lng: lng, lat: lat }
        if (gpsList.length > 0) {
            const len = gpsList.length;
            const distance = calulateGpsDistance(gpsList[len - 1], value);
            console.log(distance)
            if (distance > distThreshold) {
                gpsList.push(value)
                if (isPersonDetected) {
                    save_lnglat(gps)
                }
            } else {
                console.log('Distance between gps coordinates less than threshold')
            }
        } else {
            gpsList.push(value)
            console.log(`1st coordinates received: ${JSON.stringify(value)}`)
        }
    } else {
        console.log(`error in saving gps: invalid gps data received from telemetry`)
    }
}

/*
*
* Function Name: 	get_gps_coordinates
* Input: 		None
* Output: 		return latest gps coordinates of drone
* Logic: 		This function returns latest gps coordinates of drone
* Example Call:		get_gps_coordinates()
*
*/
function get_gps_coordinates() {
    return gpsList[gpsList.length - 1];
}


module.exports = {
    start,
    receivedLngLat,
    send_waypoints,
    get_gps_coordinates
}