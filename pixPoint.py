#! /usr/bin/env python3

# Simple function to convert pixel coordinates (from image frame)
# to world coordinates, in meters. Distance to object is taken from
# the image's focal point.
#
# Author: Anthony Aboumrad, Sonoma State University

import math

# Define lens and camera parameters
FOCAL_LENGTH = 0.00265	# focal length of lens, in meters
X_IMAGE = 0.003984      # sensor size, x, in meters, per datasheet
Y_IMAGE = 0.002952	# sensor size, y, in meters, per datasheet
X_SENSOR = 656		# sensor size, x, in pixels, per datasheet
Y_SENSOR = 488	      	# sensor size, y, in pixels, per datasheet
X_ACTIVE = 640		# active sensors, x, in pixels, per datasheet
Y_ACTIVE = 480		# active sensors, y, in pixels, per datasheet

OFFSET_ORIGIN = True	# if pixel origin differs from world origin

# Needs to be updated for selected camera mode and frame cropping
X_RANGE = 320		# frame size, x, in pixels, per selected camera mode
Y_RANGE = 240		# frame size, y, in pixels, per selected camera mode

# determine dimensions (in meters) of individual pixels (ps = pixelsize)
x_ps = (X_IMAGE/X_SENSOR)         # pixel size for default VGA mode, no cropping
x_ps = x_ps*2                     # temp fix, this corresponds to QVGA vs VGA pixel size
#x_ps = x_ps*(X_ACTIVE/X_RANGE)   # obsolete, will not work for cropped frames
y_ps = (Y_IMAGE/Y_SENSOR)         # pixel size for default VGA mode, no cropping
y_ps = y_ps*2                     # temp fix, this corresponds to QVGA vs VGA pixel size
#y_ps = y_ps*(Y_ACTIVE/Y_RANGE)   # obsolete, will not work for cropped frames

#  xy offset of world origin (assumed image center) from pixel origin
x_off = 0
y_off = 0
if OFFSET_ORIGIN:
   x_off = int(X_RANGE/2)
   y_off = int(Y_RANGE/2)

# transform function
def pixelPoint(x_pixel, y_pixel, distance, focal, x_pix_off, y_pix_off, x_pix_size, y_pix_size):
   "Returns xy coordinates, in meters, from image pixel point, given object distance, camera's focal length, and origin offset"
   k = distance/focal
   x = k*x_pix_size*(x_pixel - x_pix_off)
   y = k*y_pix_size*(y_pixel - y_pix_off)
   return x,y;

# example coordinates
a = 269         # x pixel
b = 49         # y pixel
z = 0.9           # distance, in meters

# example function call
x,y = pixelPoint(a, b, z, FOCAL_LENGTH, x_off, y_off, x_ps, y_ps);
print(f'x = {x:.2f}')
print(f'y = {y:.2f}')
