import serial
import sys
import glob
import math
import time
import numpy

class LandingPlatformController():
    
    def __init__(self, UAV=None, cameraInitValue='{900$900}\r\n', hoverHeight=0.5, velocity=0.2, serialLimiters=['{','$','}']):
        """
        Function: __init__
        Purpose: Setup the LandingPlatformController class
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
            
        #Define class constants necessary for 
        self._uav = UAV
        self._uavVelocity = velocity
        self._hoverHeight = hoverHeight
        self._minHoverHeight = hoverHeight - hoverHeight/10
        self._uavPos = [-1, -1, -1]
        self._landingPos = [0, 0, 0] #A set of world coordinates that needs to be defined somehow
        self._cameraInitValue = cameraInitValue
        self._serialLimiters = serialLimiters
        self._cameraAccuracy = 50 #Number of points the camera will sample each pass
        self._uavLandingAccuracy = 0.01 #The magnitude a offset vector needs to overcome to be considered valid

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
        self._camera = None
        while(self._getCameraSerialConnection(cameraInitValue) == None):{"""Do Nothing"""}
        self._camera = serial.Serial(port=self._getCameraSerialConnection(cameraInitValue))

    def _getUAVPosition(self):
        """
        Function: _getUAVPosition
        Purpose: Get the most up-to-date UAV position in rectangular coordinates
        Inputs: None
        Outputs: None
        """
        if(self._camera == None):
            return 

        #Find the default value for the camera, this indicates non-detection
        xValDummy = int(self._cameraInitValue[self._cameraInitValue.rfind(self._serialLimiters[0])+1:self._cameraInitValue.rfind(self._serialLimiters[1])])
        yValDummy = int(self._cameraInitValue[self._cameraInitValue.rfind(self._serialLimiters[1])+1:self._cameraInitValue.rfind(self._serialLimiters[2])])
        
        #Get update height
        self._uavPos[2] = self._uavGetHeight()
        xPoints = [0]
        yPoints = [0]
        
        #Flush serial buffer to insure that most recent data points are grabbed
        self._camera.reset_input_buffer()

        #Workaround currently
        #Until the last value in the initial value is found, read characters
        while(self._camera.read(1).decode('ascii') != self._cameraInitValue[-1]):{} #Need to fix this to a limiter
           
        for i in range(0, int(self._cameraAccuracy)):
            #Read serial data for largest possible string length from camera
            posString = self._camera.read(len(self._cameraInitValue)).decode('ascii')
            posString = posString[posString.find(self._serialLimiters[0]):posString.find(self._serialLimiters[2])+1]

            if(len(posString) > 0):
                if(posString[0] == '{'):                    
                    #Find the limiter positions to properly split string into x & y components
                    initIndex=posString.rfind(self._serialLimiters[0])
                    splitIndex=posString.rfind(self._serialLimiters[1])
                    lastIndex=posString.rfind(self._serialLimiters[2])
            
                    #Convert both positions to integer values
                    xPos = int(posString[(initIndex+1):splitIndex])
                    yPos = int(posString[(splitIndex+1):lastIndex])

                    if(xPos > xValDummy or yPos > yValDummy):
                        #A value greater than the init string indicates an error occurred
                        self._uavPos = [None, None, None]
                        return self._uavPos

                    #If values are less than dummy values, append to array
                    if((xPos <= xValDummy) and (yPos <= yValDummy)):
                        #Convert from pixels to world coordinates with conversion function
                        xPos, yPos = self._pixelConversion(xPos, yPos, self._uavPos[2])
                        #Append to list for potential averaging
                        xPoints.append(xPos)
                        yPoints.append(yPos)
            else:
                #If a proper value was not found, flush the input buffer again
                self._camera.reset_input_buffer()
                
        #Update the UAV x,y positions with the averages from camera                
        if((len(xPoints) > 0) and (len(yPoints) > 0)):
            self._uavPos[0] = math.fsum(xPoints)/len(xPoints)
            self._uavPos[1] = math.fsum(yPoints)/len(yPoints)
        else:
            self._uavPos = [None, None, None]
            
        return self._uavPos

    def _uavInFrame(self):

        #Find the default value for the camera, this indicates non-detectionx
        xValDummy = int(self._cameraInitValue[self._cameraInitValue.rfind(self._serialLimiters[0])+1:self._cameraInitValue.rfind(self._serialLimiters[1])])
        
        #Create blank arrays
        xPoints = [xValDummy]
        inFrame = False

        #Flush serial buffer to insure that most recent data points are grabbed
        self._camera.reset_input_buffer()
        
        #Workaround currently
        #Until the last value in the initial value is found, read characters
        while(self._camera.read(1).decode('ascii') != self._cameraInitValue[-1]):{} #Need to fix this to a limiter

        for i in range(0, int(self._cameraAccuracy*0.2)): #Will need to worry about this if twenty percent of accuracy is less than one
            #Read serial data for largest possible string length from camera
            posString = self._camera.read(len(self._cameraInitValue)).decode('ascii')
            posString = posString[posString.find(self._serialLimiters[0]):posString.find(self._serialLimiters[2])+1]

            #If a proper position string was grabbed, process it
            if(len(posString) > 0):
                if(posString[0] == '{'):                    
                    #Find the limiter positions to properly split string into x & y components
                    initIndex=posString.rfind(self._serialLimiters[0])
                    splitIndex=posString.rfind(self._serialLimiters[1])
                    lastIndex=posString.rfind(self._serialLimiters[2])
            
                    #Convert both positions to integer values
                    xPos = int(posString[(initIndex+1):splitIndex])
                    
                    #Append to list for potential averaging
                    xPoints.append(xPos)
            else:
                #If a proper value was not found, flush the input buffer again
                self._camera.reset_input_buffer()

        print("LPC: _uavInFrame - xPoints =", xPoints)
        if(xPoints.count(xValDummy) < len(xPoints)*0.5): #Will need to allow this fifty percent to be modifiable
            inFrame = True
            
        return inFrame
    
    def _pixelConversion(self, x_pixel, y_pixel, distance):
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
        offset[0] = self._landingPos[0] - self._uavPos[0]
        offset[1] = self._landingPos[1] - self._uavPos[1]
        offset[2] = self._landingPos[2] - self._uavPos[2]
        return offset

    def _uavGetHeight(self):
        """
        Function: _uavGetHeight
        Purpose: Get the UAV z-coordinate in the world frame
        Inputs: None
        Outputs: a floating point value representing the z-coordinate 
        """
        #Might want to figure out how to read UAV height from logs as this is a terrible way to go about it. 
        return self._hoverHeight

    def _sendMovement(self, xDis, yDis, zDis):
        """
        Function: _sendMovement
        Purpose: Instruct the UAV to move to certain coordinates
        Inputs: xDis - a floating point value to move in the x-dimension, in meters
                yDis - a floating point value to move in the y-dimension , in meters
                zDis - a floating point value to move in the z-dimension, in meters
        Outputs: None
        """
        #Send movement to UAV, UAV controller class will delay an appropriate time while the UAV moves
        self._uav.move(xDis, yDis, zDis, self._uavVelocity)
        #Update hover height
        self._hoverHeight += zDis
        return
    
    def engageFlightRoutine(self):
        self._sendMovement(0, 0, 0.5)
        self._performLandingSequence()
        return

    def done(self):
        self._uav.land()
        self._uav.done()
        self._camera.close()
        return
    
    def _performLandingSequence(self):
        """
        Function: _performLandingSequence
        Purpose: Align UAV with desired coordinates, once aligned safely land the UAV
        Inputs: None
        Outputs: None
        """
        #While UAV is still flying (height >= min)
        #Get UAV position reported by camera 
        #Calculate distance vector from landing point
        #Move UAV along distance vector
        #  While UAV is moving, stall landing procedure
        #Repeat procedure

        #Perform landing sequence
        while((self._hoverHeight >= self._minHoverHeight)):
            #Get current position and save to temp variable, then copy to actual variable to prevent erroneous overwriting
            temp = self._getUAVPosition()
            if(temp != None):
                startPos = temp.copy()
            else:
                startPos = [0, 0, ]
            offset = self._calculateOffset()
            #Calculate the magnitude of the offset vector
            offsetMagnitude = math.sqrt(math.pow(offset[0],2) + math.pow(offset[1],2))
            #If the magnitude is greater than the desired accuracy value, move the UAV in the X-Y plane
            if(offsetMagnitude > self._uavLandingAccuracy):
                expectedPos = [startPos[0]+offset[0], startPos[1]+offset[1], offset[2]]
                self._sendMovement(offset[0], offset[1], 0)
                
                #While the UAV is not in the frame, reduce the offset given by ten percent
                offsetRedux = 0.1
                while(self._uavInFrame() == False):
                    self._sendMovement(-offset[0]*offsetRedux, -offset[1]*offsetRedux, 0)
                    
                    temp = self._getUAVPosition()
                    endPos = temp.copy()
                    print("LPC: _performLandingSequence - startPos =", startPos)
                    print("LPC: _performLandingSequence - Offset =", offset)
                    print("LPC: _performLandingSequence - expecetdPos =", expectedPos)
                    print("LPC: _performLandingSequence - endPos =", endPos)
                    self._alignUAV(startPos, expectedPos, endPos)
                    while(self._uavInFrame() == False):
                        self._sendMovement(0,0,math.fabs(offset[2]*0.05))
            #Otherwise, move the UAV in the -Z direction
            else:
                self._sendMovement(0, 0, 0.1*offset[2]) 

        self._uav.land()
        return

    def _alignUAV(self, startVector, expectedVector, endVector):
        """
        Function: _alignUAV
        Purpose: Reduce the UAV's offset rotation to near zero from perspective of camera
                 by calculating the angle between an expected move and the actual move
                 using the law of cosines. 
        Inputs: expectedVector - a list of values indicating expected <x, y> coordinates of the UAV in the view of the camera
                actualVector - a list of values indicating the actual <x, y> coordinates of the UAV in the view of the camera
        Outputs: the angle, in degrees, by which the UAV is offset
        """ 
        #Find the magnitude of the expected change
        magnitudeExpected = math.sqrt(math.pow(expectedVector[0]-startVector[0],2) + math.pow(expectedVector[1]-startVector[1],2))
        #Find the magnitude of the actual change by subtracting start position from actual position
        magnitudeActual = math.sqrt(math.pow(endVector[0]-startVector[0],2) + math.pow(endVector[1]-startVector[1],2))
        #Find the magnitude of the difference between actual and expected
        magnitudeDiff = math.sqrt(math.pow(endVector[0]-expectedVector[0],2) + math.pow(endVector[1]-expectedVector[1],2))

        #If either of the magnitudes are equal to zero, return zero degrees
        if((magnitudeExpected == 0) or (magnitudeActual == 0)):
            return 0
        
        print("LPC: _alignUAV - startCoord =", startVector)
        print("LPC: _alignUAV - expectedChange =", expectedVector)
        print("LPC: _alignUAV - actual =", endVector)
        print("LPC: _alignUAV - (magE, magA, magD) =", (magnitudeExpected, magnitudeActual, magnitudeDiff))
        
        #Find angle between two vectors by solving the law of cosines form for the angle.
        internalVal = (math.pow(magnitudeExpected,2) + math.pow(magnitudeActual,2) - math.pow(magnitudeDiff,2))/(2*magnitudeExpected*magnitudeActual)
        print("LPC: _alignUAV - internalVal =", internalVal)
        angle = math.degrees(math.acos(internalVal))
        print("LPC: _alignUAV - angle =", angle)

        #Reduce angle to below 360 while preserving original sign value
        angle = (angle/math.fabs(angle))*(angle%360)

        #Reduce the angle to below 180 while preserving original sign value
        if(math.fabs(angle) > 180):
            angle = (angle/math.fabs(angle))*(math.fabs(angle) - 360)
            
        self._uav.rotate(angle)
        
        return angle
    
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
        #Create a blank camera port
        cameraPort = None
        
        #Get all available serial ports
        availablePorts = self._getAllSerialPorts()
        
        #For all ports returned, create a test connection and look for expected values
        for port in availablePorts:
            test = serial.Serial(port)
            while(test.read(1).decode('ascii') != expectedVals[-1]):{}
            if(test.read(len(expectedVals)).decode('ascii') == expectedVals):
                #If expected values are found, assign the string value of the port
                cameraPort = port
            
            test.close()
        
        #Return the last found serial connection as a string value
        return cameraPort
        
    def _getAllSerialPorts(self):
        """
        Function: _getAllSerialPorts
        Purpose: Find all available serial ports on the current machine regardless of operating system
        Inputs: none
        Outputs: array of all found ports represented as strings
        Credit: Thomas, https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
        Edits: Joseph Haun
        """
        #Create blank arrays for eventual contents
        availablePorts = []
        possiblePorts = []
        #Depending on Operating System:
        #Dynamically create an array of values of known possible serial port connection names
        if(sys.platform.startswith("win") == True):
            possiblePorts = ['COM%s' % (i+1) for i in range(256)]
        elif((sys.platform.startswith("linux") == True) or (sys.platform.startswith("cygwin") == True)):
            possiblePorts = glob.glob('/dev/tty[A-Za-z]*')
        elif(sys.platform.startswith("darwin") == True):
            possiblePorts = glob.glob('/dev/tty.*')
        else:
            #If a known Operating System is not found, raise an exception
            raise EnvironmentError("_getAllSerialPorts: Operating System not supported")

        for port in possiblePorts:
            try:
                #For all possible ports, attempt to create a test connection
                test = serial.Serial(port)
                test.close()
                #If successfully created, append to list
                availablePorts.append(port)
            except(OSError, serial.SerialException):
                #If not successfully created, catch exception and ignore it
                pass

        return availablePorts
