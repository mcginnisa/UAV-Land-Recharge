import csv
import os
import time
import numpy as np
import re
import math

initial_height = 0.4

target_coords = [240/2-30,240/2]

# target_coords = [30,230]
# target_coords = [12,64]

cache_size = 5

# def vector_in_rotated_axes(result_vec,expected_vec):
#     #rotate expected_vec or target_vec into the coordinates of the UAV
#     #first we need to get the CCW angle between the vectors
#     dot = np.dot(expected_vec,result_vec) #dot product
#     det = np.linalg.det(expected_vec,result_vec) #determinant
#     # dot = x1*x2 + y1*y2      # dot product between [x1, y1] and [x2, y2]
#     # det = x1*y2 - y1*x2      # determinant
#     theta = np.arctan2(det, dot)  # atan2(y, x) or atan2(sin, cos)
#
#     # theta = np.radians(30)
#     #now we compute the rotation matrix
#     rotation_mat = np.array(( (np.cos(theta), -np.sin(theta)),
#                    (np.sin(theta),  np.cos(theta)) ))
#     #rotate the expected_vec into the axes of the UAV
#     rotated_vec = np.dot(expected_vec,rotation_mat)



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
        return [901,901]
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

def write_setpoint(dx=0,dy=0,rotate_by_this=0,target_height=0):
    with open('setpoint.txt','w') as csvfile:
        setpoint_file = csv.writer(csvfile)
        setpoint_file.writerow([dx,dy,rotate_by_this,target_height])

def move_uav(direction_vec=[0,0],rot_deg_ccw=0,height=get_height(),speed=0.3):
    # print(direction_vec)
    # print(rot_deg_ccw)
    # print(height)
    # print(speed)
    length = np.linalg.norm(direction_vec)
    if not length == 0: #catch divide by zero cases
        normalized_vec = np.array(direction_vec)/length
    else:
        normalized_vec = [0,0]
    x_dir = normalized_vec[0]
    y_dir = normalized_vec[1]
    write_setpoint(*[x_dir*speed,y_dir*speed,rot_deg_ccw,height])
    #print('speed =' + str(speed))
    time.sleep(2)

# def rot_uav(degrees_ccw):
#     i = 0
#     while i < degrees_ccw:
#         i = i + 1
#         write_setpoint(0,0,i,get_height())
#         time.sleep(0.1)

def get_distance(vec1,vec2):
    diff_vec = np.subtract(vec1,vec2)
    diff_len = np.sqrt(diff_vec.dot(diff_vec))
    return diff_len

def get_delta_theta(vec1,vec2):
    #gives the angle in degrees between the vectors as measured in a
    # counterclockwise direction from vec1 to vec2.
    # if v1 = [x1,y1] and v2 = [x2,y2] are the components of two vectors, then
    dot = np.dot(vec1,vec2) #dot product
    det = np.linalg.det([vec1,vec2]) #determinant
    #     theta = np.arctan2(det, dot)  # atan2(y, x) or atan2(sin, cos)
    # dot = x1*x2 + y1*y2      # dot product between [x1, y1] and [x2, y2]
    # det = x1*y2 - y1*x2      # determinant
    theta = np.arctan2(det, dot)  # atan2(y, x) or atan2(sin, cos)
    return np.degrees(theta)

def land_softly():
    for i in np.arange(get_height(),0,-0.1):
        with open('setpoint.txt','r') as csvfile:
            setpoint_file = csv.reader(csvfile)
            for row in setpoint_file:
                float_list = [float(i) for i in row]
                print(float_list)
        if i <= 0.15:
            write_setpoint(target_height=0)
            break
        write_setpoint(target_height=i-0.1)
        time.sleep(0.5)

def get_move_speed(target_move_vec):
    distance = np.linalg.norm(target_move_vec)
    distance = np.abs(distance)
    print('distance =' + str(distance))
    distance = distance/100-0.20
    distance = np.clip(distance,0.08,0.35)
    print('speed =' + str(distance))
    return distance

# move_uav()


# def get_camera_cache():
move_uav(direction_vec=[0,0],rot_deg_ccw=0,height=0.6,speed=0.3) #set default height
# land_softly()

while True:
    time.sleep(0.5)
    reverse = 0
    first_coords = get_coords()
    print(first_coords)
    if first_coords[0] >= 900: #if there are errors try again
        print('errors or no lock')
        continue
    target_move_vec = np.subtract(target_coords,first_coords)
    move_uav(direction_vec=target_move_vec,speed=get_move_speed(target_move_vec)) #inch forward in x axis
    print('moving')
    # time.sleep(1)
    coords = get_coords() #get new coords after that is done
    print(coords)
    if get_distance(coords,first_coords) < 6.9:
        print('didnt move')
        continue
    if coords[0] == 900: #if we left the frame, come back
        print('left frame')
        move_uav(direction_vec=-target_move_vec,speed=0.45) #inch forward in x
        # time.sleep(1)
        coords = get_coords()
        print(coords)
        reverse = 1 #include this so that we know the real actual_move_vec
    if coords[0] >= 900: #if there are errors try again
        continue
    #now lets see if the commands we are sending are actually moving it
    distance = get_distance(coords,first_coords)
    print('distance moved:' + str(distance))
    if distance > 10: #if this is true, thats the drone we're moving
        print('rotating')
        actual_move_vec = np.subtract(coords,first_coords)
        if reverse:
            actual_move_vec = -actual_move_vec
        delta_theta = -1*get_delta_theta(actual_move_vec,target_move_vec)
        move_uav(rot_deg_ccw=delta_theta)
        print('rotated by' + str(delta_theta))
    else:  #if the coord didn't move, we are tracking a false positive
        continue


    if np.allclose(coords,target_coords,atol=7):
        print('reached target')
        land_softly()
        break

    print('reached end, not there yet, starting over')


    # break

    # time.sleep(0.1)
# while True:



# def rotate_degrees(degrees):
#     for i in range(1,degrees,10):
#         time.sleep(0.7)
