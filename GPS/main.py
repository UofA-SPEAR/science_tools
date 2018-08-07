import gpsd
import json
import time
import RPi.GPIO as GPIO

waitTime = 10  # set polling time to once every 10 sec

GPIO.setmode(GPIO.BOARD)
GPIO.setup([11, 13], GPIO.OUT)

dataFile = open('gpsData2.txt', 'w')
dataFile.write('')
dataFile.close()

# connects to gps, should be fixed to support connection issues
class gpsCl():
    def __init__(self):
        gpsd.connect()
        self.mode = -1
        self.position = (0, 0)

    def pollData(gps):  # polls all data and returns wanted data in json formatted txt file
        dataFile = open('gpsData2.txt', 'a')
        packet = gpsd.get_current()
        gps.mode = packet.mode
        print(packet.mode)
        if packet.mode == 1:
            GPIO.output([11, 13], [1, 0])
        elif packet.mode >= 2:
            GPIO.output([11, 13], [0, 1])
            gps.position = packet.position()
        else:
            GPIO.output([11, 13], 0)
        # TODO: use packet.XXXX to get desired data fields

        dataFile.write(str(gps.mode)+' '+json.dumps(gps.position)+'\n')
        dataFile.close()

gps = gpsCl()

try:
    while(True):
        gps.pollData()
        if gps.mode == 1:
            pinsToPulse = 11
        elif gps.mode >= 2:
            pinsToPulse = 13
        else:
            pinsToPulse = [11, 13]
        GPIO.output(pinsToPulse, 0)
        time.sleep(0.1)
        GPIO.output(pinsToPulse, 1)
        time.sleep(0.1)
        GPIO.output(pinsToPulse, 0) 
        
        if pinsToPulse == 11 or pinsToPulse == 13:
            GPIO.output(pinsToPulse, 1)
        time.sleep(waitTime)
except KeyboardInterrupt:
    GPIO.cleanup()
