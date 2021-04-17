/*
* Project Name:   FALON drone - stranded people detection using UAV
* Author List:    Jaison Jose
* Filename:       Remote_response_team
* Functions:      handleRoot(), checkClient(), setup(), loop()
* Global Variables: APSSID, APPSK, data, message, address, receive_from_app
*
*/
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

// nRF object call and initializing the pins
RF24 radio(D4, D8); // CE, CSN       
// data variable for storing data from nRF  
const byte address[6] = "10001";     

// data for recieving data from software and transmit over nRF
// from_appto read the nRF values and give to the Serial monitor
// hello and hello_dup is to repeat the last received message from serial monitor
char* data, from_app;
String hello, hello_dup;

/*
* Function Name:  setup
* Input:          None
* Output:         None
* Logic:          initiallizes serial, radio
* Example Call:   calls automatically by arduino compiler as one time run in main
*/
void setup() { 

  //start radio at address and max power
  radio.begin();
  radio.openWritingPipe(address); //Setting the address where we will send the data
  radio.setPALevel(RF24_PA_MAX);  //You can set it as minimum or maximum depending on the distance between the transmitter and receiver.
  radio.stopListening();          //This sets the module as transmitter
  // Begin Serial communication at a baudrate of 9600:
  Serial.begin(9600);
  // setting the apt minimum timeout for serial to cop-up with nRF
  // delay problem in transmission  
  Serial.setTimeout(190);

  
}
void loop() {
  //read the serial monitor until new line
  hello = Serial.readStringUntil('\n');

  // stores the value if not blank and repeats the transmission
  if(hello == ""){
    hello = hello_dup;
  }
  else{
    hello_dup = hello;
  }
  data = (char*)hello.c_str();
  // write the data over nRF
  radio.write((uint8_t*)data, strlen(data));

  // start listening to read the nRF values from app
  radio.startListening(); 
  radio.read((uint8_t*)&from_app, 26); 
  Serial.print(from_app);
  delay(100)

  //continue the transmission
  radio.stopListening(); 

}
