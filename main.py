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
    LPC = None
    while(LPC == None):
        LPC = LandingPlatformController(UAV)
    print("MAIN: Landing Platform Controller Initialized")
    LPC.engageFlightRoutine()
    #LPC._sendMovement(0, 0, 0.5)
    #print("MAIN:", LPC._uavInFrame())
    #while(LPC._uavInFrame()):
    #    LPC._sendMovement(0.1, 0, 0)
        #LPC._sendMovement(0.5, 0.5, 0)
        #print("MAIN:", LPC._getUAVPosition())
        #LPC._sendMovement(-0.5, -0.5, 0)
        #print("MAIN:", LPC._getUAVPosition())

        
        #LPC._alignUAV()
        
    LPC.done()
    #UAV.launch()
    #while(True):
    #    print("MAIN:", LPC._calculateOffset())
    #    time.sleep(0.5)
    
if __name__ == "__main__":
    main()
