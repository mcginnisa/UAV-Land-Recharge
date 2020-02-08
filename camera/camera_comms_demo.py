# sudo apt-get remove modemmanager

# USB VCP example.
# This example shows how to use the USB VCP class to send an image to PC on demand.
#
# WARNING:
# This script should NOT be run from the IDE or command line, it should be saved as main.py
# Note the following commented script shows how to receive the image from the host side.
#
# #!/usr/bin/env python2.7
import sys, serial, struct, time
message = "reset"
port = '/dev/ttyACM0'

for i in range(5):
    sp = serial.Serial(port, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                xonxoff=False, rtscts=False, stopbits=serial.STOPBITS_ONE, timeout=None, dsrdtr=True)
    sp.flush()
    s = sp.read(10)
    s = str(s)
    print(s)
    sp.close()
    # time.sleep(0.5)



sp = serial.Serial(port, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
            xonxoff=False, rtscts=False, stopbits=serial.STOPBITS_ONE, timeout=None, dsrdtr=True)
# s = sp.read(4)
# sp.flush()
# s = sp.read(4)
sp.flush()
# sp.setDTR(True) # dsrdtr is ignored on Windows.
sp.write(message.encode())
sp.flush()
#sp.write(message.encode())
#sp.write(message.encode())
#sp.write(message.encode())
s = sp.read(10)
s = str(s)
print(s)
sp.close()

for i in range(5):
    sp = serial.Serial(port, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                xonxoff=False, rtscts=False, stopbits=serial.STOPBITS_ONE, timeout=None, dsrdtr=True)
    sp.flush()
    s = sp.read(10)
    s = str(s)
    print(s)
    sp.close()
    # time.sleep(0.5)

# size = struct.unpack('<L', sp.read(4))[0]
# img = sp.read(size)
# sp.close()
#
# with open("img.jpg", "w") as f:
#     f.write(img)
