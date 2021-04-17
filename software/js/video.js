/*
*
* Project Name: 	FALON drone - stranded people detection using UAV
* Author List: 		Sarang Chouguley
* Filename: 		video.js
* Functions: 		get_mediaList()
* Global Variables:	None
*
*/ 

/*
*
* Function Name: 	get_mediaList
* Input: 		None
* Output: 		Returns list of cameras available in the sytem
* Logic: 		This function returns and sets available cameras in the system
* Example Call:		get_mediaList()
*
*/
function get_mediaList() {
    const videoDiv = document.getElementById('video');
    const select = document.getElementById('select');
    const startVideoBtn = document.getElementById('startVideo');
    let currentStream;

    function stopMediaTracks(stream) {
        stream.getTracks().forEach(track => {
            track.stop();
        });
    }

    function gotDevices(mediaDevices) {
        select.innerHTML = '';
        select.appendChild(document.createElement('option'));
        let count = 1;
        mediaDevices.forEach(mediaDevice => {
            if (mediaDevice.kind === 'videoinput') {
                const option = document.createElement('option');
                option.value = mediaDevice.deviceId;
                const label = mediaDevice.label || `Camera ${count++}`;
                const textNode = document.createTextNode(label);
                option.appendChild(textNode);
                select.appendChild(option);
            }
        });
    }

    startVideoBtn.addEventListener('click', event => {
        if (typeof currentStream !== 'undefined') {
            stopMediaTracks(currentStream);
        }
        const videoConstraints = {};
        if (select.value === '') {
            videoConstraints.facingMode = 'environment';
        } else {
            videoConstraints.deviceId = { exact: select.value };
        }
        const constraints = {
            video: videoConstraints,
            audio: false
        };
        navigator.mediaDevices
            .getUserMedia(constraints)
            .then(stream => {
                currentStream = stream;
                videoDiv.srcObject = stream;
                return navigator.mediaDevices.enumerateDevices();
            })
            .then(gotDevices)
            .catch(error => {
                console.error(error);
            });
    });

    navigator.mediaDevices.enumerateDevices().then(gotDevices);
};

module.exports = { get_mediaList }