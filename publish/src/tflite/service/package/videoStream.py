#
# videoStream.py
#
# Sanjeev Gupta, April 2020

from threading import Thread

import cv2
import time

class VideoStream:
    def __init__(self, config, source):
        self.videoCapture = cv2.VideoCapture(source)
        ret = self.videoCapture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.videoCapture.set(3, config.getResolutionWidth())
        ret = self.videoCapture.set(4, config.getResolutionHeight())

        (self.grabbed, self.frame) = self.videoCapture.read()

        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def stop(self):
        self.stopped = True

    def read(self):
        return self.frame

    def update(self):
        while True:
            if self.stopped:
                self.videoCapture.release()
                return
            else:
                (self.grabbed, self.frame) = self.videoCapture.read()
                time.sleep(0.02)
