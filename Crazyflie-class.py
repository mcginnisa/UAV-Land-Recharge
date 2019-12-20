import time
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.utils.callbacks import Caller

class autonomousUAV(self):
    def __init__(self):
        #Sets up the autonomousUAV class
        self.UAV = linkToCrazyflie()
        
    def thrustMap(percentage):
        #Function takes in a 0-100 value and outputs integer to give to Crazyflie
        return 10001 + (percentage/100)*(60000-10001)

    def linkToCrazyflie(self):
        #Still in progress, see testing-functionality file
        pass

    def sendSetpointToCrazyflie(self, roll, pitch, yawrate, thrust):
        try:
            #Send a blank setpoint, then the given setpoint to properly implement command
            self.UAV.commander.send_setpoint(0, 0, 0, 0)
            self.UAV.commander.send_setpoint(roll, pitch, yawrate, thrust)
            #Potentially write to log files here?
            return True
        except:
            #Potentially write to log files here?
            #Return false in case of an error
            return False
