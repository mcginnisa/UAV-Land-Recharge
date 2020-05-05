"""                                                    

      .o.       ooooooooo.         .o.       oooooo     oooo 
     .888.      `888   `Y88.      .888.       `888.     .8'  
    .8"888.      888   .d88'     .8"888.       `888.   .8'   
   .8' `888.     888ooo88P'     .8' `888.       `888. .8'    
  .88ooo8888.    888`88b.      .88ooo8888.       `888.8'     
 .8'     `888.   888  `88b.   .8'     `888.       `888'      
o88o     o8888o o888o  o888o o88o     o8888o       `8'       
                                                             
                                                             
File:      UAVController
Purpose:   This file contains the implementation of a wrapper class that interfaces
           with a Bitcraze Crazyflie 2.1 using the Motion Commander classes and
           logging framework provided by Bitcraze. This class is used in the LandingPlatformController
           class to provide necessary operations on the UAV platform. Key functions to
           be enabled for the LandingPlatformController class are: done, launch, land,
           getBatteryLevel, rotate, move, getHeight, and isCharging.
Author:    Joseph Haun, Alexander McGinnis, Anthony Aboumrad
Created:   12-1-2019
Modified:  5-5-2020

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
  MA  02110-1301, USA.
"""
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

    def __init__(self, targetURI=None):
        """
        Function: __init__
        Purpose: Initialize all necessary UAV functionality
        Inputs: none
        Outputs: none
        Description: An initializer function that finds a Crazyflie, can be particular target or not, and sets up all necessary data values for logging data values from the Crazyflie.
        """

        #Enable the CrazyRadio PA drivers to communicate with the UAV.
        cflib.crtp.init_drivers()

        self.timeout = True
        self.available = []
        self.UAV = Crazyflie()
        self.param = None
        self.airborne = False
        self._recentDataPacket = None
        self._receivingDataPacket = False

        #Attempt to locate UAV by scanning available interface
        for _ in range(0,500):
            if(len(self.available) > 0):
                self.timeout = False
                break #If a UAV is found via scanning, break out of this loop
            else:
                self.available = cflib.crtp.scan_interfaces()            

        #If there are Crazyflies available, connect to one of them
        if(len(self.available) > 0):
            #If there is a specific target, parse through the returned array to locate specific Crazyflie
            if(targetURI != None):
                for i in range(len(self.available)):
                    if(self.available[i][0] == targetURI):
                        #If found, open a link to the Crazyflie
                        self.UAV.open_link(self.available[i][0])
                        self.connectedToTargetUAV = True
                    else:
                        self.connectedToTargetUAV = False
            else:
                #If there is not a specific target, simply connect to the first Crazyflie available
                self.UAV.open_link(self.available[0][0])

            #While the Crazyflie is not connected, wait until the connection occurs to allow for Motion Commander initialization
            while(self.UAV.is_connected() == False): time.sleep(0.1)

            #Pass the connected Crazyflie to the Motion Commander class
            self.MC = MotionCommander(self.UAV)
            
            #Create desired logging parameters
            self.UAVLogConfig = LogConfig(name = "UAVLog", period_in_ms=100)
            self.UAVLogConfig.add_variable('pm.vbat', 'float')
            self.UAVLogConfig.add_variable('stateEstimate.x', 'float')
            self.UAVLogConfig.add_variable('stateEstimate.y', 'float')
            self.UAVLogConfig.add_variable('stateEstimate.z', 'float')
            self.UAVLogConfig.add_variable('pm.chargeCurrent', 'float')
            #Add more variables here for logging as desired

            #Add the configured logger to the Crazyflie to begin grabbing data packets
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
        Description: See purpose.
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
        Description: A wrapper function that calls the Crazyflie Motion Commander take_off function. See Bitcraze Crazyflie documentation for further details.
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
        Description: A function that calls the Crazyflie Motion Commander Land function. See Bitcraze Crazyflie documentation for further details.
        """
        self.airborne = False
        self.MC.land()
        return
    
    def move(self, distanceX, distanceY, distanceZ, velocity):
        """
        Function: move
        Purpose: A wrapper function to instruct an UAV to move <x, y, z> distance from current point
        Inputs: distanceX - a floating point value that represents the distance to move the in the X-dimension, measured in meters.
                distanceY - a floating point value that represents the distance to move the in the Y-dimension, measured in meters.
                distanceZ - a floating point value that represents the distance to move the in the Z-dimension, measured in meters.
                velocity - a floating point value that represents the velocity of the UAV during movement, measured in meters per second
        Outputs: none
        Description: See purpose.
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
        Description: Currently this function is not in use as rotating the Crazyflie regularly introduces positional errors. In particular, the Crazyflie will rotate on a motor, not the center of the drone.
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
        Purpose: A function that reads the UAV battery level from an IOStream
        Inputs: none
        Outputs: retVal - a floating point value that represents the battery voltage of the UAV.
        Description: See purpose.
        """
        retVal = None
        if(self._recentDataPacket != None and self._receivingDataPacket == False):
            retVal = self._recentDataPacket["pm.vbat"]      
            
        return retVal

    def getHeight(self):
        """
        Function: getCurrentHeight
        Purpose: A function that reads the UAV height from a IOStream.
        Inputs: none
        Outputs: retVal - a floating point value that represents the onboard height detection of the UAV.
        Description: See purpose.
        """
        retVal = None
        if(self._recentDataPacket != None and self._receivingDataPacket == False):
            retVal = self._recentDataPacket["stateEstimate.z"]

        return retVal

    def isCharging(self):
        """
        Function: getCurrentHeight
        Purpose: A function that reads the UAV charge current from a IOStream
        Inputs: none
        Outputs: retVal - a floating point value that represents the charge current of the UAV. 
        Description: See purpose. 
        """
        retVal = None
        if(self._recentDataPacket != None and self._receivingDataPacket == False):
            retVal = self._recentDataPacket["pm.chargeCurrent"]

        return retVal
        
    def _getUAVDataPacket(self, ident, data, logconfig):
        """
        Function: getUAVDataPacket
        Purpose: A callback function to process a data packet received from the UAV
        Inputs: ident -  identifier of the UAV
                data - data from the UAV
                logconfig - log configuration from the UAV
        Outputs: None
        Description: A user should NEVER call this function.
        """
        self._receivingDataPacket = True
        self._recentDataPacket = data
        self._receivingDataPacket = False 
