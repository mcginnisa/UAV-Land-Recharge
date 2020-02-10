from UAVController import UAVController
from LandingPlatformController import LandingPlatformController

import signal
import sys
import time

LPC = None

def signallHandler(sig, frame):
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
    while(LPC == None):
        LPC = LandingPlatformController(UAV, debug=True)
    print("MAIN: Landing Platform Controller Initialized")
    LPC.engageFlightRoutine()
    LPC.done()

if __name__ == "__main__":
    main()
