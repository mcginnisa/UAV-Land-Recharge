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
from cflib.crazyflie.log import Log

cflib.crtp.init_drivers()
available = cflib.crtp.scan_interfaces()
    
crazyflie = Crazyflie()

if(len(available) > 0):
    crazyflie.open_link(available[0][0])
    while(crazyflie.is_connected() == False): time.sleep(0.1)
    lg_stab = LogConfig(name="Battery", period_in_ms=1000)
    lg_stab.add_variable('pm.batteryLevel', 'float') #stateEstimate.x, stateEstimate.y
    lg_stab.add_variable('stateEstimate.x', 'float')
    lg_stab.add_variable('stateEstimate.y', 'float')
    
    crazyflie.log.add_config(lg_stab)
    print(dir(crazyflie.log))
    crazyflie.log.refresh_toc()
    print(crazyflie.log.state)
    #testLog.add_config(lg_stab)
    time.sleep(5)
    
    crazyflie.close_link()
    pass
else:
    print("ERROR: Unable to find anything")


