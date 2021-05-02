#
# videoSource.py
#
# Sanjeev Gupta, April 2020

class VideoSource:
    def __init__(self, sourceType, source, name):
        self.sourceType = sourceType
        self.source = source
        self.name = name
        self.index = None
        self.resolution = None
        self.detector = None
        self.frame_annotated = None
        
    def getSourceType(self):
        return self.sourceType

    def getSource(self):
        return self.source

    def getName(self):
        return self.name

    def setIndex(self, index):
        self.index = index

    def getIndex(self):
        return self.index

    def setResolution(self, resolution):
        self.resolution = resolution

    def getResolution(self):
        return self.resolution

    def getResolutionWidth(self):
        return self.resolution[0]

    def getResolutionHeight(self):
        return self.resolution[1]

    def setDetector(self, detector):
        self.detector = detector
 
    def getDetector(self):
        return self.detector

    
