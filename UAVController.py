import logging
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.utils.callbacks import Caller
from cflib.positioning.motion_commander import MotionCommander
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.crazyflie.log import LogConfig
    
class UAVController():
    
    def __init__(self):
        self.timeout = True
        self.available = []
        self.UAV = None
        self.param = None
        self.connected = False
        
        cflib.crtp.init_drivers()
        foundUAV = False

        #Attempt to locate UAV by scanning available interface
        for _ in range(0,500):
            if(len(self.available) > 0):
                self.timeout = False
                break #If a UAV is found via scanning, break out of this loop
            else:
                self.available = cflib.crtp.scan_interfaces()
                print("Still searching...", _)
            
        self.UAV = Crazyflie()
        
        if(len(self.available) > 0):
            self.logForUAV = LogConfig(name = "UAVLog", period_in_ms=1000)
            self.logForUAV.add_variable('pm.batteryLevel', 'float')
            self.logForUAV.add_variable('stateEstimate.x', 'float')
            self.logForUAV.add_variable('stateEstimate.y', 'float')
            """Add more variables here for logging as desired"""
            self.UAVLog = MotionCommander(SyncLogger(SyncCrazyflie(self.available[0][0]), self.logForUAV))
            
        #End of function
    
    def launch(self):
        """
        Function: launch
        Purpose: manually connect the UAV so that any automated processes are avoided on system startup
        Inputs: none
        Outputs: none
        """
        if(self.timeout == False):
            #self.UAV = MotionCommander(self.UAVLog)
            self.connected = True
        else:
            self.connected = False #Send to logs that a connection failed
            
        #End of function
        return
    
    def move(self, distanceX, distanceY, distanceZ, velocity):
        """
        Function: up
        Purpose: A wrapper function to instruct an UAV to move <x, y, z> distance from current point
        Inputs: distance - a floating point value distance in meters
                velocity - a floating point value velocity in meters per second
        Outputs: none
        """
        if(self.connected == False):
            self.launch()

        self.UAV.move_distance(distanceX, distanceY, distanceZ, velocity)
        #End of function
        return

    def rotate(self, degree):
        """
        Function: rotate
        Purpose: A wrapper function to instruct an UAV to rotate
        Inputs: degree - a floating point value in degrees
        Outputs: none
        """
        if(degree < 0):
            self.UAV.turn_right(abs(degree))
        else:
            self.UAV.turn_left(degree)
        #End of function
        return
        
    def getBatteryLevel(self):
        """
        Function: getBatteryLevel
        Purpose: A wrapper function to grab the battery voltage
        Inputs: degree - a floating point value in degrees
        Outputs: none
        """
        
        #End of function
        return

if True:
    UAV = UAVController()
    print("TESTED")
    UAV.launch()
    print("TRIED AND TRUE")
