/*
*
* Project Name: 	FALON drone - stranded people detection using UAV
* Author List: 		Sarang Chouguley
* Filename: 		mode1.js
* Functions: 		select_waypoints(), track_drone(), send_waypoints(),
                    toggle_options(), main()
* Global Variables:	waypoints
*
*/

// Load modules
const tfjsNode = require('@tensorflow/tfjs-node');
const path = require('path');
const video = require(path.join(__dirname, "../js", "video"));
const telemetry = require(path.join(__dirname, "../js", "telemetry"));
const serial = require(path.join(__dirname, "../js", "serial"));
const mapBox = require(path.join(__dirname, "../js", "mapbox"));

// global variables
var waypoints = [];

// defining buttons
const toggle_options = document.getElementById('showOptionsBtn')
const select_waypoints = document.getElementById('selectWaypointsCheckBox');
const send_waypoints = document.getElementById('sendWaypointsBtn');
const track_drone = document.getElementById('trackDroneCheckBox')


/*
*
* Function Name: 	select_waypoints
* Input: 		checkbox_element -> the checkbox element from the UI
* Output: 		Alerts the users whether he can add waypoints or not
* Logic: 		This function is called whenever the user selects or deselectes
                the selectWaypoints Checkbox. If the checkbox is selected it calls 
                the addWaypoints method with a true value.
* Example Call:		select_waypoints(checkbox)
*
*/
select_waypoints.addEventListener('change', (ele) => {
    const select = ele.target.checked;
    if (select) {
        waypoints = mapBox.add_waypoints(select);
        alert('Select Waypoints ON. Click on Map to add waypoints');
    } else {
        waypoints = mapBox.add_waypoints(select);
        alert('Select Waypoints OFF');
        mapBox.draw_area(waypoints);
    }
});

/*
*
* Function Name: 	track_drone
* Input: 		checkbox_element -> the checkbox element from the UI
* Output: 		Alerts the users whether the drone is being tracked or not
* Logic: 		This function is called whenever the user selects or deselectes
                the trackDrone Checkbox. If the checkbox is selected it calls 
                the initLine and getGPSCoordinates method, to track the drone 
                and show a line on the map.
* Example Call:		track_drone(checkbox)
*
*/
track_drone.addEventListener('change', (ele) => {
    const track = ele.target.checked;
    var interval;
    if (track) {
        mapBox.initLine();
        interval = setInterval(() => {
            const coordinates = telemetry.get_gps_coordinates();
            mapbox.draw_area(coordinates);
        }, 500);
        alert('Drone Tracking started')
    } else {
        clearInterval(interval);
        alert('Drone Tracking started');
    }
})

/*
*
* Function Name: 	toggle_options
* Input: 		None
* Output: 		None
* Logic: 		Toggles the options in UI
* Example Call:		toggle_options
*
*/
toggle_options.addEventListener('click', () => {
    document.querySelector('.hiddenMenu').classList.toggle('show')
});

/*
*
* Function Name: 	send_waypoints
* Input: 		None
* Output: 		None
* Logic: 		This function is called when the user presses the send_waypoints 
                button.It calls the send_waypoints method to send waypoints 
                to the drone.
* Example Call:		send_waypoints()
*
*/
send_waypoints.addEventListener('click', () => {
    telemetry.send_waypoints(waypoints, 8, 1);
});

/*
*
* Function Name: 	main
* Input: 		None
* Output: 		None
* Logic: 		Calls the get_mediaList, plot_markers, send_to_esp, telemetryStart.
* Example Call:		main()
*
*/
function main(){
    video.get_mediaList();
    setInterval(mapBox.plot_markers, 500);
    setTimeout(serial.send_to_esp, 1000);
    setTimeout(telemetry.start, 1000);
}

main()

