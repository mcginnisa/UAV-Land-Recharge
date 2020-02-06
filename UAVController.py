import logging
import time
import io

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.crazyflie.log import LogConfig, Log, LogVariable
        
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
        self._recentDataPacket = None
        self._receivingDataPacket = False
        
        #Setup logging objects/constants
        rootLog = logging.getLogger()
        rootLog.setLevel(logging.INFO)

        #Setup battery stream handler
        self._batteryCaptureString = io.StringIO()
        self._batteryStreamHandler = logging.StreamHandler(self._batteryCaptureString)
        self._batteryStreamHandler.setLevel(logging.INFO)
        rootLog.addHandler(self._batteryStreamHandler)
        
        #Setup height stream handler
        self._heightCaptureString = io.StringIO()
        self._heightStreamHandler = logging.StreamHandler(self._heightCaptureString)
        self._heightStreamHandler.setLevel(logging.INFO)
        rootLog.addHandler(self._heightStreamHandler)
        
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
            self.UAVLogConfig = LogConfig(name = "UAVLog", period_in_ms=100)
            self.UAVLogConfig.add_variable('pm.batteryLevel', 'float')
            self.UAVLogConfig.add_variable('stateEstimate.x', 'float')
            self.UAVLogConfig.add_variable('stateEstimate.y', 'float')
            #Add more variables here for logging as desired

            self.UAV.log.add_config(self.UAVLogConfig)
            if(self.UAVLogConfig.valid):
                self.UAVLogConfig.data_received_cb.add_callback(self._getUAVDataPacket)
                self.UAVLogConfig.start()
            else:
                logger.warning("Could not setup log configuration")
 
        
        #End of function

    def done(self):
        """
        Function: done
        Purpose: Close connection to UAV to terminate all threads running
        Inputs: none
        Outputs: none
        """
        self.UAVLogConfig.stop()
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
            locDeg = 0
            #self.MC.turn_right(abs(degree))
            for _ in range(1,int(abs(degree)/1)):
                locDeg += 1
                self.MC.turn_right(1)
            self.MC.turn_right(abs(degree)-locDeg)
        else:
            print("UC: rotate - Going Left")
            self.MC.turn_left(abs(degree))

        #Delay by 1 second, to allow for total rotation time
        time.sleep(1)
        return
        
    def getBatteryLevel(self):
        """
        Function: getBatteryLevel
        Purpose: A function that reads the UAV battery level from a IOStream
        Inputs: none
        Outputs: none
        Description: 
        """
        retVal = None
        if(self._recentDataPacket != None and self._receivingDataPacket == False):
            retVal = self._recentDataPacket["pm.batteryLevel"]
            
        return retVal

    def getHeight(self):
        """
        Function: getCurrentHeight
        Purpose: A function that reads the UAV height from a IOStream
        Inputs: none
        Outputs: none
        Description: 
        """
        retVal = None
        if(self._recentDataPacket != None and self._receivingDataPacket == False):
            retVal = self._recentDataPacket["stateEstimate.x"]

        return retVal
        
    def _getUAVDataPacket(self, ident, data, logconfig):
        """
        Function: getUAVDataPacket
        Purpose: Process a data packet received from the UAV
        Inputs: ident -
                data -
                logconfig -
        Outputs: None
        Description: A user should never call this function.
        """
        self._receivingDataPacket = True
        self._recentDataPacket = data
        self._receivingDataPacket = False
