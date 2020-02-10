import serial
import sys
import glob
import math
import time

class LandingPlatformController():
    
    def __init__(self, settings=dict(), debug=False):
        """
        Function: __init__
        Purpose: Setup the LandingPlatformController class
        Inputs: debug - a boolean value that indicates whether debug messages and actions are taken. If false, systems will fail silently or crash.  
                settings - a relational array that contains various parameters that can be changed by the user

        <<<DETAIL SETTINGS HERE>>>

        Outputs: None
        Description: 
        """

        #Create a file descriptor object that can then be written to for debug messages
        try:
            self._debugFile = open(settings['debugFile'], 'w')
        except KeyError:
            if(debug == True):
                self._debugFile = sys.stdout
            else:
                self._debugFile = open('/dev/null', 'w')
        
        #Define boolean values used for flagging errors
        self._updatedPosition = False

        #Define default UAV position values
        self._uavPos = [-1, -1, -1]

        #Define default UAV offset angle value
        self._uavOffsetAngle = 0 #in radians
    
        #Define class constants necessary for UAV 
        try:
            self._uav = settings['uav']
        except KeyError:
            #If the dictionary value is not present, print warning message.
            if(debug == False):
                sys.exit(0)
            else:
                print("LPC: __init__ - Landing Platform Controller requires a UAV control object.", file=self._debugFile)
        
        try:
            self._uavVelocity = settings['velocity']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._uavVelocity = 0.2 

        try:
            self._hoverHeight = settings['hoverHeight']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._hoverHeight = 0.5

        try:
            self._minHoverHeight = settings['minHoverHeight']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._minHoverHeight = self._hoverHeight - self._hoverHeight/10

        try:
            self._landingPos = settings['landingPos']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._landingPos = [0, 0, 0]

        #Begin definition of class tolerance/accuracy values

        #Define a number of points the camera will sample each pass
        try:
            self._cameraAccuracy = settings['cameraAccuracy']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._cameraAccuracy = 15 

        #Define a number of points camera will use to determine if UAV is in frame
        try:
            self._cameraInFrameAccuracy = settings['cameraInFrameAccuracy']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._cameraInFrameAccuracy = 5 

        #Define a percentage of points at which the UAV is considered 'in frame'
        try:
            self._cameraInFrameThreshold = settings['cameraInFrameThreshold']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._cameraInFrameThreshold = 0.5

        #Define the magnitude an offset vector needs to overcome to be considered valid
        try:
            self._uavLandingTolerance = settings['uavLandingTolerance']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._uavLandingTolerance = 0.1 

        #Define a value used to determine if a new coordinate transform is necessary
        try:
            self._coordTolerance = settings['coordTolerance']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._coordTolerance = 0.05 

        #Define an integer value that determines the factor of the logarithmic function that determines if the UAV is on target
        try:
            self._onTargetFactor = settings['onTargetFactor']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._onTargetFactor = 12 

        #Define a floating point value that determines the height offset
        try:
            self._onTargetOffset = settings['onTargetOffset']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._onTargetOffset = 1.8

        #End definition of class tolerance/accuracy values

        #Begin definitions of values to allow for pixel to world coordinate conversion
        #Define the focal length of lens in meters, per datasheet
        try:
            self._focalLength = settings['focalLength']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._focalLength = 0.00265 

        #Define the sensor x-size in meters, per datasheet
        try:
            self._xImage = settings['xImage']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._xImage = 0.003984 

        #Define the sensor y-size in meters, per datasheet
        try:
            self._yImage = settings['yImage']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._yImage = 0.002952 

        #Define the sensor x-size in pixels, per datasheet
        try:
            self._xSensor = settings['xSensor']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._xSensor = 656

        #Define the sensor y-size in pixels, per datasheet
        try:
            self._ySensor = setting['xSensor']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._ySensor = 488 

        #Define the dimension of active sensors in the x direction in pixels, per datasheet
        try:
            self._xActive = settings['xActive']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._xActive = 640 

        #Define the dimension of active sensors in the y direction in pixels, per datasheet
        try:
            self._yActive = settings['yActive']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._yActive = 480 
            
        #Define the frame size in the x dimension in pixels, per selected camera mode
        try:
            self._xRange = settings['xRange']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._xRange = 240 

        #Define the frame size in the y dimension in pixels, per selected camera mode
        try:
            self._yRange = settings['yRange']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._yRange = 240 

        #Define the offset value in the x dimension
        try:
            self._xOff = settings['xOff']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._xOff = self._xRange/2 

        #Define the offset value in the y dimension
        try:
            self._yOff = settings['yOff']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._yOff = self._yRange/2 

        #End definitions of values to allow for pixel to world coordinate conversion

        #Begin definitions of values to manage/enable serial connection to the camera
        #Define the initial string values expected from the camera
        try:
            self._cameraInitValue = settings['cameraInitValue']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._cameraInitValue = '{904$904}\r\n'

        #Define the string that will be sent to the camera to start operations
        try:
            self._cameraStartString = settings['cameraStartString']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._cameraStartString = 'start'

        #Define limiters used to parse the serial data for coordinate values
        try:
            self._serialLimiters = settings['serialLimiters']
        except KeyError:
            #If the dictionary value is not present, use defaults
            self._serialLimiters = ['{','$','}']

        #End definitions of values to manage/enable serial connection to the camera
        
        #Create camera serial connection
        self._camera = None
        while(self._getCameraSerialConnection(cameraInitValue) == None):{"""Do Nothing"""}
        self._camera = serial.Serial(port=self._getCameraSerialConnection(cameraInitValue))

        #Send start string to camera value to begin operations
        self._camera.write(self._cameraStartString.encode())

    def _getUAVPosition(self):
        """
        Function: _getUAVPosition
        Purpose: Get the most up-to-date UAV position in rectangular coordinates
        Inputs: None
        Outputs: None
        Description:
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
   
        for i in range(0, int(self._cameraAccuracy)):
            #Workaround currently
            #Until the last value in the initial value is found, read characters
            while(self._camera.read(1).decode('ascii') != self._cameraInitValue[-1]):{} #Need to fix this to a limiter
        
            #Read serial data for largest possible string length from camera
            posString = self._camera.read(len(self._cameraInitValue)).decode('ascii')
            #Throw away any characters after the final limiter value
            posString = posString[posString.find(self._serialLimiters[0]):posString.find(self._serialLimiters[2])+1]
        
            if(len(posString) > 0):
                if(posString[0] == self._serialLimiters[0]):                    
                    #Find the limiter positions to properly split string into x & y components
                    initIndex=posString.rfind(self._serialLimiters[0])
                    splitIndex=posString.rfind(self._serialLimiters[1])
                    lastIndex=posString.rfind(self._serialLimiters[2])
            
                    #Convert both positions to integer values
                    xPos = int(posString[(initIndex+1):splitIndex])
                    yPos = int(posString[(splitIndex+1):lastIndex])

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
            self._updatedPosition = True
        else:
            self._updatedPosition = False

        return self._uavPos

    def _uavInFrame(self):
        """
        Function: _uavInFrame
        Purpose: Determine if the UAV is within the frame of the camera
        Inputs: None
        Outputs: a boolean value indicating if the UAV is within the frame
        Description:
        """
        #Find the default value for the camera, this indicates non-detectionx
        xValDummy = int(self._cameraInitValue[self._cameraInitValue.rfind(self._serialLimiters[0])+1:self._cameraInitValue.rfind(self._serialLimiters[1])])
        
        #Create blank arrays
        xPoints = [xValDummy]
        inFrame = False

        #Flush serial buffer to insure that most recent data points are grabbed
        self._camera.reset_input_buffer()
        
        for i in range(0, int(self._cameraInFrameAccuracy)):
            #Workaround currently
            #Until the last value in the initial value is found, read characters
            while(self._camera.read(1).decode('ascii') != self._cameraInitValue[-1]):{} #Need to fix this to a limiter
            
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

        print("LPC: _uavInFrame - xPoints =" + str(xPoints), file=self._debugFile)
        if(xPoints.count(xValDummy) <= len(xPoints)*self._cameraInFrameThreshold):
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
        Description:
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
        Purpose: Calculate the offset distance of the UAV to the desired landing point, assumes the position is up to date
        Inputs: None
        Outputs: offset - an array of values representing <dx, dy, dz> in meters 
        Description: This functions makes use of the landing platform position determined by the user to calculate the offset
                     given the current UAV position. This assumes that the UAV position has been updated recently. Otherwise,
                     it will be an inaccurate offset value. 
        """
        offset = [0, 0, 0]
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
        Description:
        """
        #Will want to figure out how to read UAV height from logs as this is a terrible way to go about it. 
        return self._hoverHeight

    def _sendMovement(self, xDis, yDis, zDis):
        """
        Function: _sendMovement
        Purpose: Instruct the UAV to move to certain coordinates
        Inputs: xDis - a floating point value denoting the distance, in meters, to move along the x-axis
                yDis - a floating point value denoting the distance, in meters, to move along the y-axis
                zDis - a floating point value denoting the distance, in meters, to move along the z-axis
        Outputs: None
        Description:
        """
        #If there is a movement to make
        if( (xDis+yDis+zDis) != 0):
            #Send movement to UAV, UAV controller class will delay an appropriate time while the UAV moves
            self._uav.move(xDis, yDis, zDis, self._uavVelocity)
            #Update hover height
            self._hoverHeight += zDis
        
        return

    def _sendToHome(self, xPos, yPos):
        """
        Function: _sendToHome
        Purpose: Instruct the UAV to move to certain coordinates
        Inputs: xPos - a floating point value denoting the x-dimension coordinate
                yPos - a floating point value denoting the y-dimension coordinate
        Outputs: None
        Description:
        """
        #Make copy of world coordinates
        print("LPC: _sendToHome - self._landingPos =" + str(self._landingPos), file=self._debugFile)
        temp = [xPos, yPos]
        worldCoords = temp.copy()
        print("LPC: _sendToHome - worldCoords =" + str(worldCoords), file=self._debugFile)
        #Transform the world coordinates to the UAV frame coordinates
        transformX = worldCoords[0]*math.cos(self._uavOffsetAngle) + worldCoords[1]*math.sin(self._uavOffsetAngle)
        transformY = -worldCoords[0]*math.sin(self._uavOffsetAngle) + worldCoords[1]*math.cos(self._uavOffsetAngle)
        print("LPC: _sendToHome - transform =" + str(transformX) + "," + str(transformY), file=self._debugFile)
        print("LPC: _sendToHome - self._landingPos =" + str(self._landingPos), file=self._debugFile)

        temp = [self._landingPos[0] - transformX, self._landingPos[1] - transformY, 0]
        distances = temp.copy()
        print("LPC: _sendToHome - distances =" + str(distances), file=self._debugFile)

        #Instruct UAV to move distances determined
        self._sendMovement(distances[0], distances[1], distances[2])
        #Update hover height
        self._hoverHeight += distances[2]
        #To prevent leaving of the camera frame, reduce previous movement by 10% if UAV is not in frame
        while(self._uavInFrame() == False and (distances[0]+distances[1]+distances[2]) != 0):
            print("LPC: _sendToHome - UAV Not in Frame", file=self._debugFile)
            self._sendMovement(-0.1*distances[0], -0.1*distances[1], 0*distances[2])
            
        return
    
    def engageFlightRoutine(self):
        """
        Function: engageFlightRoutine
        Purpose: 
        Inputs: None
        Outputs: None
        Description:
        """
        self._uav.launch()
        while(self._uavInFrame() == False):
            self._sendMovement(0, 0, 0.5)
        self._performLandingSequence()
        return

    def done(self):
        """
        Function: done
        Purpose: Halt all class activities
        Inputs: None
        Outputs: None
        Description:
        """
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
        Description:
        """

        #Perform landing sequence while the current hover height is greater than the minimum hover height
        while((self._hoverHeight >= self._minHoverHeight)):
            #Get current position and save to temp variable, then copy to actual variable to prevent erroneous overwriting
            temp = self._getUAVPosition()
            print("LPC: _performLandingSequence - updatedPosition =" + str(self._updatedPosition), file=self._debugFile)
            #START STATEMENT
            if(temp != None):
                startPos = temp.copy()
            print("LPC: _performLandingSequence - startPos1 =" + str(startPos), file=self._debugFile)
                    
            offset = self._calculateOffset()
            print("LPC: _performLandingSequence - Offset =" + str(offset), file=self._debugFile)
            
            #If the magnitude is greater than the desired accuracy value, move the UAV in the X-Y plane
            if(self._uavOnTarget(offset) == False):
                temp = [startPos[0]+offset[0], startPos[1]+offset[1], offset[2]]
                expectedPos = temp.copy()
                print("LPC: _performLandingSequence - expecetdPos =" + str(expectedPos), file=self._debugFile)
                self._sendToHome(startPos[0], startPos[1])

                #After movement, get the new UAV position so that the offset can be determined
                temp = self._getUAVPosition()
                if(temp != None):
                    endPos = temp.copy()
                print("LPC: _performLandingSequence - endPos =" + str(endPos), file=self._debugFile)
                        
                #After movement, make sure the UAV is aligned properly
                percentDiffX = expectedPos[0]/math.fabs(expectedPos[0] - endPos[0])
                percentDiffY = expectedPos[1]/math.fabs(expectedPos[1] - endPos[1])
                #If percent difference is greater than threshold and the angle is zero, create new transform
                if((percentDiffX > self._coordTolerance or percentDiffY > self._coordTolerance) and self._uavOffsetAngle == 0):
                    print("LPC: _performLandingSequence - Creating new transform", file=self._debugFile)
                    self._createCoordinateTransform(startPos, expectedPos, endPos)
                elif((percentDiffX > self._coordTolerance or percentDiffY > self._coordTolerance) and self._uavOffsetAngle != 0):
                    print("LPC: _performLandingSequence - Resetting Angle", file=self._debugFile)
                    print("LPC: _performLandingSequence - offsetAngle =" + str(self._uavOffsetAngle), file=self._debugFile)
                    self._uavOffsetAngle = 0
                #self._alignUAV(startPos, expectedPos, endPos)
                
            #Otherwise, move the UAV in the -Z direction
            else:
                self._sendMovement(0, 0, 0.1*offset[2]) 
            
        #Perform Landing Operations Here
        self._uav.land()
        return

    def _uavOnTarget(self, offsetVector):
        """
        Function: _uavOnTarget
        Purpose: Determine if the UAV is within the target area for its specific height
        Inputs: offsetVector - a list of floating point values representing the <dX, dY> necessary for the UAV to move to reach the center point
        Outputs: a boolean value indicating whether the UAV is within the target area for its specific height
        Description: _uavOnTarget determines if the UAV is within the appropriate offset from the target point by calculating the offset vector
                     magnitude and comparing it to a value calculated by solving the function h = log_{k}(r) for the radius, r, where h is the 
                     current height of the UAV and K is a scaling factor that can be adjusted depending on the desired function. If the offset
                     vector's magnitude is less than the calculated radius, the function reports true. Otherwise, it reports false.
        """
        #Calculate the magnitude of the vector to allow for better comparison
        offsetMag = math.sqrt(math.pow(offsetVector[0],2) + math.pow(offsetVector[1],2))

        #Assumes the _uavHoverHeight variable has been recently updated
        maxOffset = math.pow(self._onTargetFactor, self._hoverHeight - self._onTargetOffset)

        print("LPC: _uavOnTarget - maxOffset =" + str(maxOffset), file=self._debugFile)
        
        #If the maximum offset allowed at the UAV height is greater than current offset, return true
        if(maxOffset > offsetMag):
            return True
        return False

    def _createCoordinateTransform(self, startPosition, expectedPosition, endPosition):
        """
        Function: _createCoordinateTransform
        Purpose: Calculate the necessary angle to allow for UAV coordinates to be transformed from camera coordinates
        Inputs: startPosition - a list of values indicating the starting <x, y> coordinates of the UAV in the view of the camera
                expectedPosition - a list of values indicating expected <x, y> coordinates of the UAV in the view of the camera
                actualVector - a list of values indicating the actual <x, y> coordinates of the UAV in the view of the camera
        Outputs: None
        Description: 
        """
        self._uavOffsetAngle = math.atan2(expectedPosition[0]*endPosition[1] - expectedPosition[1]*endPosition[0], expectedPosition[0]*endPosition[0] - expectedPosition[1]*endPosition[1])
        return math.degrees(self._uavOffsetAngle)
                        
    def _alignUAV(self, startPosition, expectedPosition, endPosition):
        """
        Function: _alignUAV
        Purpose: Reduce the UAV's offset rotation to near zero from perspective of camera
                 by calculating the angle between an expected move and the actual move
                 using the law of cosines. 
        Inputs: startPosition - a list of values indicating the starting <x, y> coordinates of the UAV in the view of the camera
                expectedPosition - a list of values indicating expected <x, y> coordinates of the UAV in the view of the camera
                actualVector - a list of values indicating the actual <x, y> coordinates of the UAV in the view of the camera
        Outputs: the angle, in degrees, by which the UAV is offset
        Description: _alignUAV determines the angle the UAV is rotated by, when compared with the camera's world frame, and
                     rotates the UAV to better align with the camera. It does this by solving for the angle, theta, in the law of cosines form
                     a^2 = b^2 + c^2 - b*c*cos(theta) where a is the magnitude of the vector determined by the difference of the expected and 
                     end positions, b is the magnitude of the vector determined by the difference of the expected and start positions,
                     and c is the magnitude of the vector determined by the difference of the end and start positions. After the rotation, the 
                     camera is queried to insure that the UAV is still within the camera frame. If it is no longer detected, the UAV is instructed
                     to move upwards until the camera is able to positively detect it. If the UAV reaches the maximum height possible, the error
                     correction will make use of directional movements in the X-Y plane to attempt to relocate the UAV. If those fail, the UAV will
                     be instructed to land at its current position and the system will exit. 
        """ 
        #Find the magnitude of the expected change
        magnitudeExpected = math.sqrt(math.pow(expectedPosition[0]-startPosition[0],2) + math.pow(expectedPosition[1]-startPosition[1],2))

        #Find the magnitude of the actual change by subtracting start position from actual position
        magnitudeActual = math.sqrt(math.pow(endPosition[0]-startPosition[0],2) + math.pow(endPosition[1]-startPosition[1],2))

        #Find the magnitude of the difference between actual and expected
        magnitudeDiff = math.sqrt(math.pow(endPosition[0]-expectedPosition[0],2) + math.pow(endPosition[1]-expectedPosition[1],2))

        #If either of the magnitudes are equal to zero, return zero degrees
        if((magnitudeExpected == 0) or (magnitudeActual == 0)):
            return 0
        
        #Find angle between two vectors by solving the law of cosines form for the angle.
        internalVal = (math.pow(magnitudeExpected,2) + math.pow(magnitudeActual,2) - math.pow(magnitudeDiff,2))/(2*magnitudeExpected*magnitudeActual)
        angle = math.degrees(math.acos(internalVal))
        
        print("LPC: _alignUAV - startCoord =" + str(startPosition), file=self._debugFile)
        print("LPC: _alignUAV - expectedChange =" + str(expectedPosition), file=self._debugFile)
        print("LPC: _alignUAV - actual =" + str(endPosition), file=self._debugFile)
        print("LPC: _alignUAV - (magE, magA, magD) =" + str(magnitudeExpected) + "," + str(magnitudeActual) + "," + str(magnitudeDiff), file=self._debugFile)
        print("LPC: _alignUAV - internalVal =" + str(internalVal), file=self._debugFile)
        print("LPC: _alignUAV - angle =" + str(angle), file=self._debugFile)

        #Reduce angle to below 360 while preserving original sign value
        #This step is likely unnecessary as math.cos should return a value from zero to two pi
        angle = (angle/math.fabs(angle))*(math.fabs(angle)%360)

        #Reduce the angle to below 180 while preserving original sign value
        if(angle > 180):
            angle = angle - 360
        elif(angle < -180):
            angle = angle + 360

        self._uav.rotate(angle)

        #After alignment, if the UAV is not inside the vision cone, increase the height to preserve <x, y> position
        #Will need to make this error correction more robust to account for maximum height limitations
        while(self._uavInFrame() == False):
            self._sendMovement(0,0,self._hoverHeight*0.05)
        
        return angle
    
    def _getBatteryLevel(self):        
        """
        Function: _getBatteryLevel
        Purpose: Query the UAV to determine the battery percentage
        Inputs: None
        Outputs: a floating point value denote the battery percentage from zero to one hundred
        Description: Makes use of the UAV controller's built-in function to query the battery level
        """
        return self._uav.getBatteryLevel()
   
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
            test = serial.Serial(port, timeout=0.01)
            timeoutCount = 0
            while(test.read(1).decode('ascii') != expectedVals[-1] and timeoutCount <= len(expectedVals)*4):
                timeoutCount += 1
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
