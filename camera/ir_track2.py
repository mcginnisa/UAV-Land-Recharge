

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



TRIGGER_THRESHOLD = 5

#width_frame = 320 #max for QVGA 320
#height_frame = 240 #max for QVGA 240
#width_frame = int(240) #max for QVGA 320
#height_frame = int(240) #max for QVGA 240

#sensor.reset() # Initialize the camera sensor.
#sensor.set_pixformat(sensor.GRAYSCALE) # or sensor.GRAYSCALE RGB565
#sensor.set_framesize(sensor.QVGA) # or sensor.QQVGA (or others)
#sensor.set_windowing((width_frame, height_frame)) # look at center 240x240 pixels of the VGA resolution.

#sensor.skip_frames(time = 200) # Let new settings take affect.
#sensor.set_auto_whitebal(False) # Turn off white balance.
#sensor.set_auto_gain(False)



thresholds = (255, 255) # thresholds for bright white light from IR.

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QVGA)
#sensor.set_windowing((240, 240)) # 240x240 center pixels of VGA
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()


EXPOSURE_TIME_SCALE = 0.01

current_exposure_time_in_microseconds = sensor.get_exposure_us()

sensor.set_auto_exposure(False, \
    exposure_us = int(current_exposure_time_in_microseconds * EXPOSURE_TIME_SCALE))




clock = time.clock() # Tracks FPS.

# Take from the main frame buffer's RAM to allocate a second frame buffer.
# There's a lot more RAM in the frame buffer than in the MicroPython heap.
# However, after doing this you have a lot less RAM for some algorithms...
# So, be aware that it's a lot easier to get out of RAM issues now. However,
# frame differencing doesn't use a lot of the extra space in the frame buffer.
# But, things like AprilTags do and won't work if you do this...
#extra_fb = sensor.alloc_extra_fb(sensor.width(), sensor.height(), sensor.GRAYSCALE)
#extra_fb = sensor.alloc_extra_fb(width_frame, height_frame, sensor.GRAYSCALE)

'''
print("About to save background image...")
sensor.skip_frames(time = 200) # Give the user time to get ready.
extra_fb.replace(sensor.snapshot())
print("Saved background image - Now frame differencing!")
'''

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
    #if len(blobs) > 1:
    #    print("More than one blob!")
    blob_list = []
    for blob in blobs:
        if len(blobs) > 3:
            raise_error()
        elif len(blobs) == 0:
            print('{900$900}')
            red_led.off()
            blue_led.on()
            green_led.off()
        else:
            red_led.off()
            blue_led.off()
            green_led.on()
        RGBcolor = (255,255,255)
        xpos = blob.cx()
        ypos = blob.cy()
        img.draw_cross(xpos, ypos)
        img.draw_circle(blob.enclosing_circle(),color=RGBcolor)
        coord = [xpos,ypos]
        blob_list.append(coord)
        #print(str(xpos) + ',' + str(ypos))
    if len(blob_list) > 2:
        #we picked up the flow deck, finding most distant points
        ab=0
        ac=0
        bc=0
        length_ab = ((blob_list[0][0]-blob_list[1][0])**2 + (blob_list[0][1]-blob_list[1][1])**2)**0.5
        length_ac = ((blob_list[0][0]-blob_list[2][0])**2 + (blob_list[0][1]-blob_list[2][1])**2)**0.5
        length_bc = ((blob_list[1][0]-blob_list[2][0])**2 + (blob_list[1][1]-blob_list[2][1])**2)**0.5
        #sorting because micropython might not have sort
        if length_ab >= length_ac:
            if length_ab >= length_bc:
                blob_list.pop(2)
        elif length_ac >= length_ab:
            if length_ac >= length_bc:
                blob_list.pop(1)
        elif length_bc >= length_ab:
            if length_bc >= length_ac:
                blob_list.pop(0)
    #midpoint = ((x1 + x2)/2, (y1 + y2)/2)
    midpoint = ((blob_list[0][0] + blob_list[1][0])/2, (blob_list[0][1] + blob_list[2][2])/2)
    xpos = pad_with_0(str(midpoint[0]),3)
    ypos = pad_with_0(str(midpoint[1]),3)
    print('{' + xpos + '$' + ypos + '}')
