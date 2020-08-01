import time

from package import Config
from package import Detector
from package import OpenCV
from package import VideoStream
from package import util

class VideoObjectClassifier:
    def __init__(self, config, source):
        self.videostreams = []
        self.config = config
        self.detector = Detector(self.config)
        self.opencv = OpenCV()
        self.videostreams.append(VideoStream(self.config, source))

    def addStream(self, source):
        self.videostreams.append(VideoStream(self.config, source))

    def process(self, sequence):
        self.videostreams[sequence].start()
        time.sleep(1)
        while True:
            # Get a frame in different states
            frame_current, frame_normalized, frame_faces, frame_gray = self.opencv.getFrame(self.config, self.detector, self.videostreams[sequence])

            # Perform the actual inferencing with the initilized detector . tflite
            inference_interval = self.detector.infer(frame_normalized)

            # Get results
            boxes, classes, scores, num = self.detector.getResults()

            # Annotate the frame with class boundaries
            entities_dict = self.opencv.updateFrame(self.config, self.detector, self.opencv, frame_current, frame_faces, frame_gray, boxes, classes, scores, num)
    
            # Get full payload in json
            inference_data_json = self.detector.getInferenceDataJSON(self.config, inference_interval, entities_dict, frame_current)

            # Publish the result to kafka event stream
            if self.config.shouldPublishKafka():
                util.inference_publish(self.config.getPublishPayloadKafkaUrl(), inference_data_json)

            if self.config.shouldPublishStream():
                util.inference_publish(self.config.getPublishPayloadStreamUrl(), inference_data_json)

            # Update framerate
            self.opencv.updateFrameRate()

        self.videostreams[sequence].stop()

    # TODO
    def processThread(self, sequence):
        Thread(target=self.process, args=(sequence)).start()

        
