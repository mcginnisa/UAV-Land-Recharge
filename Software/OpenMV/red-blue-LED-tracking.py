
import sensor, image, time, math



#threshold values were determined by taking a snapshot of the LED test board at a high altitude, and using the Tools > Machine Vision > Threshold Editor
#thresholdRed = [(64, 100, 14, 127, -128, 127)]
#thresholdBlue = [(75, 100, -128, 2, -128, 127)]

#thresholdRed = [(80, 100, -6, 50, -18, 3)]
#thresholdBlue = [(74, 100, 7, 36, -60, -8)]

thresholdRed = [(80, 100, -6, 50, -18, 3)]
thresholdBlue = [(75, 100, -128, 2, -128, 127)]

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.VGA)
sensor.set_windowing((400,400)) #MUST ADD THIS IF USING VGA MODE (find blobs cant handle bayer images)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()

#xpos1 = 0
#ypos1 = 0
#xpos2 = 0
#ypos2 = 0

def getthoseblobs(targetColor,img):

    if targetColor == 'red':
        LABlist = thresholdRed
        RGBcolor = (255,0,0)
    if targetColor == 'blue':
        LABlist = thresholdBlue
        RGBcolor = (0,0,255)
    try:
        for blob in img.find_blobs(LABlist, pixels_threshold=10, area_threshold=10): #red blobs
            xpos = blob.cx()
            ypos = blob.cy()
            img.draw_cross(xpos, ypos)
            img.draw_circle(blob.enclosing_circle(),color=RGBcolor)
        return [xpos,ypos]
    except:
        return 0


# Only blobs that with more pixels than "pixel_threshold" and more area than "area_threshold" are
# returned by "find_blobs" below. Change "pixels_threshold" and "area_threshold" if you change the
# camera resolution. Don't set "merge=True" becuase that will merge blobs which we don't want here.

while(True):
    clock.tick()
    img = sensor.snapshot()
    #print(clock.fps())
    redPosXY = getthoseblobs('red',img)
    bluePosXY = getthoseblobs('blue',img)
    print('red x,y: ' + str(redPosXY))
    print('blue x,y: ' + str(bluePosXY))

