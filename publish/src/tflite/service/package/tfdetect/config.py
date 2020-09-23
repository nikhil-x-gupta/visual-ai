#
# config.py
#
# Sanjeev Gupta, April 2020

from threading import Thread

import cv2
import datetime
import numpy 
import os
import requests
import time

class Config:
    def __init__(self, resolution=(640, 480), framerate=30):
        self.resolution = resolution
        self.framerate = framerate

        b_frame_border = 8
        bg_color = [32, 32, 32]
        b_frame = numpy.zeros([self.resolution[1] - 2 * b_frame_border, self.resolution[0] - 2 * b_frame_border, 3], dtype=numpy.uint8)
        b_frame[:] = (48, 48, 48) # gray fill
        self.blankFrame = cv2.copyMakeBorder(b_frame, b_frame_border, b_frame_border, b_frame_border, b_frame_border, cv2.BORDER_CONSTANT, value=bg_color)

        self.env_dict = {}
        self.env_dict['SHOW_OVERLAY'] = os.environ['SHOW_OVERLAY'] if 'SHOW_OVERLAY' in os.environ else True
        self.env_dict['DETECT_FACE'] = os.environ['DETECT_FACE'] if 'DETECT_FACE' in os.environ else True
        self.env_dict['BLUR_FACE'] = os.environ['BLUR_FACE'] if 'BLUR_FACE' in os.environ else True
        self.env_dict['PUBLISH_KAFKA'] = os.environ['PUBLISH_KAFKA'] if 'PUBLISH_KAFKA' in os.environ else False
        self.env_dict['PUBLISH_STREAM'] = os.environ['PUBLISH_STREAM'] if 'PUBLISH_STREAM' in os.environ else True

        # os.path.join - leading / only for the first path. NO leading / in sub paths
        self.defaultModelDir = "/model"
        self.defaultModel = "detect.tflite"
        self.defaultLabelmap = "labelmap.txt"

        self.modelDir = None
        self.model = None
        self.labelmap = None

        self.modelObjectType = None
        self.modelObjectId = None
        self.modelNet = None
        self.modelFmwk = None
        self.modelVersion = None

        self.modelUpdatedAt = datetime.datetime.now()

    def getRTSPStreams(self):
        rtspStr = os.environ['RTSP_STREAMS'] if 'RTSP_STREAMS' in os.environ else ''
        rtsps =  (rtspStr.replace(" ", "")).split(",")
        rtsp = [rtsp for rtsp in rtsps if "rtsp" in rtsp]  
        return rtsps if rtsp else None

    def getRTSPIP(self, rtsp):
        x = rtsp.split(":")
        x = x[1].strip("/")
        return x

    def getViewColumn(self):
        return int(os.environ['VIEW_COLUMN'] if 'VIEW_COLUMN' in os.environ else '1')

    def getBlankFrame(self):
        return self.blankFrame

    def discoverVideoDeviceSources(self, bound):
        deviceSources = []
        for source in range(0, bound):
            vcap = cv2.VideoCapture(source)
            if vcap.read()[0]:
                deviceSources.append(source)
                vcap.release()

        return deviceSources

    def getDeviceId(self):
        return os.environ['DEVICE_ID'] if 'DEVICE_ID' in os.environ else 'DEVICE_ID'
    
    def getDeviceName(self):
        return os.environ['DEVICE_NAME'] if 'DEVICE_NAME' in os.environ else 'DEVICE_NAME'
    
    def getMMSConfigProviderUrl(self):
        url = "http://" + os.environ['DEVICE_IP_ADDRESS'] + ":7778/mmsconfig"
        return url

    def getMMSModelProviderUrl(self):
        url = "http://" + os.environ['DEVICE_IP_ADDRESS'] + ":7778/mmsmodel"
        return url

    def getPublishPayloadKafkaUrl(self):
        return os.environ['HTTP_PUBLISH_KAFKA_URL'] if 'HTTP_PUBLISH_KAFKA_URL' in os.environ else 'Missing HTTP_PUBLISH_KAFKA_URL'

    def getPublishPayloadStreamUrl(self):
        return os.environ['HTTP_PUBLISH_STREAM_URL'] if 'HTTP_PUBLISH_STREAM_URL' in os.environ else 'Missing HTTP_PUBLISH_STREAM_URL'

    def getMinConfidenceThreshold(self):
        return float(os.environ['MIN_CONFIDENCE_THRESHOLD'] if 'MIN_CONFIDENCE_THRESHOLD' in os.environ else "0.6")

    def shouldShowOverlay(self):
        return self.env_dict['SHOW_OVERLAY'] == 'true'

    def shouldPublishKafka(self):
        return self.env_dict['PUBLISH_KAFKA'] == 'true'

    def shouldPublishStream(self):
        return self.env_dict['PUBLISH_STREAM'] == 'true'
    
    def shouldDetectFace(self):
        return self.env_dict['DETECT_FACE']  == 'true'

    def shouldBlurFace(self):
        return self.env_dict['BLUR_FACE']  == 'true'

    def getResolution(self):
        return self.resolution

    def getFramerate(self):
        return self.framerate

    def getResolutionWidth(self):
        return self.resolution[0]

    def getResolutionHeight(self):
        return self.resolution[1]

    def getTool(self):
        return "OpenCV TensorFlow Lite"

    def getModelDir(self):
        return self.defaultModelDir if self.modelDir is None else self.modelDir

    def getModel(self):
        return self.defaultModel if self.model is None else self.model

    def getLabelmap(self):
        return self.defaultLabelmap if self.labelmap is None else self.labelmap

    def getModelPath(self):
        return os.path.join(self.getModelDir(), self.getModel())

    def getLabelmapPath(self):
        return os.path.join(self.getModelDir(), self.getLabelmap())

    def getInputMean(self):
        return 127.5

    def getInputStd(self):
        return 127.5

    def getStatusText(self):
        #   return "Default" if self.modelObjectId is None else self.modelObjectId
        ts = self.modelUpdatedAt.strftime("%Y-%m-%d %H:%M:%S")
        if self.modelObjectId is None:
            return "Default" + " " + ts
        else:
            return self.modelObjectId + " " + ts
    
    def mmsConfig(self):
        url = self.getMMSConfigProviderUrl()
        try:
            resp = requests.get(url)
            dict = resp.json()
            if dict['mms_action'] == 'updated':
                value_dict = dict['value']
                if 'SHOW_OVERLAY' in value_dict:
                    self.env_dict['SHOW_OVERLAY'] = value_dict['SHOW_OVERLAY']

                if 'PUBLISH_KAFKA' in value_dict:
                    self.env_dict['PUBLISH_KAFKA'] = value_dict['PUBLISH_KAFKA']

                if 'PUBLISH_STREAM' in value_dict:
                    self.env_dict['PUBLISH_STREAM'] = value_dict['PUBLISH_STREAM']

                if 'DETECT_FACE' in value_dict:
                    self.env_dict['DETECT_FACE'] = value_dict['DETECT_FACE']

                if 'BLUR_FACE' in value_dict:
                    self.env_dict['BLUR_FACE'] = value_dict['BLUR_FACE']

        except requests.exceptions.HTTPError as errh:
            print ("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else", err)

    #{"mms_action":"updated","value":{"OBJECT_TYPE":"tflite-mmsmodel","OBJECT_ID":"mobilenet-tflite-1.0.0-mms.tar.gz","MODEL_NET":"mobilenet","MODEL_FMWK":"tflite","MODEL_VERSION":"1.0.0","MODEL_DIR":"/var/tmp/horizon/tflite-mmsmodel/mobilenet/tflite/1.0.0/files","FILES":"detect.tflite labelmap.txt"}}
    def mmsModel(self):
        url = self.getMMSModelProviderUrl()
        try:
            resp = requests.get(url)
            dict = resp.json()
            if dict['mms_action'] == 'updated':
                value_dict = dict['value']
                self.modelObjectType = value_dict['OBJECT_TYPE']
                self.modelObjectId = value_dict['OBJECT_ID']
                self.modelNet = value_dict['MODEL_NET']
                self.modelFmwk = value_dict['MODEL_FMWK']
                self.modelVersion = value_dict['MODEL_VERSION']
                self.modelDir = value_dict['MODEL_DIR']

                files = value_dict['FILES'].split(" ")
                for file in files:
                    if(file.startswith("labelmap.")):
                        self.labelmap = file
                    elif(file.endswith(".tflite")):
                        self.model = file

                self.modelUpdatedAt = datetime.datetime.now()

        except requests.exceptions.HTTPError as errh:
            print ("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else", err)

    def mmsProcessor(self):
        while True:
            time.sleep(1)
            #if self.shouldRefreshModel is None:
            self.mmsConfig()
            time.sleep(1)
            self.mmsModel()

    def mmsPoller(self):
        Thread(target=self.mmsProcessor, args=()).start()

    """
    def mmsConfigProcessor(self):
        while True:
            time.sleep(1)
            self.mmsConfig()

    def mmsModelProcessor(self):
        while True:
            time.sleep(1)
            self.mmsModel()

    def mmsConfigPoller(self):
        Thread(target=self.mmsConfigProcessor, args=()).start()

    def mmsModelPoller(self):
        Thread(target=self.mmsModelProcessor, args=()).start()
    """
            
