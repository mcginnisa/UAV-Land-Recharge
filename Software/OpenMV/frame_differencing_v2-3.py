#Now with programmatic reseting

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
width_frame = int(240) #max for QVGA 320
height_frame = int(240) #max for QVGA 240

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.GRAYSCALE) # or sensor.GRAYSCALE RGB565
sensor.set_framesize(sensor.QVGA) # or sensor.QQVGA (or others)
sensor.set_windowing((width_frame, height_frame)) # look at center 240x240 pixels of the VGA resolution.

sensor.skip_frames(time = 200) # Let new settings take affect.
sensor.set_auto_whitebal(False) # Turn off white balance.
sensor.set_auto_gain(False)



clock = time.clock() # Tracks FPS.

# Take from the main frame buffer's RAM to allocate a second frame buffer.
# There's a lot more RAM in the frame buffer than in the MicroPython heap.
# However, after doing this you have a lot less RAM for some algorithms...
# So, be aware that it's a lot easier to get out of RAM issues now. However,
# frame differencing doesn't use a lot of the extra space in the frame buffer.
# But, things like AprilTags do and won't work if you do this...
#extra_fb = sensor.alloc_extra_fb(sensor.width(), sensor.height(), sensor.GRAYSCALE)
extra_fb = sensor.alloc_extra_fb(width_frame, height_frame, sensor.GRAYSCALE)


print("About to save background image...")
sensor.skip_frames(time = 200) # Give the user time to get ready.
extra_fb.replace(sensor.snapshot())
print("Saved background image - Now frame differencing!")


usb = USB_VCP()
while(True):
    cmd = usb.recv(5, timeout=100)
    if (cmd == b'reset'):
        cmd = "0"
        print('{902$902}')
        red_led.on()
        green_led.off()
        blue_led.off()
        ir_led.off()
        sensor.skip_frames(time = 2000) # take a new picture
        extra_fb.replace(sensor.snapshot())
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.

    # Replace the image with the "abs(NEW-OLD)" frame difference.
    img = img.difference(extra_fb)


    blobs = img.find_blobs([(30, 255)], pixels_threshold=5, area_threshold=5, merge=True, margin=100) #red blobs
    if len(blobs) > 1:
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
    for blob in blobs:
    #for blob in img.find_blobs([(80, 255)]): #red blobs
        #if blob.area() > (1/8)*height_frame*width_frame: #1/8 will filter out smaller objects
        #    raise_error()
        if blob.area() > (0.75)*height_frame*width_frame: #1/8 will filter out smaller objects
            raise_error()
            #print("About to save background image...")
            sensor.skip_frames(time = 2000) # wait for 2 seconds for the error to leave
            extra_fb.replace(sensor.snapshot())
            #print("Saved background image - Now frame differencing!")
            continue
        #print('found blob')
        RGBcolor = (255,255,255)
        xpos = blob.cx()
        ypos = blob.cy()
        img.draw_cross(xpos, ypos)
        img.draw_circle(blob.enclosing_circle(),color=RGBcolor)
        xpos = pad_with_0(str(xpos),3)
        ypos = pad_with_0(str(ypos),3)
        #xpos = str(xpos).rjust(3,'0')
        #ypos = str(ypos).rjust(3,'0')
        #xpos = str(xpos).zfill(3)
        #ypos = str(ypos).zfill(3)
        print('{' + xpos + '$' + ypos + '}')
        #print('{' + str(xpos) + '$' + str(ypos) + '}')

    #img.find_edges(image.EDGE_CANNY, threshold=(80, 100))


    #hist = img.get_histogram()
    # This code below works by comparing the 99th percentile value (e.g. the
    # non-outlier max value against the 90th percentile value (e.g. a non-max
    # value. The difference between the two values will grow as the difference
    # image seems more pixels change.
    #diff = hist.get_percentile(0.99).l_value() - hist.get_percentile(0.90).l_value()
    #triggered = diff > TRIGGER_THRESHOLD

    #print(clock.fps(), triggered) # Note: Your OpenMV Cam runs about half as fast while
    # connected to your computer. The FPS should increase once disconnected.
