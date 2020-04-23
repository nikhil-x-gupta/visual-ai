#
# tflite_webcam_image.py
#
# OpenCV - image capture and image manipulation 
# TensorFlow Lite - object classification using coco_ssd_mobilenet_v1_1.0 model
# Kafka - send inferred meta data and annotated image to event stream
#
# Sanjeev Gupta, April 2020
#


import os
import time

from package import Config
from package import Detector
from package import OpenCV
from package import VideoStream
from package import util

config = Config(resolution=(640, 480), framerate=30)
detector = Detector(config)
opencv = OpenCV()
videostream = VideoStream(config).start()

time.sleep(1)

while True:
    # Get frame from the videostream
    current_frame, frame_normalized = opencv.getFrame(config, detector, videostream)

    # Perform the actual inferencing with the initilized detector . tflite
    inference_interval = detector.infer(frame_normalized)

    # Get results
    boxes, classes, scores, num = detector.getResults()
    
    # Annotate the frame with class boundaries
    entities_dict = opencv.updateFrame(config, detector, opencv, current_frame, boxes, classes, scores, num)
    
    # Get full payload in json
    inference_data_json = detector.getInferenceDataJSON(config, inference_interval, entities_dict, current_frame)

    # Publish the result to kafka event stream
    #    util.inference_publish(config.getPublishPayloadKafkaUrl(), inference_data_json)

    util.inference_publish(config.getPublishPayloadStreamUrl(), inference_data_json)

    # Update framerate
    opencv.updateFrameRate()

videostream.stop()
