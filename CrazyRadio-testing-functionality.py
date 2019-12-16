#!/bin/env python3

import logging
import time
import cflib.crtp
import random

from cflib.crazyflie import Crazyflie
from cflib.utils.callbacks import Caller
from cflib.positioning.motion_commander import MotionCommander

cflib.crtp.init_drivers()
available = cflib.crtp.scan_interfaces()
for i in available:
    print("Interface with URI [%s] found and name/comment [%s]" % (i[0], i[1]))

crazyflie = Crazyflie()
#crazyflie.connected.add_callback(crazyflie_connected)
if(len(available) > 0):
    crazyflie.open_link(available[0][0])
    with MotionCommander(crazyflie) as UAV:
        UAV.up(0.5, 0.01)
        time.sleep(5)
        UAV.down(0.5, 0.01)
    crazyflie.close_link()
    
else:
    print("ERROR: Unable to find anything")



