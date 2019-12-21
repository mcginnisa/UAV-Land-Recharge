# QRCode Example
#
# This example shows the power of the OpenMV Cam to detect QR Codes
# without needing lens correction.

import sensor, image, time, math

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
#sensor.set_contrast(-3)
sensor.set_framesize(sensor.VGA)
sensor.set_windowing((230, 230)) # look at center 240x240 pixels of the VGA resolution.
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must turn this off to prevent image washout...
clock = time.clock()

while(True):
    clock.tick()
    img = sensor.snapshot()
    for code in img.find_apriltags():
        if code.id() == 9:
            codey = code.cy()
            codex = code.cx()
            img.draw_rectangle(code.rect(), color = (255,255,255))
            print(str(codex) + ',' + str(codey) + ',' + str(math.degrees(code.rotation())) )
            sensor.set_windowing((codex, codey, 150, 150))
        else:
            sensor.set_windowing((230, 230))
        #print(code.id())
    #print(clock.fps())
