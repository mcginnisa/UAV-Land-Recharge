#! /usr/bin/env python3

# Simple function to convert pixel coordinates (from image frame)
# to world coordinates, in meters. Distance to object is taken from
# the image's focal point.
#
# Author: Anthony Aboumrad, Sonoma State University

import math

# Define camera parameters
FOCAL_LENGTH = 0.00265	# focal length of camera, in meters
X_IMAGE = 0.003984      # sensor size, x, in meters, per datasheet
Y_IMAGE = 0.002952	# sensor size, y, in meters, per datasheet
X_SENSOR = 656		# sensor size, x, in pixels, per datasheet
Y_SENSOR = 488	      	# sensor size, y, in pixels, per datasheet
X_ACTIVE = 640		# active sensors, x, in pixels, per datasheet
Y_ACTIVE = 480		# active sensors, y, in pixels, per datasheet
OFFSET_ORIGIN = True	# if pixel origin differs from world origin
X_RANGE = 320		# frame size, x, in pixels
Y_RANGE = 240		# frame size, y, in pixels

# determine dimensions (in meters) of individual pixels (ps = pixelsize)
x_ps = X_IMAGE/X_SENSOR
x_ps = x_ps*(X_ACTIVE/X_RANGE)
y_ps = Y_IMAGE/Y_SENSOR
y_ps = y_ps*(Y_ACTIVE/Y_RANGE)

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
a = 160         # x pixel
b = 120         # y pixel
z = 2           # distance, in meters

# example function call
x,y = pixelPoint(a, b, z, FOCAL_LENGTH, x_off, y_off, x_ps, y_ps);
print(f'x = {x:.2f}')
print(f'y = {y:.2f}')
