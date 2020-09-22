#
# tfliteVideoObjectDetector.py
#
# An implementation using IBM Edge Application Manager (IEAM) to deploy container workloads on edge nodes
#
# IEAM - containers deployment and life cycle management
# IEAM Deployment Policy - policy based
# IEAM MMS - Model Management System for machine inferencing model deployments to edge nodes
#
# OpenCV - image capture and image manipulation 
# TensorFlow Lite - object classification using coco_ssd_mobilenet_v1_1.0 model
# Kafka - send inferred meta data and annotated image to event stream
#
# Sanjeev Gupta, April 2020
#
# - A simple video device discoverer connected via USB
# - Consumes RTSP streams additionally
# - Python threads for each video source feed
#   - OpenCV based video capture
#   - mobilenet tflite based object detector
#   - OpenCV for image annotation
#   - Dynamic consolidation of each video streams in presentation frame
#   - Configutable horizontal and vertical layout 
# - Local viewing over http
# - Result streaming to Kafka based event stream 
# - Result visualization in grafana after processing via cloud function
# - Separate threads for MMS based configuration and model updates

from package import Config
from package import VideoSourceProcessor

if __name__ == '__main__':

    videoSourceProcessor = None
    config = Config(resolution=(640, 480), framerate=30)

    sources = []
    sources.extend(config.discoverVideoDeviceSources(8)) # Max number of /dev/videoX to discover for

    rtsps = config.getRTSPStreams() # A list of RTSP sources passed to container via user-input
    if rtsps is not None:
        sources.extend(rtsps)

    index = 0
    for source in sources:
        src_sfx = "    " + source if str(source).startswith("rtsp:") else "    /dev/video" + str(source)
        sourceName = "Camera " + str(index + 1) + src_sfx
        if videoSourceProcessor is None:
            videoSourceProcessor = VideoSourceProcessor(config, sourceName, source)
        else:
            videoSourceProcessor.addVideoSource(sourceName, source)

        videoSourceProcessor.processThread(index)
        index += 1

    if videoSourceProcessor is not None:
        config.mmsPoller()
        
    
