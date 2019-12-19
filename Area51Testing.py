import logging
import time
import cflib.crtp
import random

from cflib.crazyflie import Crazyflie
from cflib.utils.callbacks import Caller
from cflib.positioning.motion_commander import MotionCommander
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.crazyflie.log import LogConfig

cflib.crtp.init_drivers()
available = cflib.crtp.scan_interfaces()
    
crazyflie = Crazyflie()
#crazyflie.connected.add_callback(crazyflie_connected)
if(len(available) > 0):

    lg_stab = LogConfig(name="Battery", period_in_ms=1000)
    lg_stab.add_variable('pm.batteryLevel', 'float') #stateEstimate.x, stateEstimate.y
    lg_stab.add_variable('stateEstimate.x', 'float')
    lg_stab.add_variable('stateEstimate.y', 'float')
    
    with SyncCrazyflie(available[0][0]) as scf:
        with SyncLogger(scf, lg_stab) as logger:
            #with MotionCommander(scf) as UAV:
                #        UAV.up(1, 0.2)
                #        time.sleep(1)
                #        UAV.down(1, 0.2)
            endTime = time.time() + 20
            for log_entry in logger:
                #print(log_entry[1].get("pm.batteryLevel"))
                print((log_entry[1].get("stateEstimate.x"), log_entry[1].get("stateEstimate.y")))
                #if(time.time() > endTime):
                    #break
    pass
else:
    print("ERROR: Unable to find anything")


