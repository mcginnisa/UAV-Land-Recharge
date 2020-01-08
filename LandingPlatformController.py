from UAVController import UAVController
import serial
import sys
import glob
import math

class LandingPlatformController():
    
    def __init__(self, UAV=None, cameraInitValue='{900$900}\r\n', hoverHeight=0.3, velocity=0.1, serialLimiters=['{','%','}']):
        """
        Function: _getUAVPosition
        Purpose: Get the most up-to-date UAV position in rectangular coordinates
        Inputs: UAV - a UAV controller object that is able to direct a relevant UAV
                cameraInitValue - a string denoting the default value that should be present on the serial connection representing the camera
                hoverHeight - a floating point value denoting a minimum height in meters to hover
                velocity - a floating point value indicating the velocity in meters per second the UAV will travel at
                serialLimiters - an array of strings that denote the limiting characters/strings for the serial data
        Outputs: None
        """
        
        #Define/Manage UAV connection
        if(UAV == None):
            print("ERROR: Landing Platform Controller requires a UAV control object")
            
        #Define class constants
        self._uav = UAV
        self._uavVelocity = velocity #Find out default velocity
        self._hoverHeight = hoverHeight
        self._uavPos = [-1, -1, -1]
        self._landingPos = [-1, -1, -1] #Will need to be defined somehow
        self._cameraInitValue = cameraInitValue
        self._serialLimiters = serialLimiters

        #Define constants to allow for pixel to world coordinate conversion
        self._focalLength = 0.00265 #focal length of lens in meters, per datasheet
        self._xImage = 0.003984 #sensor x-size in meters, per datasheet
        self._yImage = 0.002952 #sensor y-size in meters, per datasheet
        self._xSensor = 656 #sensor x-size in pixels, per datasheet
        self._ySensor = 488 #sensor y-size in pixels, per datasheet
        self._xActive = 640 #Dimension of active sensors in the x direction in pixels, per datasheet
        self._yActive = 480 #Dimension of active sensors in the y direction in pixels, per datasheet
        self._xRange = 240 #Frame size in the x dimension in pixels, per selected camera mode
        self._yRange = 240 #Frame size in the y dimension in pixels, per selected camera mode
        self._xOff = self._xRange/2 #Offset value in the x dimension
        self._yOff = self._yRange/2 #Offset value in the y dimension
        
        #Define/Manage Serial connection
        self._camera = serial.Serial(self._getCameraSerialConnection(cameraInitValue))

    def _getUAVPosition(self):
        """
        Function: _getUAVPosition
        Purpose: Get the most up-to-date UAV position in rectangular coordinates
        Inputs: None
        Outputs: curPosition - an array of floating point values representing <x, y, z>
        """
        
        #Get update height
        self._uavPos[2] = self._uavGetHeight()
        #Flush serial buffer to insure that most recent data points are grabbed
        self._camera.reset_input_buffer()
        #Create blank string to add values
        positionString=""
        #Find the first limiter value to begin grabbing a data point
        while(self._camera.read(1).decode('ascii') != self._serialLimiters[0]): {""" Do nothing """}
        #Find the third limiter which denotes the end of a data point
        while(self._camera.read(1).decode('ascii') != self._serialLimiters[2]):
            positionString = positionString + self._camera.read(1).decode('ascii')
        #Find the second limiter inside the given string to split the string into necessary x and y portions
        splitIndex=positionString.rfind(self._serialLimiters[1])
        #Convert the parsed values from serial connection to integers and pass to pixel conversion function
        self._uavPos[0], self._uavPos[1] = self._pixelConversion(int(positionString[:splitIndex]), int(positionString[(splitIndex+1):]), self._uavPos[2])

        return

    def _pixelConversion(x_pixel, y_pixel, distance):
        """
        Function: _pixelConversion
        Purpose: Convert pixel coordinates into world coordinates
        Inputs: x_pixel - an integer value denoting the x-coordinate of the UAV
                y_pixel - an integer value denoting the y-coordiante of the UAV
                distance - a floating point value denoting the distance in meters of the UAV from the camera
        Outputs: a tuple of x,y
                 x - a floating point value denoting the x-coordinate of the UAV in the world frame
                 y - a floating point value denoting the y-coordinate of the UAV in the world frame
        """
        k = distance/self._focalLength
        xPixSize = 2*(self._xImage/self._xSensor)
        yPixSize = 2*(self._yImage/self._ySensor) #Temporary fix corresponding to QVGA vs VGA pixel
        x = k*xPixSize*(x_pixel - self._xOff)
        y = k*yPixSize*(y_pixel - self._yOff)
        return x,y
    
    def _calculateOffset(self):
        """
        Function: _calculateOffset
        Purpose: Calculate the offset distance of the UAV to the desired landing point
        Inputs: None
        Outputs: offset - an array of values representing <dx, dy, dz> in meters 
        """
        offset = [0, 0, 0]
        self._getUAVPosition()
        offset[0] = self._uavPos[0] - self._landingPos[0]
        offset[1] = self._uavPos[1] - self._landingPos[1]
        offset[2] = self._uavPos[2] - self._landingPos[2]
        return offset

    def _uavGetHeight(self):
        """
        Function: _uavGetHeight
        Purpose: Get the UAV z-coordinate in the world frame
        Inputs: None
        Outputs: a floating point value representing the z-coordinate 
        """
        return self._hoverHeight

    def _sendMovement(self, xPos, yPos, zPos):
        """
        Function: _sendMovement
        Purpose: Instruct the UAV to move to certain coordinates
        Inputs: xPos - a floating point value denoting the new x position, in meters, to move towards
                yPos - a floating point value denoting the new y position, in meters, to move towards
                zPos - a floating point value denoting the new z position, in meters, to move towards
        Outputs: None
        """
        distances = [(self._uavPos[0] - xPos), (self._uavPos[1] - yPos), (self._uavPos[2] - zPos) ]
        if(distances[2] != 0):
            self._hoverHeight = zPos
        self._uav.move(distances[0], distances[1], distances[2], self._uavVelocity)
        pass

    def engageFlightRoutine(self):
        pass
    
    def _performLandingSequence(self):
        """
        Function: _performLandingSequence
        Purpose: Align UAV with desired coordinates, once aligned safely land the UAV
        Inputs: None
        Outputs: None
        """
        #curPosition = self._getUAVPosition()
        self._uav.launch()
        self._uav.move(0,0,0.5,0.05)
        self._uav.land()
        self._uav.done()
        pass

    def _getBatteryLevel(self):        
        pass

    def _getCameraSerialConnection(self, expectedVals):
        """
        Function: _getAllSerialPorts
        Purpose: Find the currently connected camera module by analyzing a series of serial values
        Inputs: expectedVals - an array of values that are expected to come from the serial connection
                offsetVal - an integer representing extra characters to pull in that are not part of expected values
        Outputs: A string that represents the port that has the camera connection
        Note: Performs a priming read which will discard the first value sent.
        """
        cameraPort = None
        availablePorts = self._getAllSerialPorts()
        for port in availablePorts:
            test = serial.Serial(port)
            while(test.read(1).decode('ascii') != expectedVals[-1]):{}
            if(test.read(len(expectedVals)).decode('ascii') == expectedVals):
                cameraPort = port
            
            test.close()
        #End of Function
        return cameraPort
        
    def _getAllSerialPorts(self):
        """
        Function: _getAllSerialPorts
        Purpose: Find all available serial ports on the current machine regardless of operating system
        Inputs: none
        Outputs: array of all found ports represented as strings
        Credit: Thomas, https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
        """
        availablePorts = []
        possiblePorts = []
        if(sys.platform.startswith("win") == True):
            possiblePorts = ['COM%s' % (i+1) for i in range(256)]
        elif((sys.platform.startswith("linux") == True) or (sys.platform.startswith("cygwin") == True)):
            possiblePorts = glob.glob('/dev/tty[A-Za-z]*')
        elif(sys.platform.startswith("darwin") == True):
            possiblePorts = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError("_getAllSerialPorts: Operating System not supported")

        for port in possiblePorts:
            try:
                test = serial.Serial(port)
                test.close()
                availablePorts.append(port)
            except(OSError, serial.SerialException):
                pass
        #End of Function
        return availablePorts

import time
    
if True:
    TestUAV = UAVController()
    print("UAV Added?", dir(TestUAV))
    Test = LandingPlatformController(UAV=TestUAV)
    Test._performLandingSequence()
    print("Success!")
    
