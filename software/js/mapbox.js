/*
*
* Project Name: 	FALON drone - stranded people detection using UAV
* Author List: 		Sarang Chouguley
* Filename: 		mapbox.js
* Functions: 		add_waypoints, plot_single_marker, plot_markers, 
                    draw_area, init_line, draw_line
* Global Variables:	markerList, waypoints, selectWaypoints, lineGeojson
*
*/

var markersList = [];
var waypoints = [];
var selectWaypoints = false;
// Create a GeoJSON source with an empty lineString.
var lineGeojson = {
    'type': 'FeatureCollection',
    'features': [
        {
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': [[0, 0]]
            }
        }
    ]
};
// set access token
mapboxgl.accessToken = 'pk.eyJ1Ijoic2FyYW5nY2hvdWd1bGV5IiwiYSI6ImNrbHRlZG1uNDA3dTcyd3F4ZmIyNDV4cnQifQ.SySARwQe-u5hi982pK5E3w';

// initialise map
const map = new mapboxgl.Map({
    container: 'mapContainer', // container ID
    style: 'mapbox://styles/sarangchouguley/cklvsum8z38qh17s5yr6btmyi', // style URL
    center: [79.04905350623918, 21.007050226637872], // starting position [lng, lat]
    zoom: 16 // starting zoom
});

// Add geolocate control to the map.
map.addControl(
    new mapboxgl.GeolocateControl({
        positionOptions: {
            enableHighAccuracy: true
        },
        trackUserLocation: true
    })
);

// Search places using geoCoder
map.addControl(
    new MapboxGeocoder({
        accessToken: mapboxgl.accessToken,
        mapboxgl: mapboxgl
    })
);

// place marker on mouse click
map.on('click', function (e) {
    if (selectWaypoints) {
        //On-click add coordinates of marker in waypoints list 
        waypoints.push(e.lngLat);
        plot_markers(waypoints)
    }
});

/*
*
* Function Name: 	add_waypoints
* Input: 		state
* Output: 		add waypoints list
* Logic: 		It sets selectWaypoints to true or false, and returns added waypoints list
* Example Call:		add_waypoints(true)
*
*/
function add_waypoints(state) {
    if(state) {
        selectWaypoints = true;
    }else {
        selectWaypoints = false;
    }
    return waypoints;
}

/*
*
* Function Name: 	plot_single_marker
* Input: 		marker coordinates
* Output: 		Returns a marker 
* Logic: 		This function adds a single marker on the map.
* Example Call:		plot_single_marker(coordinates)
*
*/
function plot_single_marker(coordinates) {
     // create popup
     const pop = new mapboxgl.Popup({
        closeButton: true,
        // closeOnClick: false
    }).setText(JSON.stringify(coordinates))

    // create marker
    var marker = new mapboxgl.Marker({ color: '#432232' })
        .setLngLat([coordinates.lng, coordinates.lat])
        .addTo(map)
        .setPopup(pop)

    return marker;
}

/*
*
* Function Name: 	plot_markers
* Input: 		list of coodinates
* Output: 		None
* Logic: 		Adds more than one marker to the map
* Example Call:		plot_markers([point1, point2, point3])
*
*/
function plot_markers(points) {
        var list = points;
        if (list.length == 0) {
            alert("no coordinates in list");
            return;
        } else {
            console.log("points in list:", list)
        }

        // remove already added markers
        if (markersList.length > 0) {
            markersList.forEach(() => {
                const m = markersList.pop();
                m.remove();
            });
            console.log("Markers list emptyed")
        } else {
            console.log('Markers list is already empty')
        }

        list.forEach(e => {
            // create popup
            const pop = new mapboxgl.Popup({
                closeButton: true,
                // closeOnClick: false
            }).setText(JSON.stringify(e))

            // create marker
            var marker = new mapboxgl.Marker({ color: '#432232' })
                .setLngLat([e.lng, e.lat])
                .addTo(map)
                .setPopup(pop)

            // add marker to global list
            markersList.push(marker)
        });

}

/*
*
* Function Name: 	draw_area
* Input: 		none
* Output: 		a area polygon on map
* Logic: 		This function plots the survey area of the drone on the map
* Example Call:		draw_area()
*
*/
function draw_area() {
    var coordinates = [];
    if(waypoints.length >= 4) {

        // If layer already exists, remove it.
        if (map.getLayer('waypointeLayer')) map.removeLayer('waypointsLayer');
        // If source already exists, remove it.
        if(map.getSource('waypointsSource')) map.removeSource('waypointsSource');

        // create coordinates list
        coordinates = [];
        waypoints.map((w) => {
            coordinates.push([w.lng, w.lat])
        });

        // create source
        map.addSource('waypointsSource', {
            'type': 'geojson',
            'data': {
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [
                        [
                            ...coordinates
                        ]
                    ]
                }
            }
        });

        // add layer
        map.addLayer({
            'id': 'waypointsLayer',
            'type': 'fill',
            'source': 'waypointsSource',
            'layout': {},
            'paint': {
                'fill-color': '#088',
                'fill-opacity': 0.8
            }
        });
    }else {
        alert('Please Select atleast 4 waypoints');
        return ;
    }
    
}

/*
*
* Function Name: 	init_line
* Input: 		None
* Output: 		Initialises line
* Logic: 		This function initialises the line for tracing drone positions
* Example Call:		init_line()
*
*/
function init_line(){
    map.addSource('line', {
        'type': 'geojson',
        'data': lineGeojson
    });

    // add the line which will be modified in the animation
    map.addLayer({
        'id': 'line-animation',
        'type': 'line',
        'source': 'line',
        'layout': {
            'line-cap': 'round',
            'line-join': 'round'
        },
        'paint': {
            'line-color': '#ed6498',
            'line-width': 5,
            'line-opacity': 0.8
        }
    });
}

/*
*
* Function Name: 	draw_line
* Input: 		coordinates -> coordinates of point
* Output: 		Draws a line on the given coordinates on the map
* Logic: 		This function receives the latest point and adds it to the line. 
                This function is used to draw a line, tracing the drone location
* Example Call:		draw_line(point)
*
*/
function draw_line(coordinates) {
    // append new coordinates to the lineString
    if (!lineGeojson.features[0].geometry.coordinates.includes([coordinates.lng, coordinates.lat])){
        lineGeojson.features[0].geometry.coordinates.push([coordinates.lng, coordinates.lat]);
        // then update the map
        map.getSource('line').setData(lineGeojson);
    }
}

module.exports = {
    plot_markers,
    add_waypoints,
    draw_area,
    plot_single_marker,
    init_line,
    draw_line
}