'''
If there are >3 points, it will report an error (901).
If there <1 point, it will report nothing (900),
If there is one point, it will report that point
If there are two points, it will report midpoint between the two points
If there are 3 points, it will report midpoint between two most distant points (ignoring the flash from the flow deck)

'''

import sensor, image, pyb, os, time
from pyb import USB_VCP


from pyb import LED
red_led   = LED(1)
green_led = LED(2)
blue_led  = LED(3)
ir_led    = LED(4)
red_led.off()
green_led.off()
blue_led.off()
ir_led.off()


def raise_error():
    print('{901$901}')
    red_led.on()
    blue_led.off()
    green_led.off()

def pad_with_0(string_to_pad, target_length):
   while len(string_to_pad) < target_length:
        string_to_pad = '0' + string_to_pad
   return string_to_pad
#print pad_with_n_chars("doggy",9,"y")


thresholds = (255, 255) # thresholds for bright white light from IR.

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QVGA)
#sensor.set_windowing((240, 240)) # 240x240 center pixels of VGA
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()


#If you lose the crazyflie at high altitude, increase this number
#0.015 is a good value for infrared. Set to 1 to see background and pickup ceiling lights
EXPOSURE_TIME_SCALE = 0.017
current_exposure_time_in_microseconds = sensor.get_exposure_us()

sensor.set_auto_exposure(False, \
    exposure_us = int(current_exposure_time_in_microseconds * EXPOSURE_TIME_SCALE))



clock = time.clock() # Tracks FPS.


usb = USB_VCP()

#Send standby code (904) until RasPi gives the go ahead
#comment out this while loop to start the camera spamming coords by default

while(True):
    red_led.off()
    green_led.on()
    blue_led.on()
    ir_led.off()
    print('{904$904}')
    cmd = usb.recv(5, timeout=100)
    if (cmd == b'start'):
        cmd = "0"
        break


while(True):
    #clock.tick()
    img = sensor.snapshot()
    blobs = img.find_blobs([(240, 255)], pixels_threshold=1, area_threshold=1, merge=False, margin=50) #red blobs

    if len(blobs) > 3:
        raise_error()
        continue
    elif len(blobs) == 0:
        print('{900$900}')
        red_led.off()
        blue_led.on()
        green_led.off()
        continue
    else:
        red_led.off()
        blue_led.off()
        green_led.on()


    blob_list = []
    for blob in blobs:
        xpos = blob.cx()
        ypos = blob.cy()
        img.draw_cross(xpos, ypos)
        img.draw_circle(blob.enclosing_circle(),color=(255,255,255))
        coord = [xpos,ypos]
        blob_list.append(coord)
        #print(str(xpos) + ',' + str(ypos))
    if len(blob_list) > 2:
        #we picked up the flow deck, finding most distant points

        distance = [0,0,0]
        #d=sqrt((x2-x1)^2+(y2-y1)^2)
        #distance a to b
        distance[2] = ((blob_list[0][0]-blob_list[1][0])**2 + (blob_list[0][1]-blob_list[1][1])**2)**0.5
        #distance a to c
        distance[1] = ((blob_list[0][0]-blob_list[2][0])**2 + (blob_list[0][1]-blob_list[2][1])**2)**0.5
        #distance b to c
        distance[0] = ((blob_list[1][0]-blob_list[2][0])**2 + (blob_list[1][1]-blob_list[2][1])**2)**0.5

        #sorting because micropython might not have sort
        max = distance[0]
        #find the max in the list
        for i in range(len(distance)):
            if distance[i] >= max:
                max = distance[i]
        #delete the point which is not involved in the max distance. This works
        #because of the ordering of the distance list
        for i in range(len(distance)):
            if distance[i] == max:
                blob_list.pop(i)
                break

    #midpoint = ((x1 + x2)/2, (y1 + y2)/2)
    if len(blob_list) > 1:
        midpoint = ((blob_list[0][0] + blob_list[1][0])/2, (blob_list[0][1] + blob_list[1][1])/2)
    else:
        midpoint = blob_list[0]
    xpos = pad_with_0(str(int(midpoint[0])),3)
    ypos = pad_with_0(str(int(midpoint[1])),3)
    print('{' + xpos + '$' + ypos + '}')
