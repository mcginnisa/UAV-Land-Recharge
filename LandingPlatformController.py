from UAVController import UAVController
import serial
import sys
import glob

class LandingPlatformController():
    
    def __init__(self, UAV=None, cameraInitValue='{900$900}\r\n'):
        #Define/Manage Serial connection
        self._camera = serial.Serial(self._getCameraSerialConnection(cameraInitValue))
        
        #Define/Manage UAV connection
        #self._uav = UAVController()
        self._uavPos = [-1, -1, -1]

    def _getUAVPosition(self):
        #Need to figure out serial data
        pass

    def _calculateOffset(self):
        offset = [0, 0, 0]
        curPosition = _getUAVPosition()
        offset[0] = curPosition[0] - cameraMidPoint[0]
        offset[1] = curPosition[1] - cameraMidPoint[1]
        offset[2] = curPosition[2] - cameraMidPoint[2]
        return offset

    def _sendMovement(self):
        pass

    def _performLandingSequence(self):
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
