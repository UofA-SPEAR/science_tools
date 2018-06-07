/*
# This Sample code is for testing the UV Sensor .
 #Connection:
     VCC‐5V
     GND‐GND
     OUT‐Analog pin 0
 */
  

#include <Arduino.h>

#define ANAPIN 0

void setup(){
	init();
	Serial.begin(9600);
}

int main(){

	setup();

	int sensorValue;
	int analogValue = analogRead(ANAPIN);

	while(true){

		analogValue = analogRead(ANAPIN);

		if(analogValue < 20){
		sensorValue = 0;
	}
		else{
			sensorValue = 0.05*analogValue-1;
		}

		Serial.println(sensorValue);
		delay(200);
	}

	
}



