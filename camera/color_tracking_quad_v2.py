
import sensor, image, time, math


#threshold values were determined by taking a snapshot of the LED test board at a high altitude, and using the Tools > Machine Vision > Threshold Editor
#thresholdRed = [(64, 100, 14, 127, -128, 127)]
#thresholdBlue = [(75, 100, -128, 2, -128, 127)]

#thresholdRed = [(80, 100, -6, 50, -18, 3)]
#thresholdBlue = [(74, 100, 7, 36, -60, -8)]

thresholdRed = [(14, 100, 25, 127, 4, 127)]  #red tape
#thresholdRed = [(0, 91, 26, 127, -128, 127)]
#thresholdGreen = [(0, 100, -128, 127, 28, 127)]
thresholdGreen = [(0, 100, -128, -11, 37, 127)] #pale sticky paper
thresholdBlue = [(75, 100, -128, 2, -128, 127)]



sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.VGA)
sensor.set_windowing((450,450)) #MUST ADD THIS IF USING VGA MODE (find blobs cant handle bayer images)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()

EXPOSURE_TIME_SCALE = 1

current_exposure_time_in_microseconds = sensor.get_exposure_us()

sensor.set_auto_exposure(False, \
    exposure_us = int(current_exposure_time_in_microseconds * EXPOSURE_TIME_SCALE))

#xpos1 = 0
#ypos1 = 0
#xpos2 = 0
#ypos2 = 0

def list_diff(list1, list2):
    out = []
    for ele in list1:
        if not ele in list2:
            out.append(ele)
    return out

"""
def reject_old_blobs(list1):
    middle = int(len(list1)/2)
    if not (len(list1) % 2) == 0: #if not even
        list1.append([0,0])
        middle = int(len(list1)/2)

    firsthalf = list1[0:middle]
    lasthalf = list1[middle:middle*2]
    difference = list_diff(firsthalf,lasthalf)
    #print(difference)
    return difference

"""
def reject_old_blobs(list1):

    return [i for n, i in enumerate(list1) if i not in list1[:n]]
    #print(res)

list_blob = []

def getthoseblobs(img):
    xpos = 0
    ypos = 0
    unique_list = []
    global list_blob
    if len(list_blob) > 100:
        list_blob = list_blob[-100:]

    for blob in img.find_blobs([(14, 100, 25, 127, 4, 127)], pixels_threshold=1, area_threshold=1, merge=True, margin=50): #red blobs
       # print(blob.pixels())
        #if False:
        if blob.pixels() > 100000:
            xpos = 0
            ypos = 0
            #continue
        else:
            xpos = blob.cx()
            ypos = blob.cy()
            coord = [xpos,ypos]
            #img.draw_cross(xpos, ypos)
            img.draw_circle(blob.enclosing_circle(),color=(0,0,255))
            if coord not in list_blob:
                unique_list.append(coord)
            list_blob.append(coord)
            #return [xpos,ypos]

    list_blob = reject_old_blobs(list_blob)
    print(unique_list)




# Only blobs that with more pixels than "pixel_threshold" and more area than "area_threshold" are
# returned by "find_blobs" below. Change "pixels_threshold" and "area_threshold" if you change the
# camera resolution. Don't set "merge=True" becuase that will merge blobs which we don't want here.

while(True):
    #sensor.skip_frames(time = 100)
    #sensor.set_pixformat(sensor.RGB565)
    clock.tick()
    img = sensor.snapshot()
    #print(clock.fps())
    redPosXY = getthoseblobs(img)
    #bluePosXY = getthoseblobs('blue',img)
    #print('red x,y: ' + str(redPosXY))
unique_list    #print('blue x,y: ' + str(bluePosXY))
    #sensor.skip_frames(time = 100)
    #sensor.set_pixformat(sensor.GRAYSCALE)

