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
        self.UAV = Crazyflie()
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
            

        if(len(self.available) > 0):
            self.UAV.open_link(self.available[0][0])
            while(self.UAV.is_connected() == False): time.sleep(0.1)
            self.MC = MotionCommander(self.UAV)
            #Create desired logging parameters
            self.logForUAV = LogConfig(name = "UAVLog", period_in_ms=1000)
            self.logForUAV.add_variable('pm.batteryLevel', 'float')
            self.logForUAV.add_variable('stateEstimate.x', 'float')
            self.logForUAV.add_variable('stateEstimate.y', 'float')
            #Add more variables here for logging as desired
            
                #with SyncLogger(SyncObject, self.logForUAV) as LogObject:
                #    self.UAVLogObject = LogObject
        
        #End of function

    def done(self):
        """
        Function: done
        Purpose: Close connection to UAV to terminate all threads running
        Inputs: none
        Outputs: none
        """
        self.UAV.close_link()
        self.connected = False
        
    def launch(self):
        """
        Function: launch
        Purpose: Instruct the UAV to takeoff from current position to the default height
        Inputs: none
        Outputs: none
        """
        self.connected == True
        self.MC.take_off()
        #End of function
        return

    def land(self):
        """
        Function: launch
        Purpose: Instruct the UAV to land on the ground at current position
        Inputs: none
        Outputs: none
        """
        self.MC.land()
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

        self.MC.move_distance(distanceX, distanceY, distanceZ, velocity)
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
            self.MC.turn_right(abs(degree))
        else:
            self.MC.turn_left(degree)
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
