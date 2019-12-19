class LandingPlatformController():
    cameraMidpoint = [0, 0, 0]
    
    def __init__(self, UAV=None):
        self._uav = UAV
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
    
    
