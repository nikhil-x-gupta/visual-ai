#
# videoSource.py
#
# Sanjeev Gupta, April 2020

class VideoSource:
    def __init__(self, name, source):
        self.name = name
        self.source = source
        self.frame_annotated = None
        
    def getName(self):
        return self.name

    def getSource(self):
        return self.source

