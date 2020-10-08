#
# videoSourceProcessor.py
#
# Sanjeev Gupta, April 2020

from threading import Thread

from package import Config

from package.detect import TFLiteDetector
from package.detect import TFLiteOpenCV
from package.detect import VinoDetector
from package.detect import VinoOpenCV

from package.util import util

from . import VideoStream
from . import VideoSource

import time

class VideoSourceProcessor:
    def __init__(self, config, name, source):
        self.videoSources = []
        self.config = config
        self.videoSources.append(VideoSource(name, source))
        self.detector = None if config.getIsTFLite() else VinoDetector(config)
       
    def addVideoSource(self, name, source):
        self.videoSources.append(VideoSource(name, source))

    def process(self, index):
        videoSource = self.videoSources[index]
        videoStream = VideoStream(self.config, videoSource.getSource())
        videoStream.startThread()
        time.sleep(1)

        if self.config.getIsTFLite():
            print ("{:.7f} VideoSourceProcessor TFLite".format(time.time()))
            detector = TFLiteDetector(self.config)
            opencv = TFLiteOpenCV()

            while True:
                frame_current, frame_normalized, frame_faces, frame_gray = opencv.getFrame(self.config, videoStream, detector.getFloatingModel(), detector.getHeight(), detector.getWidth())

                inference_interval = detector.infer(frame_normalized)
                boxes, classes, scores, num = detector.getResults()
                entities_dict = opencv.annotateFrame(self.config, detector, frame_current, videoSource.getName(), frame_faces, frame_gray, boxes, classes, scores)
            
                if self.config.shouldShowOverlay():
                    opencv.addOverlay(frame_current, self.config.getTool(), self.config.getDeviceName(), inference_interval, opencv.getFrameRate())

                videoSource.frame_annotated = frame_current.copy()
    
                inference_data_json = opencv.getInferenceDataJSON(self.config, inference_interval, entities_dict, self.videoSources)

                if self.config.shouldPublishKafka():
                    util.inference_publish(self.config.getPublishPayloadKafkaUrl(), inference_data_json)

                if self.config.shouldPublishStream():
                    util.inference_publish(self.config.getPublishPayloadStreamUrl(), inference_data_json)

                opencv.updateFrameRate()

                if detector.getModelPath() != self.config.getModelPathTFLite():
                    detector = TFLiteDetector(self.config)

            videoStream.stop()

        else:
            print ("{:.7f} VideoSourceProcessor OpenVINO".format(time.time()))
            
            #detector = VinoDetector(self.config)
            opencv = VinoOpenCV()

            frameCount = 0;
            while True:
                frameCount += 1
                if frameCount % 100 == 0:
                    print (" frame processed {} ".format(frameCount))
                elif frameCount % 100 == 1:
                    print ("{:.7f} VideoSourceProcessor".format(time.time()), end="", flush=True)
                elif frameCount % 10 == 0:
                    print (" .", end = "", flush=True)

                frame_current, frame_norm, frame_faces, frame_gray, images, images_hw = opencv.getFrame(self.config, videoStream, self.detector.getN(), self.detector.getC(), self.detector.getHeight(), self.detector.getWidth())

                inference_interval, boxes, classes, scores = self.detector.getInferResults(images, images_hw, frame_current)

                entities_dict = opencv.annotateFrame(self.config, frame_current, videoSource.getName(), frame_faces, frame_gray, boxes, classes, scores)
            
                if self.config.shouldShowOverlay():
                    opencv.addOverlay(frame_current, self.config.getTool(), self.config.getDeviceName(), inference_interval, opencv.getFrameRate())

                videoSource.frame_annotated = frame_current.copy()
    
                inference_data_json = opencv.getInferenceDataJSON(self.config, inference_interval, entities_dict, self.videoSources)

                if self.config.shouldPublishKafka():
                    util.inference_publish(self.config.getPublishPayloadKafkaUrl(), inference_data_json)

                if self.config.shouldPublishStream():
                    util.inference_publish(self.config.getPublishPayloadStreamUrl(), inference_data_json)

                opencv.updateFrameRate()

                #if detector.getModelPath() != self.config.getModelPath():
                #    detector = VinoDetector(self.config)

            videoStream.stop()

    def processThread(self, index, threaded):
        if threaded:
            Thread(target=self.process, args=(index,)).start()
        else:
            self.process(index)

        
