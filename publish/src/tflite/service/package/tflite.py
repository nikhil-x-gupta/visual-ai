#
# tflite.py
#
# Config      : Configuration and handling of enviroment variables
# Detector    : Machine inferencing and annotation data
# OpenCV      : Image porcessing
# VideoStream : Image capture
#
# Sanjeev Gupta, April 2020
#

from threading import Thread
import base64
import cv2
import datetime
import importlib.util
import json
import numpy 
import math 
import os
import time
import requests

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
        self.env_dict['SHOW_OVERLAY'] = os.environ['SHOW_OVERLAY'] 
        self.env_dict['DETECT_FACE'] = os.environ['DETECT_FACE'] 
        self.env_dict['BLUR_FACE'] = os.environ['BLUR_FACE'] 
        self.env_dict['PUBLISH_KAFKA'] = os.environ['PUBLISH_KAFKA'] 
        self.env_dict['PUBLISH_STREAM'] = os.environ['PUBLISH_STREAM'] 

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
        rtspStr = os.environ['RTSP_STREAMS'] 
        rtspStr = rtspStr.replace(" ", "")
        return rtspStr.split(",")

    def getRTSPIP(self, rtsp):
        x = rtsp.split(":")
        x = x[1].strip("/")
        return x

    def getViewColumn(self):
        return int(os.environ['VIEW_COLUMN'])

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
        return os.environ['DEVICE_ID']
    
    def getDeviceName(self):
        return os.environ['DEVICE_NAME']
    
    def getMMSConfigProviderUrl(self):
        url = "http://" + os.environ['DEVICE_IP_ADDRESS'] + ":7778/mmsconfig"
        return url

    def getMMSModelProviderUrl(self):
        url = "http://" + os.environ['DEVICE_IP_ADDRESS'] + ":7778/mmsmodel"
        return url

    def getPublishPayloadKafkaUrl(self):
        return os.environ['HTTP_PUBLISH_KAFKA_URL']

    def getPublishPayloadStreamUrl(self):
        return os.environ['HTTP_PUBLISH_STREAM_URL']

    def getMinConfidenceThreshold(self):
        return float(os.environ['MIN_CONFIDENCE_THRESHOLD'])

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
            
class Detector:
    def __init__(self, config):
        spec = importlib.util.find_spec('tflite_runtime')
        if spec:
            from tflite_runtime.interpreter import Interpreter
        else:
            from tensorflow.lite.python.interpreter import Interpreter

        #Fix label content
        with open(config.getLabelmapPath(), 'r') as f:
            self.labels = [line.strip() for line in f.readlines()]
        if self.labels[0] == '???':
            del(self.labels[0])

        self.inference_interval = 0
        self.interpreter = Interpreter(model_path=config.getModelPath())
        self.interpreter.allocate_tensors()
        self.modelPath = config.getModelPath()

    def getModelPath(self):
        return self.modelPath

    def getLabels(self):
        return self.labels

    def infer(self, frame_normalized):
        t1 = time.time()
        self.interpreter.set_tensor(self.getInputDetailsIndex(), frame_normalized)
        self.interpreter.invoke()
        self.inference_interval = time.time() - t1
        return self.inference_interval

    def getInferenceInterval(self):
        return self.inference_interval

    def getInputDetailsIndex(self):
        return self.getInputDetails()[0]['index']

    def getInputDetails(self):
        return self.interpreter.get_input_details()

    def getOutputDetails(self):
        return self.interpreter.get_output_details()

    def getHeight(self):
        return self.getInputDetails()[0]['shape'][1]

    def getWidth(self):
        return self.getInputDetails()[0]['shape'][2]

    def getFloatingModel(self):
        return (self.getInputDetails()[0]['dtype'] == numpy.float32)

    def getResults(self):
        output_details = self.getOutputDetails()
        boxes = self.interpreter.get_tensor(output_details[0]['index'])[0]
        classes = self.interpreter.get_tensor(output_details[1]['index'])[0]
        scores = self.interpreter.get_tensor(output_details[2]['index'])[0]
        num = self.interpreter.get_tensor(output_details[3]['index'])[0]

        return boxes, classes, scores, num

class OpenCV:
    def __init__(self):
        self.frame_rate  = 1 # seed value. Will get updated
        self.tickFrequency = cv2.getTickFrequency()
        self.t1 = cv2.getTickCount()
        self.face_cascade = cv2.CascadeClassifier('/usr/local/lib/python3.7/site-packages/cv2/data/haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier('/usr/local/lib/python3.7/site-packages/cv2/data/haarcascade_eye.xml')
        
    def getFrameRate(self):
        return self.frame_rate

    def updateFrameRate(self):
        t2 = cv2.getTickCount()
        time1 = (t2 - self.t1)/self.tickFrequency
        self.frame_rate = 1/time1
    
    def faceDetector(self, frame_current):
        frame_gray = cv2.cvtColor(frame_current, cv2.COLOR_BGR2GRAY)
        frame_faces = self.face_cascade.detectMultiScale(frame_gray, 1.3, 5)
        
        return frame_faces, frame_gray

    def getFrame(self, config, detector, videostream):
        self.t1 = cv2.getTickCount()
        frame_read = videostream.read()
        frame_current = frame_read.copy()
        frame_rgb = cv2.cvtColor(frame_current, cv2.COLOR_BGR2RGB)
        frame_resize = cv2.resize(frame_rgb, (detector.getWidth(), detector.getHeight()))

        frame_faces = None
        frame_gray = None
        if config.shouldDetectFace() or config.shouldBlurFace():
            frame_faces, frame_gray = self.faceDetector(frame_current)
            
        # Condition and Normalize pixel values
        frame_norm = numpy.expand_dims(frame_resize, axis=0)
        if detector.getFloatingModel():
            frame_norm = (numpy.float32(frame_norm) - config.getInputMean()) / config.getInputStd()

        return frame_current, frame_norm, frame_faces, frame_gray

    def annotateFrame(self, config, detector, opencv, frame_current, src_name, frame_faces, frame_gray, boxes, classes, scores, num):
        entities_dict = {}
        for i in range(len(scores)):
            if ((scores[i] > config.getMinConfidenceThreshold()) and (scores[i] <= 1.0)):
                
                imageH, imageW, _ = frame_current.shape

                # Get bounding box coordinates and draw box
                ymin = int(max(1, (boxes[i][0] * imageH)))
                xmin = int(max(1, (boxes[i][1] * imageW )))
                ymax = int(min(imageH, (boxes[i][2] * imageH)))
                xmax = int(min(imageW, (boxes[i][3] * imageW)))
                cv2.rectangle(frame_current, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)

                # Draw label
                object_name = detector.getLabels()[int(classes[i])]
                label = '%s: %d%%' % (object_name,  int(scores[i] * 100))
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                label_ymin = max(ymin, labelSize[1] + 8)
                cv2.rectangle(frame_current, (xmin, label_ymin - labelSize[1] - 10), (xmin + labelSize[0], label_ymin + baseLine - 10), (255, 255, 255), cv2.FILLED)
                cv2.putText(frame_current, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
            
                details = []
                if object_name in entities_dict:
                    details = entities_dict[object_name]
                else:
                    entities_dict[object_name] = details

                h = int(ymax-ymin)
                w = int(xmax-xmin)
                detail_dict = {}
                detail_dict['h'] = h 
                detail_dict['w'] = w
                detail_dict['cx'] = int(xmin + w/2)
                detail_dict['cy'] = int(ymin + h/2)
                detail_dict['confidence'] = float('{0:.2f}'.format(scores[i]))
                details.append(detail_dict)

                if frame_faces is not None:
                    for (x, y, w, h) in frame_faces:
                        if config.shouldBlurFace():
                            cv2.ellipse(frame_current, (int(x + w/2), int(y + h/2)), (int(0.6 * w), int(0.8 * h)), 0, 0, 360, (128, 128, 128), -1)
                        elif config.shouldDetectFace():
                            cv2.rectangle(frame_current, (x, y), (x+w, y+h), (192, 192, 192), 2)
                            roi_gray = frame_gray[y:y+h, x:x+w]
                            roi_color = frame_current[y:y+h, x:x+w]
                            eyes = self.eye_cascade.detectMultiScale(roi_gray)
                            for (ex, ey, ew, eh) in eyes:
                                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (64, 128, 192), 2)

        alpha = 0.7
        title = frame_current.copy()
        h, w = frame_current.shape[:2]
        cv2.rectangle(title, (0, 0), (w, 25), (64, 64, 64), -1)
        cv2.addWeighted(title, alpha, frame_current, 1 - alpha, 0, frame_current)
        cv2.putText(frame_current, src_name, (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame_current, 'GMT {0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()), (w - 230, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame_current, config.getStatusText(), (10, h-20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2, cv2.LINE_AA)

        return entities_dict 
        
    def addOverlay(self, frame_current, tool, device_name, inference_interval, frame_rate): 
        alpha = 0.6
        overlay = frame_current.copy()
        cv2.rectangle(overlay, (2, 30), (215, 125), (64, 64, 64), -1)
        cv2.addWeighted(overlay, alpha, frame_current, 1 - alpha, 0, frame_current)
        cv2.putText(frame_current, '{tool}'.format(tool=tool), (5, 50), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame_current, '{device_name}'.format(device_name=device_name), (5, 80), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame_current, 'Detection Time {0:.2f} sec'.format(inference_interval), (5, 100), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame_current, 'Overall FPS {0:.2f}'.format(frame_rate), (5, 120), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0), 1, cv2.LINE_AA)
    
    def getInferenceDataJSON(self, config, inference_interval, entities_dict, video_sources):
        entities = []
        for key in entities_dict:
            entity_dict = {}
            entity_dict["eclass"] = key
            entity_dict["details"] = entities_dict[key]
            entities.append(entity_dict)

        ncols = config.getViewColumn()
        nsrc = len(video_sources)
        nrows = math.trunc((nsrc-1) / ncols) + 1
        rowFrames = []
        for r in range (0, nrows):
            colFrames = []
            for c in range(0, ncols):
                v = r * ncols + c
                if v < nsrc:
                    videoSource = video_sources[v]
                    if videoSource.frame_annotated is not None:
                        colFrames.append(videoSource.frame_annotated)
                    else:
                        colFrames.append(config.getBlankFrame())
                else:
                    colFrames.append(config.getBlankFrame())

            hframe = cv2.hconcat(colFrames)
            rowFrames.append(hframe)

        fullFrame = cv2.vconcat(rowFrames)

        bgColor = [15, 15, 15]
        fullFrame = cv2.copyMakeBorder(fullFrame, 0, 60, 0, 0, cv2.BORDER_CONSTANT, value=bgColor)

        status_text = "Detect Face: "
        if config.shouldDetectFace():
            status_text += "YES"
        else:
            status_text += "NO "

        status_text += "      Blur Face: "
        if config.shouldBlurFace():
            status_text += "YES"
        else:
            status_text += "NO "
            
        status_text += "       Publish Kafka: "
        if config.shouldPublishKafka():
            status_text += "YES"
        else:
           status_text += "NO"
            
        if ncols == 1:
            font_scale = 1
            status_x = 60
        else:
            font_scale = 2
            ht, wd, ch = config.getBlankFrame().shape
            status_x = int((ncols * wd - 1040)/2)

        alpha = 0.7
        status = fullFrame.copy()
        h, w = fullFrame.shape[:2]
        cv2.rectangle(status, (2, h-28), (w-2, h-2), (64, 64, 64), -1)
        cv2.addWeighted(status, alpha, fullFrame, 1 - alpha, 0, fullFrame)
        cv2.putText(fullFrame, status_text, (status_x, h-5), cv2.FONT_HERSHEY_PLAIN, font_scale, (255, 255, 192), 1, cv2.LINE_AA)

        retval, buffer = cv2.imencode('.jpg', fullFrame)

        infered_b64_frame = (base64.b64encode(buffer)).decode('utf8')
            
        # Create inference payload
        inference_dict = {}
        inference_dict['deviceid'] = config.getDeviceId()
        inference_dict['devicename'] = config.getDeviceName()
        inference_dict['tool'] = config.getTool()
        inference_dict['date'] = int(time.time())
        inference_dict['camtime'] = 0
        inference_dict['time'] = round(inference_interval, 3)
        inference_dict['count'] = len(entities)
        inference_dict['entities'] = entities
        inference_dict['image'] = infered_b64_frame

        inference_data = {}
        inference_data['detect'] = inference_dict
        inference_data_json = json.dumps(inference_data);

        return inference_data_json

class VideoStream:
    def __init__(self, config, source):
        self.videoCapture = cv2.VideoCapture(source)
        ret = self.videoCapture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.videoCapture.set(3, config.getResolutionWidth())
        ret = self.videoCapture.set(4, config.getResolutionHeight())

        (self.grabbed, self.frame) = self.videoCapture.read()

        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def stop(self):
        self.stopped = True

    def read(self):
        return self.frame

    def update(self):
        while True:
            if self.stopped:
                self.videoCapture.release()
                return
            else:
                (self.grabbed, self.frame) = self.videoCapture.read()
                time.sleep(0.02)
