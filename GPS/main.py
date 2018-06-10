import gpsd
import json
import time

waitTime = 10  # set polling time to once every 10 sec

# connects to gps, should be fixed to support connection issues
class gpsCl():
    # TODO: set up data fields for wanted information
    def __init__(self):
        gpsd.connect()
        self.position = (0, 0)
        self.movement = {'speed': 0, 'track': 0, 'climb' : 0}

    def pollData(gps):  # polls all data and returns wanted data in json formatted txt file
        dataFile = open('gpsData.txt', 'w')
        packet = gpsd.get_current()
        gps.position = packet.position()
        gps.movement = packet.movement()
        # TODO: use packet.XXXX to get desired data fields

        dataFile.write(json.dumps(gps))
        dataFile.close()

gps = gpsCl()

while(True):
    gps.pollData()
    time.sleep(waitTime)
