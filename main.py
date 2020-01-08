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
    print("Attempting to connect to UAV")
    while(UAV == None):
        UAV = UAVController()
    print("UAV Connected, Initializing Landing Platform Controller")
    LPC = None
    while(LPC == None):
        LPC = LandingPlatformController(UAV)
    print("Landing Platform Controller Initialized")
    while(True):
        time.sleep(0.1)
    
if __name__ == "__main__":
    main()
