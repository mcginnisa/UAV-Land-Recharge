import os
import csv
import time
def owo_what_is_this(arg1,arg2,arg3,arg4):
    print(arg1)
    print(arg2)
    print(arg3)
    print(arg4)



# print("receiving commands...")
# old_mod_time = os.stat('setpoint.txt').st_mtime
# while True:
#     new_mod_time = os.stat('setpoint.txt').st_mtime
#     if new_mod_time != old_mod_time:
#         print("the file has CHANGED!")
#         old_mod_time = os.stat('setpoint.txt').st_mtime
#         with open('setpoint.txt') as csvfile:
#             setpoint_file = csv.reader(csvfile)
#
#             for row in setpoint_file:
#                 int_list = [int(i) for i in row]
#                 #* means interpret list as arguments
#                 owo_what_is_this(*int_list)
#             #     print([int(i) for i in row])
#             #     print(int(row[0]))


print("receiving commands...")
old_mod_time = os.stat('setpoint.txt').st_mtime
while True:
    new_mod_time = os.stat('setpoint.txt').st_mtime
    if new_mod_time != old_mod_time:
        print("the file has CHANGED!")
        old_mod_time = os.stat('setpoint.txt').st_mtime
        with open('setpoint.txt') as csvfile:
            setpoint_file = csv.reader(csvfile)
            for row in setpoint_file:
                int_list = [int(i) for i in row]
                for y in range(10):
                    print('test')
                    # cf.commander.send_hover_setpoint(*int_list)
                    time.sleep(0.1)
