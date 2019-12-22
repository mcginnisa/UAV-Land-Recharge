import csv
import os
import time
import numpy as np
import re

initial_height = 0.4

target_coords = [64,64]

cache_size = 5

def get_camera_cache(range=cache_size):
    with open('camera_cache.txt','r') as csvfile:
        reader_object = csv.reader(csvfile)
        string_list = []
        for row in reader_object:
            string_list = [str(i) for i in row]
        return string_list[-range:]

def get_coords(range=cache_size):
    coord_list_str = get_camera_cache(range)
    if any("error" in s for s in coord_list_str):
        return [999,999]
    x_coords = []
    y_coords = []
    # print(coord_list_str)
    for coord in coord_list_str:
        if not re.search(r'\d', coord): #if there are no digits
            continue
        x_coords.append(int(coord.split('$')[0]))
        y_coords.append(int(coord.split('$')[1]))
        #if there are no coords in this list
    if len(x_coords) == 0:
        return [900,900]
    return [np.mean(x_coords),np.mean(y_coords)]

def get_height():
    with open('setpoint.txt','r') as csvfile:
        setpoint_file = csv.reader(csvfile)
        for row in setpoint_file:
            float_list = [float(i) for i in row]
            height = float_list[3]
            return height

def write_setpoint(dx,dy,rotate_by_this,target_height):
    with open('setpoint.txt','w') as csvfile:
        setpoint_file = csv.writer(csvfile)
        setpoint_file.writerow([dx,dy,rotate_by_this,target_height])

def inch_x_y(x_dir=0,y_dir=0,speed=0.1):
    write_setpoint(*[x_dir*speed,y_dir*speed,0,get_height()])
    time.sleep(0.7)

def set_height(height=0.2):
    write_setpoint(*[0,0,0,height])
    time.sleep(0.7)

def get_distance(vec1,vec2):
    diff_vec = np.subtract(vec1,vec2)
    diff_len = np.sqrt(diff_vec.dot(diff_vec))
    return diff_len

# def get_camera_cache():

while True:
    first_coords = get_coords()
    if first_coords[0] >= 900: #if there are errors try again
        continue
    inch_x_y(x_dir=3) #inch forward in x axis
    print('moving')
    time.sleep(1)
    coords = get_coords() #get new coords after that is done
    if coords[0] == 900: #if we left the frame, come back
        inch_x_y(x_dir=-6)
    if coords[0] > 900: #if there are errors try again
        continue
    #now lets see if the commands we are sending are actually moving it
    distance = get_distance(coords,first_coords)
    #if distance > 10: #if this is true, thats the drone were moving


    print(distance)
    # np.linalg.norm(np.subtract(coords,first_coords))
    print('end')
    break

    time.sleep(0.1)
# while True:



# def rotate_degrees(degrees):
#     for i in range(1,degrees,10):
#         time.sleep(0.7)
