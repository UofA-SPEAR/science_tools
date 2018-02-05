/**
 * ReadSHT1xValues
 *
 * Read temperature and humidity values from an SHT1x-series (SHT10,
 * SHT11, SHT15) sensor.
 *
 * Copyright 2009 Jonathan Oxer <jon@oxer.com.au>
 * www.practicalarduino.com
 */

#include <SHT1x.h>
#include <Arduino.h>

// Specify data and clock connections and instantiate SHT1x object
#define dataPin  10
#define clockPin 11
SHT1x sht1x(dataPin, clockPin);

void setup()
{
  init();
  Serial.begin(9600); // Open serial connection to report values to host
  pinMode(dataPin,INPUT);
  pinMode(clockPin,INPUT);
  Serial.println("Starting up");
  Serial.flush();
}

int main()
{


  float temp_c;
  float temp_f;
  float humidity;
  while(true){
      // Read values from the sensor
    temp_c = sht1x.readTemperatureC();
    temp_f = sht1x.readTemperatureF();
    humidity = sht1x.readHumidity();

    // Print the values to the serial port
    Serial.print("Temperature: ");
    Serial.print(temp_c, DEC);
    Serial.print("C / ");
    Serial.print(temp_f, DEC);
    Serial.print("F. Humidity: ");
    Serial.print(humidity);
    Serial.println("%");

    delay(2000);
  }
  

  Serial.end();
  return 0;
}
