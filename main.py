from UAVController import UAVController
from LandingPlatformController import LandingPlatformController

import signal
import sys
import time

UAV = None

def signalHandler(sig, frame):
    global UAV
    if(UAV != None):
        UAV.land()
        UAV.done()
    sys.exit(0)

def main():
    global UAV
    signal.signal(signal.SIGINT, signalHandler)
    print("MAIN: Attempting to connect to UAV")
    while(UAV == None):
        UAV = UAVController()
    print("MAIN: UAV Connected, Initializing Landing Platform Controller")
#    while(True):
#        UAV.getBatteryLevel()
#        time.sleep(1)
    #print(UAV.getBatteryLevel())
        
    LPC = None
    while(LPC == None):
        LPC = LandingPlatformController(UAV)
    print("MAIN: Landing Platform Controller Initialized")
    LPC.engageFlightRoutine()
    LPC.done()

if __name__ == "__main__":
    main()