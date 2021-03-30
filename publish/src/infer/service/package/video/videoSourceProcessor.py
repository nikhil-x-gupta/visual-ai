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
from package.detect import MVIDetector
from package.detect import MVIOpenCV

from package.util import util

from . import VideoStream
from . import VideoSource

import time

class VideoSourceProcessor:
    def __init__(self, config, name, source):
        self.videoSources = []
        self.config = config
        self.videoSources.append(VideoSource(name, source))
        self.detector = None
       
    def addVideoSource(self, name, source):
        self.videoSources.append(VideoSource(name, source))

    def process(self, index):
        videoSource = self.videoSources[index]
        videoStream = VideoStream(self.config, videoSource.getSource())
        videoStream.startThread()
        time.sleep(1)

        if self.config.getIsTFLite():
            print ("{:.7f} VideoSourceProcessor TFLite".format(time.time()), end="\n", flush=True)
            detector = TFLiteDetector(self.config)
            opencv = TFLiteOpenCV()
            while True:
                frame_current, frame_normalized, frame_faces, frame_gray = opencv.getFrame(self.config, videoStream, detector.getFloatingModel(), detector.getHeight(), detector.getWidth())
                inference_interval, boxes, classes, scores = detector.getInferResults(frame_normalized)
                self.update(self.config, self.videoSources, videoSource, detector, opencv, frame_current, frame_faces, frame_gray, boxes, classes, scores, inference_interval)
                if detector.getModelPath() != self.config.getModelPathTFLite():
                    detector = TFLiteDetector(self.config)
            videoStream.stop()

        elif self.config.getIsVino():
            print ("{:.7f} VideoSourceProcessor OpenVINO".format(time.time()), end="\n", flush=True)
            detector = VinoDetector(self.config)
            opencv = VinoOpenCV()
            while True:
                frame_current, frame_normalized, frame_faces, frame_gray, images, images_hw = opencv.getFrame(self.config, videoStream, detector.getN(), detector.getC(), detector.getHeight(), detector.getWidth())
                inference_interval, boxes, classes, scores = detector.getInferResults(images, images_hw, frame_current)
                self.update(self.config, self.videoSources, videoSource, detector, opencv, frame_current, frame_faces, frame_gray, boxes, classes, scores, inference_interval)
                #if detector.getModelPath() != self.config.getModelPath():
                #    detector = VinoDetector(self.config)
            videoStream.stop()

        elif self.config.getIsMVI():
            print ("{:.7f} VideoSourceProcessor MVI".format(time.time()), end="\n", flush=True)
            detector = MVIDetector(self.config)
            opencv = MVIOpenCV()
            while True:
                frame_current, frame_normalized, frame_faces, frame_gray = opencv.getFrame(self.config, videoStream, detector.getFloatingModel(), detector.getHeight(), detector.getWidth())
                inference_interval, boxes, classes, scores = detector.getInferResults(frame_current, index, opencv)
                self.update(self.config, self.videoSources, videoSource, detector, opencv, frame_current, frame_faces, frame_gray, boxes, classes, scores, inference_interval)
                #if detector.getModelPath() != self.config.getModelPath():
                #    detector = VinoDetector(self.config)

            videoStream.stop()

    def processThread(self, index, threaded):
        if threaded:
            Thread(target=self.process, args=(index,)).start()
        else:
            self.process(index)

    def update(self, config, video_sources, video_source, detector, opencv, frame_current, frame_faces, frame_gray, boxes, classes, scores, inference_interval):
        entities_dict = opencv.annotateFrame(config, detector, frame_current, video_source.getName(), frame_faces, frame_gray, boxes, classes, scores)
        if config.shouldShowOverlay():
            opencv.addOverlay(frame_current, config.getTool(), config.getDeviceName(), inference_interval, opencv.getFrameRate())
        video_source.frame_annotated = frame_current.copy()
        inference_data_json = opencv.getInferenceDataJSON(config, inference_interval, entities_dict, video_sources)
        if config.shouldPublishKafka():
            util.inference_publish(config.getPublishPayloadKafkaUrl(), inference_data_json)
        if config.shouldPublishStream():
            util.inference_publish(config.getPublishPayloadStreamUrl(), inference_data_json)
        opencv.updateFrameRate()
