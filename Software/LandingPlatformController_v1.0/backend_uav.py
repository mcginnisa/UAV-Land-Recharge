
import logging
import time
import sys
import os
import csv

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

URI = 'radio://0/80/250K'

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

def get_height():
    with open('setpoint.txt','r') as csvfile:
        setpoint_file = csv.reader(csvfile)
        for row in setpoint_file:
            float_list = [float(i) for i in row]
            height = float_list[3]
            return height

if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        cf = scf.cf

        cf.param.set_value('kalman.resetEstimation', '1')
        time.sleep(0.1)
        cf.param.set_value('kalman.resetEstimation', '0')
        time.sleep(2)

        print('lifting off...')
        for y in range(10):
            cf.commander.send_hover_setpoint(0, 0, 0, y / 25)
            time.sleep(0.1)

        print("receiving commands...")
        old_mod_time = os.stat('setpoint.txt').st_mtime
        while True:
            new_mod_time = os.stat('setpoint.txt').st_mtime
            if new_mod_time != old_mod_time:
                # print("the file has CHANGED!")
                old_mod_time = os.stat('setpoint.txt').st_mtime
                with open('setpoint.txt') as csvfile:
                    setpoint_file = csv.reader(csvfile)
                    for row in setpoint_file:
                        float_list = [float(i) for i in row]
                        for y in range(5): #this routine takes half a second
                            # print('test')
                            cf.commander.send_hover_setpoint(*float_list)
                            time.sleep(0.1)
            else:
                #hover at 0.4 meters
                try:
                    height = get_height()
                except:
                    height = 0.4
                cf.commander.send_hover_setpoint(0, 0, 0, height)
                time.sleep(0.1)
                        #* means interpret list as arguments
                        # owo_what_is_this(*int_list)
                    #     print([int(i) for i in row])
                    #     print(int(row[0]))


        # print('holding...')
        # while True:
        #     for j in range(50):
        #         cf.commander.send_hover_setpoint(0, 0, 0, 0.4)
        #         time.sleep(0.1)
"""
        except KeyboardInterrupt:
            print('touching down...')
            for y in range(10):
                cf.commander.send_hover_setpoint(0, 0, 0, (10 - y) / 25)
                time.sleep(0.1)
                cf.commander.send_stop_setpoint()
                sys.exit()
"""
