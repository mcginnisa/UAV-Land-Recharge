# In Memory Basic Frame Differencing Example
#
# This example demonstrates using frame differencing with your OpenMV Cam. It's
# called basic frame differencing because there's no background image update.
# So, as time passes the background image may change resulting in issues.

import sensor, image, pyb, os, time

TRIGGER_THRESHOLD = 5

width_frame = 320 #max for QVGA 320
height_frame = 240 #max for QVGA 240


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

while(True):
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.

    # Replace the image with the "abs(NEW-OLD)" frame difference.
    img = img.difference(extra_fb)

    edges = img.find_edges(image.EDGE_CANNY, threshold=(10, 80))
    blobs = img.find_blobs([(30, 255)], pixels_threshold=5, area_threshold=5, merge=True, margin=50) #red blobs
    if len(blobs) > 1:
        print("More than one blob!")
    for blob in blobs:
    #for blob in img.find_blobs([(80, 255)]): #red blobs
        if blob.pixels() > 300:
            continue
        #print('found blob')
        RGBcolor = (255,255,255)
        xpos = blob.cx()
        ypos = blob.cy()
        img.draw_cross(xpos, ypos)
        img.draw_circle(blob.enclosing_circle(),color=RGBcolor)
        print(str(xpos) + ',' + str(ypos))

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
