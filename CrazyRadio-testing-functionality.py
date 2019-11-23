#!/usr/bin/env python3
import logging
import time
import cflib.crtp

from time import perf_counter

from cflib.crazyflie import Crazyflie
from cflib.utils.callbacks import Caller
from cflib.positioning.motion_commander import MotionCommander
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

cflib.crtp.init_drivers()
available = cflib.crtp.scan_interfaces()
for i in available:
    print("Interface with URI [%s] found and name/comment [%s]" % (i[0], i[1]))

"""
URI = 'radio://0/80/1M'

with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
    # We take off when the commander is created
    with MotionCommander(scf) as mc:
        time.sleep(1)
        
        # There is a set of functions that move a specific distance
        # We can move in all directions
        mc.forward(0.8)
        mc.back(0.8)
        time.sleep(1)
        
        mc.up(0.5)
        mc.down(0.5)
        time.sleep(1)
        
        # We can also set the velocity
        mc.right(0.5, velocity=0.8)
        time.sleep(1)
        mc.left(0.5, velocity=0.4)
        time.sleep(1)
        
        # We can do circles or parts of circles
        mc.circle_right(0.5, velocity=0.5, angle_degrees=180)
        
        # Or turn
        mc.turn_left(90)
        time.sleep(1)
        
        # We can move along a line in 3D space
        mc.move_distance(-1, 0.0, 0.5, velocity=0.6)
        time.sleep(1)
        
        # There is also a set of functions that start a motion. The
        # Crazyflie will keep on going until it gets a new command.
        
        mc.start_left(velocity=0.5)
        # The motion is started and we can do other stuff, printing for
        # instance
        for _ in range(5):
            print('Doing other work')
            time.sleep(0.2)
            
            # And we can stop
        mc.stop()
            
"""
if(len(available) != 0):

    crazyflie = Crazyflie()
    firstAvail=available[0]
    
    #with SyncCrazyflie(firstAvail[0], cr=Crazyflie
    
    #Not sure what this does yet, nor how to call it
    crazyflie_connected = Caller()
    #crazyflie.connected.add_callback(firstAvail[0])
    
    #Seeing if a parameter can be set
    if(False):
        crazyflie.param.set_value("flightmode.althold","True")
        crazyflie.param.set_value()
        
    #Opening link from array of available
    crazyflie.open_link(firstAvail[0])
        
    roll = 0.0
    pitch = 0.0
    yawrate = 0
    thrust = 0
    rangeVal = 10
    
    for i in range(rangeVal):
        timerStart = perf_counter()
        crazyflie.commander.send_setpoint(0,0,0,0)
        crazyflie.commander.send_setpoint(roll,pitch,yawrate,thrust)
        timerStop = perf_counter()
        #print("Elapsed Time:", i, timerStop - timerStart)
        time.sleep(0.5)

    crazyflie.close_link()
else:
    print("ERROR: Unable to find appropriate interface.")
        

#"""
