import time
import numpy as np

from threading import Thread

from package import Config
from package import Detector
from package import OpenCV
from package import VideoStream
from package import util

class VideoSource:
    def __init__(self, name, source):
        self.name = name
        self.source = source
        self.frame_annotated = None
        
    def getName(self):
        return self.name

    def getSource(self):
        return self.source

class VideoObjectClassifier:
    def __init__(self, config, name, source):
        self.videoSources = []
        self.config = config
        self.videoSources.append(VideoSource(name, source))
       
    def addVideoSource(self, name, source):
        self.videoSources.append(VideoSource(name, source))

    def process(self, index):
        videoSource = self.videoSources[index]
        videoStream = VideoStream(self.config, videoSource.getSource())
        detector = Detector(self.config)
        opencv = OpenCV()

        videoStream.start()
        time.sleep(1)
        while True:
            # Get a frame in different states
            frame_current, frame_normalized, frame_faces, frame_gray = opencv.getFrame(self.config, detector, videoStream)

            # Perform the actual inferencing with the initilized detector . tflite
            inference_interval = detector.infer(frame_normalized)

            # Get results
            boxes, classes, scores, num = detector.getResults()

            # Annotate the frame with class boundaries
            entities_dict = opencv.annotateFrame(self.config, detector, opencv, frame_current, videoSource.getName(), frame_faces, frame_gray, boxes, classes, scores, num)
            
            if self.config.shouldShowOverlay():
                opencv.addOverlay(frame_current, self.config.getTool(), self.config.getDeviceName(), inference_interval, opencv.getFrameRate())

            videoSource.frame_annotated = frame_current.copy()
    
            # Get full payload in json
            inference_data_json = opencv.getInferenceDataJSON(self.config, inference_interval, entities_dict, self.videoSources)

            # Publish the result to kafka event stream
            if self.config.shouldPublishKafka():
                util.inference_publish(self.config.getPublishPayloadKafkaUrl(), inference_data_json)

            if self.config.shouldPublishStream():
                util.inference_publish(self.config.getPublishPayloadStreamUrl(), inference_data_json)

            # Update framerate
            opencv.updateFrameRate()

        videoStream.stop()

    def processThread(self, index):
        Thread(target=self.process, args=(index,)).start()

        
