#
# videoStream.py
#
# Sanjeev Gupta, April 2020

from threading import Thread

import cv2
import time

class VideoStream:
    def __init__(self, config, source, captureInterval=0.01):
        print ("{:.7f} VideoStream initializing".format(time.time()))
        self.captureInterval = captureInterval
        self.videoCapture = cv2.VideoCapture(source)
        ret = self.videoCapture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.videoCapture.set(3, config.getResolutionWidth())
        ret = self.videoCapture.set(4, config.getResolutionHeight())

        (self.grabbed, self.frame) = self.videoCapture.read()

        self.stopped = False
        print ("{:.7f} VideoStream initialized".format(time.time()))

    def startThread(self):
        Thread(target=self.setup, args=()).start()
        print ("{:.7f} VideoStream thread started".format(time.time()))

    def stop(self):
        self.stopped = True

    def read(self):
        return self.frame

    def setup(self):
        print ("{:.7f} VideoStream setup".format(time.time()))
        while True:
            if self.stopped:
                self.videoCapture.release()
                return
            else:
                try:
                    (self.grabbed, self.frame) = self.videoCapture.read()
                    time.sleep(self.captureInterval)
                except cv2.error as e:
                    print(e)
