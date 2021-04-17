/*
*
* Project Name: 	FALON drone - stranded people detection using UAV
* Author List: 		Sarang Chouguley
* Filename: 	customMapp.js
* Functions: 		customMap(), addMarkers(), fetchData(), PlotMarkers()
* Global Variables:	None
*
*/
import React, { useState } from 'react';
import { StyleSheet, View, Button, ToastAndroid, Alert } from 'react-native';
import MapboxGL from '@react-native-mapbox-gl/maps';

export default customMap = () => {
    // set access token
    MapboxGL.setAccessToken(
        'pk.eyJ1Ijoic2FyYW5nY2hvdWd1bGV5IiwiYSI6ImNrbHRlZG1uNDA3dTcyd3F4ZmIyNDV4cnQifQ.SySARwQe-u5hi982pK5E3w',
    );

    const [coordinates] = useState([79.04905350623918, 21.007050226637872]);
    const [mapType] = useState("mapbox://styles/sarangchouguley/cklvsum8z38qh17s5yr6btmyi")
    const [markers, setMarkers] = useState([{ lng: 0.049039, lat: 0.006189, status: "Test" }])
    const [dataStore, setDataStore] = useState([])
    const [ids, setIds] = useState([])

    const status = {
        0: 'OK',
        1: 'OK BUT NEED LIFESTOCK',
        2: 'URGENT RESQUE',
        4: 'STATUS NOT SET'
    }

    /*
    *
    * Function Name: 	fetchData
    * Input: 		None
    * Output: 		Returns data from nodemcu
    * Logic: 		Returns data using HTTP GET method from node mcu
    * Example Call:		fetchData()
    *
    */
    const fetchData = () => {
        var requestOptions = {
            method: 'GET',
            redirect: 'follow',
            type: 'application/json'
        };

        fetch("http://192.168.4.1", requestOptions)
            .then(response => response.text())
            .then(result => {
                console.log(result);
                var data;

                // check if result is not an empty or invalid string
                if (result.length > 21) {

                    // parse string for lng, lat , id, and status
                    var startIndex = result.indexOf(',') - 1;
                    var lastIndex = result.lastIndexOf(',') + 2;
                    var values = result.substring(startIndex, lastIndex)
                    values = values.split(',')

                    // check if successfully parsed
                    if (values.length > 2) {
                        data = {
                            id: values[0],
                            lat: parseFloat(values[2]),
                            lng: parseFloat(values[1]),
                            status: status[values[3]]
                        }
                        
                        // check for repeated gps coordinates, if found don't add to list
                        if (!ids.includes(data.id)) {
                            setIds(oldIds => [...oldIds, data.id]);
                            setDataStore(oldData => [...oldData, data]);
                            addMarkers(data.id, data.lng, data.lat, data.status)
                            console.log('inside if includes')
                        }
                    } else {
                        console.log('received invalid stringframe')
                    }
                } else {
                    console.log('received only html with no data')
                }
            })
            .catch(error => {
                console.log(error);
                ToastAndroid.show(`${error}`, ToastAndroid.SHORT);
            })
    }

    /*
    *
    * Function Name: 	addMarkers()
    * Input: 		id, lng, lat, status
    * Output: 		Markers
    * Logic: 		Saves marker to list of markers
    * Example Call:		addMarkers(3, 34.3434, 54.5454, 3)
    *
    */
    const addMarkers = (id, lng, lat, status) => {
        const marker = { id: id, lng: lng, lat: lat, status: status }
        setMarkers(oldMarkers => [...oldMarkers, marker]);
    }

   /*
    *
    * Function Name: 	PlotMarker
    * Input: 		data, key
    * Output: 		Returns markers that can be added to map
    * Logic: 		Creates a mapbox marker with popup
    * Example Call:		PlotMarker()
    *
    */ 
    const PlotMarkers = (data, key) => {
        return (
            <MapboxGL.PointAnnotation
                coordinate={[data.lng, data.lat]}
                id={`${key}`}
                key={`${key}`}
                onSelected = {() => rescued(data.id)}
            >
                <MapboxGL.Callout title={`Lng: ${data.lng}, Lat: ${data.lat}, State: ${data.status}`} />
            </MapboxGL.PointAnnotation>
        )
    }

    /*
    *
    * Function Name: 	rescued
    * Input: 		id of marker
    * Output: 		send id of marker to nodemcu
    * Logic: 		sends id of rescued marker to nodemcu
    * Example Call:		rescued(4)
    *
    */ 
    const rescued = (id) => {
        var requestOptions = {
            method: 'GET',
            redirect: 'follow',
            type: 'application/json'
        };

        fetch(`http://192.168.4.1/rescued?id=${id}`, requestOptions)
            .then(response => response.text())
            .then(text => text)
    }

    return (
        <>
            <MapboxGL.MapView
                style={styles.map}
                styleURL={mapType}
                zoomEnabled={true}
            >
                <MapboxGL.Camera
                    zoomLevel={16}
                    centerCoordinate={coordinates}
                />

                <MapboxGL.PointAnnotation
                    coordinate={[79.04905350623918, 21.007050226637872]}
                    id={`gs`}
                    draggable={true}
                >
                    <MapboxGL.Callout title={`Ground Station`} />
                    <View style={styles.gs} />
                </MapboxGL.PointAnnotation>
                {markers.map((e, k) => PlotMarkers(e, k))}
            </MapboxGL.MapView>
            <Button title="Plot Detections"
                onPress={() => {
                    setInterval(fetchData, 1000);
                    ToastAndroid.show('Plot Detections Clicked', ToastAndroid.SHORT);
                }} />
        </>
    );
}

const styles = StyleSheet.create({
    map: {
        flex: 1,
    },
    marker: {
        height: 20,
        width: 20,
        backgroundColor: '#00cccc',
        borderRadius: 50,
        borderColor: '#fff',
        borderWidth: 1
    },
    gs: {
        height: 15,
        width: 20,
        backgroundColor: '#00cccc',
        borderRadius: 50,
        borderColor: '#fff',
        borderWidth: 2
    }
})