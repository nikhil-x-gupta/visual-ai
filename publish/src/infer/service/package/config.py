#
# config.py
#
# Sanjeev Gupta, April 2020

from threading import Thread

import numpy 
import cv2
import datetime
import json
import os
import requests
import time
import zipfile

class Config:
    def __init__(self, fmwk, framerate=30):
        self.fmwk = fmwk
        self.framerate = framerate

        # seed resolution for blankFrame to be used as base blankFrame
        resolution = (640, 480)
        b_frame_border = 8
        bg_color = [32, 32, 32]
        b_frame = numpy.zeros([resolution[1] - 2 * b_frame_border, resolution[0] - 2 * b_frame_border, 3], dtype=numpy.uint8)
        b_frame[:] = (48, 48, 48) # gray fill
        self.blankFrame = cv2.copyMakeBorder(b_frame, b_frame_border, b_frame_border, b_frame_border, b_frame_border, cv2.BORDER_CONSTANT, value=bg_color)
        
        self.env_dict = {}
        self.env_dict['SHOW_OVERLAY'] = os.environ['SHOW_OVERLAY'] if 'SHOW_OVERLAY' in os.environ else True
        self.env_dict['DETECT_FACE'] = os.environ['DETECT_FACE'] if 'DETECT_FACE' in os.environ else True
        self.env_dict['BLUR_FACE'] = os.environ['BLUR_FACE'] if 'BLUR_FACE' in os.environ else False
        self.env_dict['PUBLISH_KAFKA'] = os.environ['PUBLISH_KAFKA'] if 'PUBLISH_KAFKA' in os.environ else False
        self.env_dict['PUBLISH_STREAM'] = os.environ['PUBLISH_STREAM'] if 'PUBLISH_STREAM' in os.environ else True

        self.modelDir = None

        self.modelObjectType = None
        self.modelObjectId = None
        self.modelNet = None
        self.modelFmwk = None
        self.modelVersion = None

        self.modelUpdatedAt = datetime.datetime.now()
        self.reloadTFLiteModel = False
        self.reloadPTHModel = False
        self.detectorInitialized = False

        if self.getIsVino():
            self.setVinoDefaults()
        elif self.getIsMVI():
            self.setMVIDefaults()
        elif self.getIsPTH():
            self.setPTHDefaults()
        else:
            self.setTFLiteDefaults()

        print ("{:.7f} Config initialized".format(time.time()))

    def setDetectorInitialized(self, flag):
        self.detectorInitialized = flag

    def getDetectorInitialized(self):
        return self.detectorInitialized
        
    def getIsTFLite(self):
        return self.fmwk == 'tflite'

    def getIsPTH(self):
        return self.fmwk == 'pth'

    def getIsVino(self):
        return self.fmwk == 'vino'

    def getIsMVI(self):
        return self.fmwk == 'mvi'

    # os.path.join - leading / only for the first path. NO leading / in sub paths
    def setTFLiteDefaults(self):
        self.detectTFLite = "detect.tflite"
        self.labelmap = "labelmap.txt"
        self.tool = "TensorFlow Lite OpenCV"
        self.modelTFLite = None
        self.defaultModelDir = os.environ['APP_MODEL_DIR']
        self.defaultModelTFLite = "default-" + os.environ['APP_MODEL_TFLITE']
        self.modelObjectId = self.defaultModelTFLite
        with zipfile.ZipFile(os.path.join(self.defaultModelDir, self.defaultModelTFLite), 'r') as zip_ref:
            zip_ref.extractall(self.defaultModelDir)
        
    def setPTHDefaults(self):
        self.tool = "Pytorch OpenCV"
        self.modelPTH = None
        self.defaultModelDir = os.environ['APP_MODEL_DIR']
        self.defaultModelPTH = "default-" + os.environ['APP_MODEL_PTH']
        self.modelObjectId = self.defaultModelPTH

    def setMVIDefaults(self):
        self.tool = "MVI OpenCV"
        self.modelObjectId = os.environ['APP_MI_MODEL'] 

    def setVinoDefaults(self):
        self.tool = "OpenVINO OpenCV"
        self.modelXML = None
        self.modelBin = None
        self.defaultModelDir = os.environ['APP_MODEL_DIR']
        self.defaultModelXML = os.environ['APP_MODEL_XML']
        self.defaultModelBin = os.environ['APP_MODEL_BIN']
        self.modelObjectId = self.defaultModelXML.split('.')[0]
        self.objectName = "Face"

    def getObjectName(self):
        return self.objectName

    def getModelDir(self):
        return self.defaultModelDir if self.modelDir is None else self.modelDir

    def getModelPTH(self):
        return self.defaultModelPTH if self.modelPTH is None else self.modelPTH

    def getModelTFLite(self):
        return self.defaultModelTFLite if self.modelTFLite is None else self.modelTFLite

    def getLabelmap(self):
        return self.labelmap

    def getModelXML(self):
        return self.defaultModelXML if self.modelXML is None else self.modelXML

    def getModelBin(self):
        return self.defaultModelBin if self.modelBin is None else self.modelBin

    def getModelPathPTH(self):
        return os.path.join(self.getModelDir(), self.getModelPTH())

    def getModelPathTFLite(self):
        return os.path.join(self.getModelDir(), self.detectTFLite)

    def getLabelmapPath(self):
        return os.path.join(self.getModelDir(), self.getLabelmap())

    def getModelPathVinoXML(self):
        return os.path.join(self.getModelDir(), self.getModelXML())

    def getModelPathVinoBin(self):
        return os.path.join(self.getModelDir(), self.getModelBin())

    def getAppCameras(self, limit):
        if 'APP_CAMERAS' in os.environ:
            if os.environ['APP_CAMERAS'] == 'all':
                return self.discoverVideoDeviceSources(limit)
            else:
                deviceSources = []
                sources =  (os.environ['APP_CAMERAS'].replace(" ", "")).split(",")
                for source in sources:
                    vcap = cv2.VideoCapture(int(source))
                    if vcap.read()[0]:
                        deviceSources.append(source)
                        vcap.release()
                    time.sleep(1) 
        else:
            return []

    def getVideoFiles(self):
        videoFilesStr = ''
        if 'APP_VIDEO_FILES' in os.environ:
            if os.environ['APP_VIDEO_FILES'] == '-':
                videoFilesStr = ''
            else:
                videoFilesStr = os.environ['APP_VIDEO_FILES']
        else:
            videoFilesStr = ''

        videoFiles = (videoFilesStr.replace(" ", "")).split(",")
        videoFile = [videoFile for videoFile in videoFiles if len(videoFile) > 0]
        return videoFiles if videoFile else None

    def getRTSPStreams(self):
        rtspStr = ''
        if 'APP_RTSPS' in os.environ:
            if os.environ['APP_RTSPS'] == '-':
                rtspStr = ''
            else:
                rtspStr = os.environ['APP_RTSPS'] 
        else:
            rtspStr = ''

        rtsps = (rtspStr.replace(" ", "")).split(",")
        rtsp = [rtsp for rtsp in rtsps if "rtsp" in rtsp]  
        return rtsps if rtsp else None

    def getRTSPIP(self, rtsp):
        x = rtsp.split(":")
        x = x[1].strip("/")
        return x

    def getViewColumn(self):
        return int(os.environ['APP_VIEW_COLUMNS'] if 'APP_VIEW_COLUMNS' in os.environ else '1')

    def getBlankFrame(self):
        return self.blankFrame

    def discoverVideoDeviceSources(self, limit):
        deviceSources = []
        for source in range(0, limit):
            vcap = cv2.VideoCapture(source)
            if vcap.read()[0]:
                deviceSources.append(source)
                vcap.release()
                time.sleep(1) 

        return deviceSources

    def getDeviceId(self):
        return os.environ['DEVICE_ID'] if 'DEVICE_ID' in os.environ else 'DEVICE_ID'
    
    def getDeviceName(self):
        return os.environ['DEVICE_NAME'] if 'DEVICE_NAME' in os.environ else 'DEVICE_NAME'
    
    # Vino container uses network:host , so use host network IP . TFLite container uses default bridge network, so use network alias
    def getPublishPayloadStreamUrl(self):
        if self.getIsTFLite():
            return os.environ['HTTP_PUBLISH_STREAM_URL'] if 'HTTP_PUBLISH_STREAM_URL' in os.environ else 'Missing HTTP_PUBLISH_STREAM_URL'
        else: #network = host vino
            return "http://" + os.environ['DEVICE_IP_ADDRESS'] + ":5000/publish/stream"
            
    def getPublishPayloadKafkaUrl(self):
        if self.getIsTFLite():
            return os.environ['HTTP_PUBLISH_KAFKA_URL'] if 'HTTP_PUBLISH_KAFKA_URL' in os.environ else 'Missing HTTP_PUBLISH_KAFKA_URL'
        else: #network = host vino
            return "http://" + os.environ['DEVICE_IP_ADDRESS'] + ":5000/publish/kafka"

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

    def getFramerate(self):
        return self.framerate

    def getTool(self):
        return self.tool

    def getInputMean(self):
        return 127.5

    def getInputStd(self):
        return 127.5

    def getModelText(self):
        #return os.path.basename(self.modelObjectId)
        return self.modelObjectId 

    def getModelUpdatedAtText(self):
        return self.modelUpdatedAt.strftime("%Y-%m-%d %H:%M:%S")
    
    def getDetectorURL(self):
        return os.environ['APP_SVC_MODEL_MVI_URL'] if 'APP_SVC_MODEL_MVI_URL' in os.environ else "Internal"

    # uses network:host . Use host network IP
    def getMMSConfigProviderUrl(self):
        return "http://" + os.environ['DEVICE_IP_ADDRESS'] + ":7771/mmsconfig"

    # uses network:host . Use host network IP
    def getMMSModelProviderUrl(self):
        return "http://" + os.environ['DEVICE_IP_ADDRESS'] + ":7772/mmsmodel"

    def mmsConfig(self):
        url = self.getMMSConfigProviderUrl()
        try:
            resp = requests.get(url)
            dict = resp.json()
            if dict['mms_action'] == 'updated':
                value_list = dict['value'] 
                for value_dict in value_list:
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
            print ("{:.7f}V mmsConfig: HttpError".format(time.time()), errh, end="\n", flush=True)
        except requests.exceptions.ConnectionError as errc:
            None
        except requests.exceptions.Timeout as errt:
            print ("{:.7f}V mmsConfig: Timeout".format(time.time()), errt, end="\n", flush=True)
        except requests.exceptions.RequestException as err:
            print ("{:.7f}V mmsConfig: Other Error".format(time.time()), err, end="\n", flush=True)

    #{"mms_action":"updated","value":{"OBJECT_TYPE":"tflite-mmsmodel","OBJECT_ID":"mobilenet-tflite-1.0.0-mms.tar.gz","MODEL_NET":"mobilenet","MODEL_FMWK":"tflite","MODEL_VERSION":"1.0.0","MODEL_DIR":"/var/tmp/horizon/tflite-mmsmodel/mobilenet/tflite/1.0.0/files","FILES":"detect.tflite labelmap.txt"}}
    #{"query_http_code":"204","message":"OK","mms_action":"updated","value":[{"OBJECT_TYPE":"mmsmodel","OBJECT_ID":"pth-frcnn-resnet50-dct-facemask-kaggle-1.0.0-mms.zip","MODEL_NET":"frcnn-resnet50-dct","MODEL_FMWK":"pth","MODEL_VERSION":"1.0.0","MODEL_DIR":"/var/local/horizon/ai/mi/model/pth_cpu"}]}
    def mmsModel(self):
        url = self.getMMSModelProviderUrl()
        try:
            resp = requests.get(url)
            dict = resp.json()
            if dict['mms_action'] == 'updated':
                value_list = dict['value']
                for value_dict in value_list:
                    self.modelUpdatedAt = datetime.datetime.now()
                    if self.getIsPTH():
                        '''
                        # Large model download takes too much time. So currently commented out
                        self.modelObjectType = value_dict['OBJECT_TYPE']
                        self.modelPTH = "mmsmodel-" + value_dict['OBJECT_ID']
                        self.modelObjectId = self.modelPTH
                        self.modelNet = value_dict['MODEL_NET']
                        self.modelFmwk = value_dict['MODEL_FMWK']
                        self.modelVersion = value_dict['MODEL_VERSION']
                        self.modelDir = value_dict['MODEL_DIR']
                        self.setReloadPTHModel(True)
                        '''
                        
                    elif self.getIsTFLite():
                        self.modelObjectType = value_dict['OBJECT_TYPE']
                        self.modelTFLite = "mmsmodel-" + value_dict['OBJECT_ID']
                        self.modelObjectId = value_dict['OBJECT_ID']
                        self.modelNet = value_dict['MODEL_NET']
                        self.modelFmwk = value_dict['MODEL_FMWK']
                        self.modelVersion = value_dict['MODEL_VERSION']
                        self.modelDir = value_dict['MODEL_DIR']

                        with zipfile.ZipFile(os.path.join(self.modelDir, self.modelTFLite), 'r') as zip_ref:
                            zip_ref.extractall(self.modelDir)
                            self.setReloadTFLiteModel(True)
                            
        except requests.exceptions.HTTPError as errh:
            print ("{:.7f}V mmsModel: Http Error".format(time.time()), errh, end="\n", flush=True)
        except requests.exceptions.ConnectionError as errc:
            None
        except requests.exceptions.Timeout as errt:
            print ("{:.7f}V mmsModel: Timeout".format(time.time()), errh, end="\n", flush=True)
        except requests.exceptions.RequestException as err:
            print ("{:.7f}V mmsModel: Other Error".format(time.time()), err, end="\n", flush=True)

    def mmsConfigProcessor(self, interval):
        while True:
            time.sleep(interval)
            self.mmsConfig()

    def mmsModelProcessor(self, interval):
        while True:
            time.sleep(interval)
            if self.getDetectorInitialized():
                self.mmsModel()

    def mmsPoller(self):
        Thread(target=self.mmsConfigProcessor, args=(5,)).start()
        Thread(target=self.mmsModelProcessor, args=(11,)).start()

    def getReloadTFLiteModel(self):
        return self.reloadTFLiteModel

    def setReloadTFLiteModel(self, flag):
        self.reloadTFLiteModel = flag

    def getReloadPTHModel(self):
        return self.reloadPTHModel

    def setReloadPTHModel(self, flag):
        self.reloadPTHModel = flag
    
