#!/usr/bin/env python

"""
SHT1x_lib.py
Created on Fri Jun 01 10:32:33 2018
Author: Tanner Cumiskey

Description:
This library is to be used to read data from the Sensirion SHT1x Humidity 
and Temperature Sensor Family.

It uses the RPi.GPIO library which must be downloaded ahead of time

It requires the following predifined variables:
data_pin: The number of the physical data pin in use [int]
sck_pin:  The number of the physical data pin in use [int]
resolution: 'HIGH' for 14bit temperature and 12bit humidity
            'LOW' for 12bit temperature and 8bit humidity [string]
heater: 'ON' if the sensors on board heater is to be used
        'OFF' if the sensors on board heater is not used [string]
vdd: the voltage applied to the sensor either 5, 4, 3.5, 3, 2.5 [int]

Functions:
_set_status_register
_read_temperature
_read_humidity
_calculate_dew_point

Important Information:
Read temperature before relative humidity, as the humidity calculation relies
on the temperature.

The data line requires a 1k resistor
"""

import time
import math

try:
    import RPi.GPIO as GPIO
except ImportError:
    print('Could not import the RPi.GPIO package (http://pypi.python.org/pypi/RPi.GPIO). Exiting.')

# Set the mode of the RPi.GPIO library
GPIO.setmode(GPIO.BOARD)

# Variables containing binary commands to be sent to the sensor
TEMPERATURE = [0,0,0,0,0,0,1,1]
HUMIDITY = [0,0,0,0,0,1,0,1]
READ_STATUS = [0,0,0,0,0,1,1,1]
WRITE_STATUS = [0,0,0,0,0,1,1,0]
SOFT_RESET = [0,0,0,1,1,1,1,0]

# Delay variables
delay_100ns = 100e-9
delay_10ms = 0.01
"""
###########################################################
# test section
data_pin = 33
sck_pin = 13
resolution = 'HIGH'
heater = 'OFF'
vdd = 5

#need to uncomment main at bottom of code to use this test section

def main():
	time.sleep(1.0)
	#_set_status_register(data_pin,sck_pin,resolution,heater)
	time.sleep(1.0)

	while 1:
		temp = _read_temperature(data_pin,sck_pin,vdd,resolution)
		hum = _read_humidity(data_pin,sck_pin,vdd,resolution,temp)
		print "Temperature: %.2f Celsius"% temp 
		print "Humidity: %.2f %%\n" % hum 
		time.sleep(1.0)

##########################################################
"""

"""
Sets status register

Inputs:
data_pin: The number of the physical data pin in use [int]
sck_pin:  The number of the physical data pin in use [int]
resolution: 'HIGH' for 14bit temperature and 12bit humidity
            'LOW' for 12bit temperature and 8bit humidity [string]
heater: 'ON' if the sensors on board heater is to be used
        'OFF' if the sensors on board heater is not used [string]

Outputs:

"""
def _set_status_register(data_pin,sck_pin,resolution,heater):
    if (resolution == 'HIGH') & (heater == 'OFF'):
        status = [0,0,0,0,0,0,1,0]
    elif (resolution == 'HIGH') & (heater == 'ON'):
        status = [0,0,0,0,0,1,1,0]
    elif (resolution == 'LOW') & (heater == 'ON'):
        status = [0,0,0,0,0,1,1,1]
    elif (resolution == 'LOW') & (heater == 'OFF'):
        status = [0,0,0,0,0,0,1,1]
    
    _start_transmission(data_pin,sck_pin)
    _send_command(data_pin,sck_pin,WRITE_STATUS)
    
    _send_byte(data_pin,sck_pin,status)
    _get_ack(data_pin,sck_pin)
    return

"""
Reads the temperature value of the sensor and returns a value in degrees celsius.

Inputs:
data_pin: The number of the physical data pin in use [int]
sck_pin:  The number of the physical data pin in use [int]
resolution: 'HIGH' for 14bit temperature and 12bit humidity
            'LOW' for 12bit temperature and 8bit humidity [string]
vdd: the voltage applied to the sensor either 5, 4, 3.5, 3, 2.5 [int]

Outputs:
temperature_celsius: The temperate value read from the sensor [float, celsius]
"""
def _read_temperature(data_pin,sck_pin,vdd,resolution):

    _send_command(data_pin,sck_pin,TEMPERATURE)
    _wait_for_measurement(data_pin)
    temperature_bin = _read_measurement(data_pin,sck_pin)
    
    temperature_celsius = _convert_celsius(temperature_bin,vdd,resolution)
    
    return temperature_celsius

"""
Reads the humidity value of the sensor and returns a value in percentage [0-100%].

Inputs:
data_pin: The number of the physical data pin in use [int]
sck_pin:  The number of the physical data pin in use [int]
resolution: 'HIGH' for 14bit temperature and 12bit humidity
            'LOW' for 12bit temperature and 8bit humidity [string]
vdd: the voltage applied to the sensor either 5, 4, 3.5, 3, 2.5 [int]
temperature: The temperate value previously read from the sensor [float, celsius]

Outputs:
humidity: The humidity read from the sensor [float, %]
"""
def _read_humidity(data_pin,sck_pin,vdd,resolution,temp):
    _send_command(data_pin,sck_pin,HUMIDITY)
    _wait_for_measurement(data_pin)
    humidity_bin = _read_measurement(data_pin,sck_pin)
    
    humidity = _convert_humidity(humidity_bin,vdd,resolution,temp)
    
    return humidity

"""
Sends the sensor information regarding what action to take next

Inputs:
data_pin: The number of the physical data pin in use [int]
sck_pin:  The number of the physical data pin in use [int]
command: The command code that will be sent to the sensor [bin]

Outputs:

"""
def _send_command(data_pin,sck_pin,command):
    _start_transmission(data_pin,sck_pin)
    _send_byte(data_pin,sck_pin,command)
    _get_ack(data_pin,sck_pin)

"""
Sends the sensor the Transmission Start sequence

Inputs:
data_pin: The number of the physical data pin in use [int]
sck_pin:  The number of the physical data pin in use [int]

Outputs:

"""
def _start_transmission(data_pin,sck_pin):
    GPIO.setup(data_pin,GPIO.OUT)
    GPIO.setup(sck_pin,GPIO.OUT)
    
    GPIO.output(data_pin,GPIO.HIGH)
    GPIO.output(sck_pin,GPIO.HIGH)
    time.sleep(delay_100ns)
    GPIO.output(data_pin,GPIO.LOW)
    GPIO.output(sck_pin,GPIO.LOW)
    time.sleep(delay_100ns)
    GPIO.output(sck_pin,GPIO.HIGH)
    time.sleep(delay_100ns)
    GPIO.output(data_pin,GPIO.HIGH)
    GPIO.output(sck_pin,GPIO.LOW)
    time.sleep(delay_100ns)

"""
Sends the sensor a byte of information

Inputs:
data_pin: The number of the physical data pin in use [int]
sck_pin:  The number of the physical data pin in use [int]
command: The command that will be sent to the sensor [bin]

Outputs:

"""
def _send_byte(data_pin,sck_pin,command):
    GPIO.setup(data_pin, GPIO.OUT)
    GPIO.setup(sck_pin, GPIO.OUT)
    
    for element in command:
	if element == 1:
            GPIO.output(data_pin,GPIO.HIGH)
	elif element == 0:
	    GPIO.output(data_pin,GPIO.LOW)
        GPIO.output(sck_pin,GPIO.HIGH)
        time.sleep(delay_100ns)
        GPIO.output(sck_pin,GPIO.LOW)
        time.sleep(delay_100ns)

"""
Waits to receive the ACK code from the sensor, meaning the sensor has received
the data sent

Inputs:
data_pin: The number of the physical data pin in use [int]
sck_pin:  The number of the physical data pin in use [int]

Outputs:

"""
def _get_ack(data_pin,sck_pin):
    GPIO.setup(data_pin,GPIO.IN)
    GPIO.setup(sck_pin,GPIO.OUT)
    
    GPIO.output(sck_pin,GPIO.HIGH)
    time.sleep(delay_100ns)
    
    while 1:
	ack = GPIO.input(data_pin)
        if ack == GPIO.LOW:
            break
    
    GPIO.output(sck_pin,GPIO.LOW)
    time.sleep(delay_100ns)

    ack = GPIO.input(data_pin)
    if ack == GPIO.LOW:
	print "not collecting data"


"""
Waits for the data line to be low, meaning the sensor has completed
taking measurements

Inputs:
data_pin: The number of the physical data pin in use [int]

Outputs:

"""
def _wait_for_measurement(data_pin):
    GPIO.setup(data_pin,GPIO.IN)
    
    while 1:
        time.sleep(delay_10ms)
        ready = GPIO.input(data_pin)
        if ready == GPIO.LOW:
            break

"""
Reads the data from the sensor, 2bytes

Inputs:
data_pin: The number of the physical data pin in use [int]
sck_pin:  The number of the physical data pin in use [int]

Outputs:
value_bin: The data collected form the sensor [bin]
"""
def _read_measurement(data_pin,sck_pin):
    value_bin = _get_byte(data_pin,sck_pin)
    value_bin <<= 8
    
    _send_ack(data_pin,sck_pin)
    
    value_bin |= _get_byte(data_pin,sck_pin)
    _end_transmission(data_pin,sck_pin)
    print value_bin
    return value_bin

"""
Collects one byte of data from the sensor

Inputs:
data_pin: The number of the physical data pin in use [int]
sck_pin:  The number of the physical data pin in use [int]

Outputs:
data: One byte of data collected from the sensor [bin]
"""
def _get_byte(data_pin,sck_pin):
    GPIO.setup(data_pin,GPIO.IN)
    GPIO.setup(sck_pin,GPIO.OUT)
    
    data = 0b00000000
    for i in range(8):
        GPIO.output(sck_pin,GPIO.HIGH)
        time.sleep(delay_100ns)
        data |= GPIO.input(data_pin) << (7-i)
        GPIO.output(sck_pin,GPIO.LOW)
        time.sleep(delay_100ns)
        
    return data

"""
Sends the ACK code to the sensor, meaning that the MCU has the data

Inputs:
data_pin: The number of the physical data pin in use [int]
sck_pin:  The number of the physical data pin in use [int]

Outputs:

"""
def _send_ack(data_pin,sck_pin):
    GPIO.setup(data_pin,GPIO.OUT)
    GPIO.setup(sck_pin,GPIO.OUT)
    
    GPIO.output(data_pin,GPIO.HIGH)
    GPIO.output(data_pin,GPIO.LOW)
    GPIO.output(sck_pin,GPIO.HIGH)
    time.sleep(delay_100ns)
    GPIO.output(sck_pin,GPIO.LOW)

def _end_transmission(data_pin,sck_pin):
    GPIO.setup(data_pin,GPIO.OUT)
    GPIO.setup(sck_pin,GPIO.OUT)

    GPIO.output(data_pin,GPIO.HIGH)
    GPIO.output(sck_pin,GPIO.HIGH)
    time.sleep(delay_100ns)
    GPIO.output(sck_pin,GPIO.LOW)
    time.sleep(delay_100ns)

"""
Converts binary sensor data to a degrees celsius

Inputs:
data: data collected from the sensor [bin]
vdd: the voltage applied to the sensor either 5, 4, 3.5, 3, 2.5 [int]
resolution: 'HIGH' for 14bit temperature and 12bit humidity
            'LOW' for 12bit temperature and 8bit humidity [string]

Outputs:
temperature_celsius: The calculated temperature [float, celsius]
"""
def _convert_celsius(data,vdd,resolution):
    
    if resolution == 'HIGH':
        d2 = 0.01
    elif resolution == 'LOW':
        d2 = 0.04
    
    if vdd == 5:
        d1 = -40.1
    elif vdd == 4:
        d1 = -39.8
    elif vdd == 3.5:
        d1 = -39.7
    elif vdd == 3:
        d1 = -39.6
    elif vdd == 2.5:
        d1 = -39.4
    
    temperature_celsius = d1 + (d2*data)
    
    return temperature_celsius

"""
Converts binary sensor data to a relative humidity

Inputs:
data: data collected from the sensor [bin]
vdd: the voltage applied to the sensor either 5, 4, 3.5, 3, 2.5 [int]
resolution: 'HIGH' for 14bit temperature and 12bit humidity
            'LOW' for 12bit temperature and 8bit humidity [string]
temperature: previously calculated temperature [float, celsius]

Outputs:
humidity: The calculated relative humidity [float, %]
"""
def _convert_humidity(data,vdd,resolution,temp):
    
    if resolution == 'HIGH':
        t1 = 0.01
        t2 = 0.00008
        c1 = -2.0468
        c2 = 0.0367
        c3 = -1.5955e-6
    elif resolution == 'LOW':
        t1 = 0.01
        t2 = 0.00128
        c1 = -2.0468
        c2 = 0.5872
        c3 = -4.0845e-4
    
    humidity_linear = c1+ (c2*data) + (c3*(data**2))
    humidity = ((temp-25)*(t1+(t2*data)))+humidity_linear
    
    return humidity

"""
Calculates the dew point

Inputs:
humidity: The previously calculated relative humidity [float, %]
temperature: previously calculated temperature [float, celsius]

Outputs:
dew_point: The calculated dew_point [float, celsius]
"""
def _calculate_dew_point(temp,humidity):
    
    if temp <= 0:
        Tn = 243.12
        m = 17.62
    else:
        Tn = 272.62
        m = 22.46
    
    numerator = math.log(humidity/100.0)+((m*temp)/(Tn+temp))
    denominator = m-math.log(humidity/100.0)-((m*temp)/(Tn+temp))
    dew_point = Tn * numerator / denominator
    
    return dew_point

#main()
