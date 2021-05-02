
#
# videoStream.py
#
# Sanjeev Gupta, April 2020

from threading import Thread

import cv2
import time

class VideoStream:
    def __init__(self, config, videoSource, index, captureInterval=0.01):
        print ("{:.7f} VideoStream initializing index ".format(time.time()), index, end="\n", flush=True)
        self.videoSource = videoSource
        self.captureInterval = captureInterval

        self.videoCapture = cv2.VideoCapture(videoSource.getSource())
        (self.grabbed, self.frame) = self.videoCapture.read()
        while not self.grabbed:
            time.sleep(0.5)
            (self.grabbed, self.frame) = self.videoCapture.read()

        videoSource.setIndex(index)
        videoSource.setResolution((int(self.videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))))

        self.stopped = False
        print ("{:.7f} VideoStream initialized index resolution".format(time.time()), index, videoSource.getResolution(), end="\n", flush=True)

    def startThread(self):
        Thread(target=self.setup, args=()).start()
        print ("{:.7f} VideoStream thread started".format(time.time()), self.videoSource.getName(), self.videoSource.getIndex(),end="\n", flush=True)

    def stop(self):
        self.stopped = True

    def read(self):
        return self.frame

    def setup(self):
        print ("{:.7f} VideoStream setup props CAP_PROP_FRAME_WIDTH".format(time.time()), self.videoSource.getName(), self.videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH), end="\n", flush=True)
        print ("{:.7f} VideoStream setup props CAP_PROP_PROP_FPS ".format(time.time()), self.videoSource.getName(), self.videoCapture.get(cv2.CAP_PROP_FPS), end="\n", flush=True)
        print ("{:.7f} VideoStream setup props CAP_PROP_FOURCC".format(time.time()), self.videoSource.getName(), self.videoCapture.get(cv2.CAP_PROP_FOURCC), end="\n", flush=True)
        print ("{:.7f} VideoStream setup props CAP_PROP_FRAME_COUNT".format(time.time()), self.videoSource.getName(), self.videoCapture.get(cv2.CAP_PROP_FRAME_COUNT), end="\n", flush=True)
        #while self.videoSource.isOpened():
        while True:
            if self.stopped:
                self.videoCapture.release()
                return
            else:
                try:
                    (self.grabbed, self.frame) = self.videoCapture.read()
                    if self.videoSource.getSourceType() == 'file':
                        if self.grabbed is False:
                            ret = self.videoCapture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            self.grabbed = True
                    time.sleep(self.captureInterval)
                except cv2.error as e:
                    print ("{:.7f} VideoStream setup error".format(time.time()), self.videoSource.getName(), self.videoSource.getSourceType(), e, end="\n", flush=True)
