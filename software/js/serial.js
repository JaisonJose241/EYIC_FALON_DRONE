/*
*
* Project Name: 	FALON drone - stranded people detection using UAV
* Author List: 		Sarang Chouguley
* Filename: 		serial.js
* Functions: 		send_to_esp
* Global Variables:	client
*
*/

// Load required modules
const net = require('net');
const path = require('path');
const portNumber = require(path.join(__dirname, '../envVariable.json')).serialSocketPort;
const client = new net.Socket();


console.log('Connecting to serialCom.py...')
client.connect({ port: portNumber, host: '127.0.0.1' });

client.on('error', (error) => {
    alert('Error in Serial.js: ', error)
})

client.on('close', (e) => {
    alert('Connection Closed with serialCom.py')
})

client.on('data', (bytes) => {
    const data = bytes.toString('utf-8');

    // check if data contains string rescued
    if(data.includes('rescued')){
        // get id
        const rescuedId = data[data.indexOf('=')+1]
        return rescuedId;
    }
});

/*
*
* Function Name: 	send_to_esp
* Input: 		None
* Output: 		Sends data using socket to python file
* Logic: 		This function initialises connect with python file and sends the gps location
                of people detected by drone, to python file
* Example Call:		send_to_esp()
*
*/

function send_to_esp() {
    var stringFrame = '';

    var sendData = require(path.join(__dirname, 'telemetry')).receivedLngLat; 

    setInterval(() => {
        console.log('send to ESP...')
        if (sendData.length > 0) {
            sendData.forEach(element => {
                stringFrame = stringFrame + `${element.id},${element.lng},${element.lat},${element.status}\n`;
            })
            client.write(stringFrame);
            console.log('data sent to esp')
        } else {
            console.log('Error in sending to esp: receivedLatLng is empty')
        }
    }, 4000)
}


module.exports = {
    send_to_esp
}