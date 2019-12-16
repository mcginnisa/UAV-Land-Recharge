#!/bin/env python3

import logging
import time
import cflib.crtp
import random
from cflib.crazyflie import Crazyflie
from cflib.utils.callbacks import Caller

cflib.crtp.init_drivers()
available = cflib.crtp.scan_interfaces()
for i in available:
    print("Interface with URI [%s] found and name/comment [%s]" % (i[0], i[1]))

crazyflie = Crazyflie()
#crazyflie.connected.add_callback(crazyflie_connected)
crazyflie.open_link("radio://0/80/250K")

roll = 0.0
pitch = 0.0
yawrate = 0
thrust = 0

for i in range(1000):
    print("Sending Setpoint", (roll, pitch, yawrate, thrust))
    crazyflie.commander.send_setpoint(0,0,0,0)
    crazyflie.commander.send_setpoint(roll,pitch,yawrate,10001+i)
    roll = random.random()
    pitch = random.random()
    yawrate = random.random()
    thrust = 10000*random.random()
    time.sleep(0.001)

crazyflie.close_link()
