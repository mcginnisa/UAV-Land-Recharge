import logging
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.crazyflie.log import LogConfig
        
class UAVController():

    def __init__(self):
        """
        Function: __init__
        Purpose: Initialize all necessary UAV functionality
        Inputs: none
        Outputs: none
        """

        cflib.crtp.init_drivers()
     
        self.timeout = True
        self.available = []
        self.UAV = Crazyflie()
        self.param = None
        self.airborne = False
        
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
            self.UAVLogConfig = LogConfig(name = "UAVLog", period_in_ms=1000)
            self.UAVLogConfig.add_variable('pm.batteryLevel', 'float')
            self.UAVLogConfig.add_variable('stateEstimate.x', 'float')
            self.UAVLogConfig.add_variable('stateEstimate.y', 'float')
            #Add more variables here for logging as desired
            

        
        #End of function

    def done(self):
        """
        Function: done
        Purpose: Close connection to UAV to terminate all threads running
        Inputs: none
        Outputs: none
        """
        self.UAV.close_link()
        self.airborne = False
        return
        
    def launch(self):
        """
        Function: launch
        Purpose: Instruct the UAV to takeoff from current position to the default height
        Inputs: none
        Outputs: none
        """
        self.airborne = True
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
        Function: move
        Purpose: A wrapper function to instruct an UAV to move <x, y, z> distance from current point
        Inputs: distance - a floating point value distance in meters
                velocity - a floating point value velocity in meters per second
        Outputs: none
        """
        if(self.airborne == False):
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
        
        if(self.airborne == False):
            self.launch()
        
        if(degree < 0):
            print("UC: rotate - Going Right")
            self.MC.turn_right(abs(degree))
        else:
            print("UC: rotate - Going Left")
            self.MC.turn_left(abs(degree))

        #Delay by 1 second, to allow for total rotation time
        time.sleep(1)
        return
        
    def getBatteryLevel(self):
        """
        Function: getBatteryLevel
        Purpose: A wrapper function to grab the battery voltage
        Inputs: none
        Outputs: none
        """
        retVal = []
        with SyncLogger(self.UAV, self.UAVLogConfig) as LogObject:
            self.UAVLogObject = LogObject
            retVal = LogObject.next()[1].get('pm.batteryLevel')
                            
        #End of function
        return retVal
