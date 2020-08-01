#
# tflite_Video_Clasifier.py
#
# OpenCV - image capture and image manipulation 
# TensorFlow Lite - object classification using coco_ssd_mobilenet_v1_1.0 model
# Kafka - send inferred meta data and annotated image to event stream
#
# Sanjeev Gupta, April 2020
#

import time

from package import Config
from package import VideoObjectClassifer

if __name__ == '__main__':
    config = Config(resolution=(640, 480), framerate=30)
    config.mmsPoller()
    time.sleep(1)
    VideoObjectClassifer(config, 1).process()

