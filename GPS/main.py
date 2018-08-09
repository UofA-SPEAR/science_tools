import gpsd
import json
import time
import RPi.GPIO as GPIO

waitTime = 10  # set polling time to once every 10 sec

#Set up GPIO pins for visual feedback
GPIO.setmode(GPIO.BOARD)
GPIO.setup([11, 13], GPIO.OUT)

#Clear data file for next run
dataFile = open('gpsData2.txt', 'w')
dataFile.write('')
dataFile.close()

# Class connecting to gpsd daemon.
class gpsCl():
    def __init__(self):
        for i in range(0, 2):
            try:
                #Try to connect to gpsd daemon
                gpsd.connect()
                self.mode = 0
            except UserError as er:
                #Most often, failed because the GPS was not active. Give the gps device time to 'wake up' and try to connect again
                print(er.msg)
                print('Failed attempt '+str(i)+' of 2. Retrying in 10 seconds...')
                time.sleep(10)
            except ConnectionRefusedError:
                #Most often, failed because the gpsd daemon was not running at all. Critical Failure, terminate the whole program and get that running before trying again.
                self.mode = -1
                break
        self.lastValidPacket = None
        self.position = [0, 0]
        #File that this class instance should write to as long as it runs
        self.dataFile = open('gpsData2.txt', 'a')

    #Polls the GPS for a data packet, stores the needed data in fields of the class
    def pollData(gps):
        packet = gpsd.get_current()
        print(packet.mode)
        gps.mode = packet.mode
        if packet.mode == 1:
            GPIO.output([11, 13], [1, 0])
        elif packet.mode >= 2:
            GPIO.output([11, 13], [0, 1])
            gps.position = packet.position()
        else:
            GPIO.output([11, 13], 0)
        #if gps.lastValidPacket is not None:
        
        gps.dataFile.write(str(gps.mode)+' '+json.dumps(gps.position)+'\n')
        
        #If the gps still holds a signal and the packet data is up-to-date, save the polled data
        #TODO: Check for data validity
        gps.lastValidPacket = packet

    #TODO: Implement closable so that the gps class may be closed like a file, to handle the gpsd connection (if it needs it, this is yet to be determined) and to close the associated dataFile
    def close(gps):
        gps.dataFile.close()

gps = gpsCl()

try:
    if gps.mode == -1:
        raise KeyboardInterrupt()

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
    gps.close()
    GPIO.cleanup()
