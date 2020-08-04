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
    config.mmsPoller()

    videoObjectClassifier = VideoObjectClassifier(config, 0)
    videoObjectClassifier.process(0)

    # For additional camera add them as new source and process each one in different thread, WIP
    #videoObjectClassifier.addSource(1)
    #videoObjectClassifier.processThread(0)
    #videoObjectClassifier.processThread(1)

