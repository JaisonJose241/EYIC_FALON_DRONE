/*
*
* Project Name: 	FALON drone - stranded people detection using UAV
* Author List: 		Sarang Chouguley
* Filename: 		detection.js
* Functions: 		load_posenet(), detect_pose(), get_person_state()
* Global Variables:	validStates, threshold, personState, pState
*
*/

// load modules
const tf = require('@tensorflow/tfjs')
const posenet = require("@tensorflow-models/posenet");

// get ui elements
const videoDiv = document.getElementById('video')
const statusDiv = document.getElementById('statusDiv')

// global variables
const validStates = {
    0: "AT SAFE PLACE",
    1: "AT SAFE PLACE BUT NEED LIFE-STOCK",
    2: "URGENT RESQUE",
    4: "NOT DETECTED"
}
const threshold = 0.75;
var personState = "none";
var pState = '';


/*
*
* Function Name: 	load_posenet
* Input: 		None
* Output: 		Returns loaded posenet model
* Logic: 		This function initialises and loads posenet model of tfjs.
* Example Call:		load_posenet()
*
*/
async function load_posenet() {
    const net = await posenet.load({
        architecture: 'ResNet50',
        outputStride: 32,
        inputResolution: { width: 640, height: 640 },
        quantBytes: 2
    });
    return net;
}

/*
*
* Function Name: 	detect_pose
* Input: 		posenet model
* Output: 		Sets the person state variable according to the detected status of person
* Logic: 		This function calculates the state of person, by detecting the position
                of left and right sholder, elbow and wrist
* Example Call:		detect_posenet(model)
*
*/
async function detect_pose(net) {
    const pose = await net.estimateSinglePose(videoDiv, { decodingMethod: "single-person" });
    const joints = {
        "leftSholder": 5,
        "rightSholder": 6,
        "leftElbow": 7,
        "rightElbow": 8,
        "leftWrist": 9,
        "rightWrist": 10
    }

    // for detecting state of left hand
    if (pose.keypoints[joints["leftWrist"]].score >= threshold && pose.keypoints[joints["leftElbow"]].score >= threshold) {
        if (pose.keypoints[joints["leftWrist"]].position.y < pose.keypoints[joints["leftElbow"]].position.y) {
            personState = 1 //1 //"Left Hand Up";

            statusDiv.innerText = '';
            statusDiv.innerText = `Status: ${validStates[1]}`;
        }
    } else {
        pState = "Left Hand not detected"
    }

    // for detecting state of right hand
    if (pose.keypoints[joints["rightWrist"]].score >= threshold && pose.keypoints[joints["rightElbow"]].score >= threshold) {
        if (pose.keypoints[joints["rightWrist"]].position.y < pose.keypoints[joints["rightElbow"]].position.y) {
            personState = 0 //0 //"Right Hand Up";

            statusDiv.innerText = '';
            statusDiv.innerText = `Status: ${validStates[0]}`;
        }

    } else {
        pState = "right Hand not detected"
    }

    // for detecting state of both hands
    if (pose.keypoints[joints["leftWrist"]].score >= threshold && pose.keypoints[joints["leftElbow"]].score >= threshold && pose.keypoints[joints["rightWrist"]].score >= 0.75 && pose.keypoints[joints["rightElbow"]].score >= 0.75) {
        if ((pose.keypoints[joints["leftWrist"]].position.y < pose.keypoints[joints["leftElbow"]].position.y) && (pose.keypoints[joints["rightWrist"]].position.y < pose.keypoints[joints["rightElbow"]].position.y)) {
            personState = 2 //2 //"Both Hands Up"

            statusDiv.innerText = '';
            statusDiv.innerText = `Status: ${validStates[2]}`;
        }
    } else {
        pState = "Hands not detected";
    }

    // print state
    console.log(pState)
    return (personState);
}

/*
*
* Function Name: 	get_person_state
* Input: 		None
* Output: 		Returns the person state
* Logic: 		Simply returns the state of person state
* Example Call:		get_person_state()
*
*/
function get_person_state() {
    return personState;
}
module.exports = { 
    load_posenet, 
    detect_pose, 
    get_person_state 
}

