from UAVController import UAVController
from LandingPlatformController import LandingPlatformController

import signal
import sys
import time

LPC = None

def signalHandler(sig, frame):
    global LPC
    if(LPC != None):
        LPC.done()
    
    sys.exit(0)

def main():
    global LPC
    UAV = None
    signal.signal(signal.SIGINT, signalHandler)
    print("MAIN: Attempting to connect to UAV")
    while(UAV == None):
        UAV = UAVController()
    print("MAIN: UAV Connected, Initializing Landing Platform Controller")        
    LPC = None
    settingsArray = dict()
    settingsArray['uav'] = UAV
    while(LPC == None):
        LPC = LandingPlatformController(settings=settingsArray, debug=True)
    print("MAIN: Landing Platform Controller Initialized")
    #LPC._sendMovement(0,0,0.8)
    #while(True):
    #    LPC._uavInBoundary(LPC._getUAVPosition())
    LPC.engageFlightRoutine()
    LPC.done()

if __name__ == "__main__":
    main()
