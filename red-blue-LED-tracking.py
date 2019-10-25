#This runs on the OpenMV H7


import sensor, image, time, math


thresholdRed = [(64, 100, 14, 127, -128, 127)]
thresholdBlue = [(75, 100, -128, 2, -128, 127)]

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.VGA)
sensor.set_windowing((400,400)) #MUST ADD THIS IF USING VGA MODE (find blobs cant handle bayer images)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()

xpos1 = 0
ypos1 = 0
xpos2 = 0
ypos2 = 0

# Only blobs that with more pixels than "pixel_threshold" and more area than "area_threshold" are
# returned by "find_blobs" below. Change "pixels_threshold" and "area_threshold" if you change the
# camera resolution. Don't set "merge=True" becuase that will merge blobs which we don't want here.

while(True):
    clock.tick()
    img = sensor.snapshot()
    xpos1 = 0
    ypos1 = 0
    xpos2 = 0
    ypos2 = 0
    for blob in img.find_blobs(thresholdRed, pixels_threshold=10, area_threshold=10):
        xpos1 = blob.cx()
        ypos1 = blob.cy()
        img.draw_cross(xpos1, ypos1)
    for blob in img.find_blobs(thresholdBlue, pixels_threshold=10, area_threshold=10):
        xpos2 = blob.cx()
        ypos2 = blob.cy()
        img.draw_cross(xpos2, ypos2)
    #print(clock.fps())
    print('red x,y: ' + str(xpos1) + ',' + str(ypos1))
    print('blue x,y: ' + str(xpos2) + ',' + str(ypos2))

