import time

from threading import Thread

from package import Config
from package import Detector
from package import OpenCV
from package import VideoStream
from package import util

class VideoObjectClassifier:
    def __init__(self, config, source):
        self.videosources = []
        self.config = config
        self.videosources.append(source)

    def addSource(self, source):
        self.videosources.append(source)

    def process(self, sequence):
        videostream = VideoStream(self.config, self.videosources[sequence])
        detector = Detector(self.config)
        opencv = OpenCV()

        videostream.start()
        time.sleep(1)
        while True:
            # Get a frame in different states
            frame_current, frame_normalized, frame_faces, frame_gray = opencv.getFrame(self.config, detector, videostream)

            # Perform the actual inferencing with the initilized detector . tflite
            inference_interval = detector.infer(frame_normalized)

            # Get results
            boxes, classes, scores, num = detector.getResults()

            # Annotate the frame with class boundaries
            entities_dict = opencv.updateFrame(self.config, detector, opencv, frame_current, frame_faces, frame_gray, boxes, classes, scores, num)
    
            # Get full payload in json
            inference_data_json = detector.getInferenceDataJSON(self.config, inference_interval, entities_dict, frame_current)

            # Publish the result to kafka event stream
            if self.config.shouldPublishKafka():
                util.inference_publish(self.config.getPublishPayloadKafkaUrl(), inference_data_json)

            if self.config.shouldPublishStream():
                util.inference_publish(self.config.getPublishPayloadStreamUrl(), inference_data_json)

            # Update framerate
            opencv.updateFrameRate()

        videostream.stop()

    def processThread(self, sequence):
        Thread(target=self.process, args=(sequence,)).start()

        
