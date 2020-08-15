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
    deviceSources = config.discoverVideoDeviceSources(8) # Max number of /dev/videoX to discover for

    videoObjectClassifier = None

    index = 0
    for source in deviceSources:
        sourceName = "Camera " + str(index + 1) + "    /dev/video" + str(source)
        if videoObjectClassifier is None:
            videoObjectClassifier = VideoObjectClassifier(config, sourceName, source)
        else:
            videoObjectClassifier.addVideoSource(sourceName, source)

        videoObjectClassifier.processThread(index)
        index += 1
        
    rtspStreams = config.getRTSPStreams()
    for source in rtspStreams:
        sourceName = "Camera " + str(index + 1) + "    RTSP " + config.getRTSPIP(source)
        if videoObjectClassifier is None:
            videoObjectClassifier = VideoObjectClassifier(config, sourceName, source)
        else:
            videoObjectClassifier.addVideoSource(sourceName, source)

        videoObjectClassifier.processThread(index)
        index += 1

    if videoObjectClassifier is not None:
        config.mmsConfigPoller()
        config.mmsModelPoller()
        
    
