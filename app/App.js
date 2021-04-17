/*
*
* Project Name: 	FALON drone - stranded people detection using UAV
* Author List: 		Sarang Chouguley
* Filename: 	App.js
* Functions: 		App
* Global Variables:	None
*
*/

import { StatusBar } from 'expo-status-bar';
import React, { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import MapboxGL from '@react-native-mapbox-gl/maps';
import CustomMap from './src/customMap';

/*
*
* Function Name: 	App
* Input: 		None
* Output: 		Returns Main page of app
* Logic: 		None
* Example Call:		App()
*
*/
export default function App() {

  return (
    <View style={styles.page}>
      <View style={styles.container}>
        <CustomMap/>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  page: {
    flex: 1,
  },
  container: {
    height: '100%',
    width: '100%',
    backgroundColor: 'blue',
  },
});
