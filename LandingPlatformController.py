from UAVController import UAVController
import serial
import sys
import glob

class LandingPlatformController():
    
    def __init__(self, UAV=None, cameraInitValue='{900$900}\r\n', defaultHoverHeight=0.3, defaultVelocity=0.1):
        #Define/Manage UAV connection
        if(UAV == None):
            print("ERROR: Landing Platform Controller requires a UAV control object")
            
        #Define class constants
        self._uav = UAV
        self._uavVelocity = defaultVelocity #Find out default velocity
        self._hoverHeight = defaultHoverHeight
        self._uavPos = [-1, -1, -1]
        self._landingPos = [-1, -1, -1] #Will need to be defined somehow
        self._cameraInitValue = cameraInitvalue
        
        #Define/Manage Serial connection
        self._camera = serial.Serial(self._getCameraSerialConnection(cameraInitValue))

    def _getUAVPosition(self):
        """
        Function: _getUAVPosition
        Purpose: Get the most up-to-date UAV position in rectangular coordinates
        Inputs: None
        Outputs: curPosition - an array of floating point values representing <x, y, z>
        """
        #Need to figure out serial data
        self._uavPos = [-1, -1 , -1]
        self._uavPos[2] = self._uavGetHeight()
        #Parse serial data
        #Flush camera bus
        positionString=""
        while(self._camera.read(1).decode('ascii') != '{'): {""" Do nothing """}
        while(self._camera.read(1).decode('ascii') != '}'): { positionString = positionString + self._camera.read(1).decode('ascii') }
        splitIndex=positionString.rfind("%") #Make sure this hard code is changed later
        pixelX = float(positionString[:splitIndex])
        pixelY = float(positionString[(splitIndex+1):])
        return

    def _calculateOffset(self):
        """
        Function: _calculateOffset
        Purpose: Calculate the offset distance of the UAV to the desired landing point
        Inputs: None
        Outputs: offset - an array of values representing <dx, dy, dz> 
        """
        offset = [0, 0, 0]
        curPosition = self._getUAVPosition()
        offset[0] = curPosition[0] - self._landingPos[0]
        offset[1] = curPosition[1] - self._landingPos[1]
        offset[2] = curPosition[2] - self._landingPos[2]
        return offset

    def _uavGetHeight(self):
        """
        Function: _uavGetHeight
        Purpose: Get the UAV z-coordinate in the world frame
        Inputs: None
        Outputs: a floating point value representing the z-coordinate 
        """
        return self._hoverHeight

    def _sendMovement(self, xpos, ypos, zpos):
        """
        Function: _sendMovement
        Purpose: Instruct the UAV to move to certain coordinates
        Inputs: xpos - a floating point value denoting the new x position to move towards
                ypos - a floating point value denoting the new y position to move towards
                zpos - a floating point value denoting the new z position to move towards
        Outputs: None
        """
        self.uav.move(xpos, ypos, zpos, self._uavVelocity)
        pass

    def _performLandingSequence(self):
        """
        Function: _performLandingSequence
        Purpose: Instruct the UAV to land fully once centered
        Inputs: None
        Outputs: None
        """
        self.uav.land()
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

if True:
    Test = LandingPlatformController()
