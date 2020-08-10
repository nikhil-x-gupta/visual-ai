#
# tflite_video_object_classifier.py
#
# OpenCV - image capture and image manipulation 
# TensorFlow Lite - object classification using coco_ssd_mobilenet_v1_1.0 model
# Kafka - send inferred meta data and annotated image to event stream
#
# Sanjeev Gupta, April 2020
#

import time

from package import Config
from package import VideoObjectClassifier

if __name__ == '__main__':

    config = Config(resolution=(640, 480), framerate=30)
    sources = config.discoverVideoDeviceSources(8) # Max number of /dev/videoX to discover for

    if len(sources) > 1:
        config.mmsPoller()
        
    ncamera = 1
    videoObjectClassifier = None
    for source in sources:
        if videoObjectClassifier is None:
            videoObjectClassifier = VideoObjectClassifier(config, "Camera " + str(ncamera), source)
        else:
            videoObjectClassifier.addVideoSource("Camera " + str(ncamera), source)

        videoObjectClassifier.processThread(source)

        ncamera += 1
        

