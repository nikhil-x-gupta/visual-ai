import time

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
        self.frame_current = None
        self.entities_dict = None
        self.inference_interval = None

    def getSource(self):
        return self.source

class VideoObjectClassifier:
    def __init__(self, config, name, source):
        self.videoSources = []
        self.config = config
        self.videoSources.append(VideoSource(name, source))
       
    def addVideoSource(self, name, source):
        self.videoSources.append(VideoSource(name, source))

    def process(self, sequence):
        videoSource = self.videoSources[sequence]
        videoStream = VideoStream(self.config, videoSource.getSource())
        detector = Detector(self.config)
        opencv = OpenCV()

        videoStream.start()
        time.sleep(1)
        while True:
            # Get a frame in different states
            videoSource.frame_current, frame_normalized, frame_faces, frame_gray = opencv.getFrame(self.config, detector, videoStream)

            # Perform the actual inferencing with the initilized detector . tflite
            videoSource.inference_interval = detector.infer(frame_normalized)

            # Get results
            boxes, classes, scores, num = detector.getResults()

            # Annotate the frame with class boundaries
            videoSource.entities_dict = opencv.updateFrame(self.config, detector, opencv, videoSource.frame_current, frame_faces, frame_gray, boxes, classes, scores, num)
    
            # Get full payload in json
            inference_data_json = detector.getInferenceDataJSON(self.config, videoSource.inference_interval, videoSource.entities_dict, videoSource.frame_current, self.videoSources)

            # Publish the result to kafka event stream
            if self.config.shouldPublishKafka():
                util.inference_publish(self.config.getPublishPayloadKafkaUrl(), inference_data_json)

            if self.config.shouldPublishStream():
                util.inference_publish(self.config.getPublishPayloadStreamUrl(), inference_data_json)

            # Update framerate
            opencv.updateFrameRate()

        videoStream.stop()

    def processThread(self, sequence):
        Thread(target=self.process, args=(sequence,)).start()

        
