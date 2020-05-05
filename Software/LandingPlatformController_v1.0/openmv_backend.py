import time
import serial
import csv

cache_size = 5

cache = []
while True:
    with serial.Serial('/dev/ttyACM0', 115200, timeout=5) as ser:
        # x = ser.read()          # read one byte
        s = ser.read(10)        # read up to ten bytes (timeout)
        # line = ser.readline()   # read a '\n' terminated line
        # print(s)
    # time.sleep(0.1)
    s = str(s)
    message = s[s.find("{")+1:s.find("}")]
    if len(cache) < cache_size:
        cache.append(message)
    else:
        with open('camera_cache.txt','w') as csvfile:
            setpoint_file = csv.writer(csvfile)
            setpoint_file.writerow(cache)
        cache = []
    # print(len(cache))
    # print(cache)
