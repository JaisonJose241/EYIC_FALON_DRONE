/*
* Project Name:   FALON drone - stranded people detection using UAV
* Author List:    Jaison Jose
* Filename:       Ground_response_team
* Functions:      handleRoot(), checkClient(), setup(), loop()
* Global Variables: APSSID, APPSK, data, message, address, receive_from_app
*
*/
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>

// defining constants for SSID and passwords
#ifndef APSSID
#define APSSID "ESPap_GS"
#define APPSK  ""
#endif

/* Set these to your desired credentials. */
const char *ssid = APSSID;
const char *password = APPSK;
char* receive_from_app;

// starting server on port 80
ESP8266WebServer server(80);
//starting client on same server
WiFiClient client = server.available();

// nRF object call and initializing the pins
RF24 radio(D4, D8); // CE, CSN
// data variable for storing data from nRF
char data[20] = "";
String message;

// address of nRF for accurate data transfer and uniques ID of nRF
const byte address[6] = "10001";

/*
* Function Name:  handleRoot
* Input:          None
* Output:         None
* Logic:          takes the global data and sends it over server in said format
* Example Call:   handleRoot()
*
*/
void handleRoot() {
  message = "<h1><br><p>"+String(data)+"</p></h1>";
  // sending in text/html format at 200: OK status mode
  server.send(200, "text/html", message);
  Serial.println("SENDING>>");
}

/*
* Function Name:  checkClient
* Input:          None
* Output:         returns the value got after the URL if any
* Logic:          checks for data
* Example Call:   checkClient()
*/
String checkClient()
{ //wait till client is available
  while(!client.available()) delay(1); 
  // read the string until carriage return is not detected
  String request = client.readStringUntil('\r');

  // remove the last 9 unwanted characters
  request.remove(request.length()-9,9);
  
  return request;
}

/*
* Function Name:  setup
* Input:          None
* Output:         None
* Logic:          initiallizes serial, radio and wifi
* Example Call:   calls automatically by arduino compiler as one time run in main
*/
void setup() {
  //serial begins at 9600 baud rate
  Serial.begin(9600);

  // setting the apt minimum timeout for serial to cop-up with nRF
  // delay problem in transmission
  Serial.setTimeout(190);

  //start radio at address and max power
  radio.begin();
  radio.openReadingPipe(0, address);
  radio.setPALevel(RF24_PA_MAX);
  radio.startListening();

  // start Aaccess Point at ssid and password
  WiFi.softAP(ssid, password);
  IPAddress myIP = WiFi.softAPIP();

  //serial print the IP address
  Serial.print("AP IP address: ");
  Serial.println(myIP);   

  //server on and calls the handleRoot function
  server.on("/", handleRoot);
  server.begin();
}

/*
* Function Name:  loop
* Input:          None
* Output:         None
* Logic:          reads the data from nRF, handles server update, sends data from app to nRF
* Example Call:   calls automatically by arduino compiler as while loop in main
*/
void loop() {
    //handle client
    server.handleClient();
    // read fro data from nRF
    radio.read((uint8_t*)&data, 26);  

    //print that data on serial monitor
    Serial.print("Data = ");
    Serial.print(data);

    //stop listening so that transmission from nRF can start
    radio.stopListening(); 
    //receive data from app
    receive_from_app = (char*)checkClient().c_str(); 
    //send the data through nRF
    radio.write((uint8_t*)receive_from_app, strlen(receive_from_app));  
    // continue listening
    radio.startListening(); 
    delay(100);
  }
