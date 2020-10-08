#
# tfliteOpenCV.py
#
# Sanjeev Gupta, April 2020

import base64
import cv2
import datetime
import json
import math
import numpy 
import time

class TFLiteOpenCV:
    def __init__(self):
        self.frame_rate  = 1 # seed value. Will get updated
        self.tickFrequency = cv2.getTickFrequency()
        self.t1 = cv2.getTickCount()
        # haarcascade based face classifier not reliable enough
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

    def getFrame(self, config, videostream, isFloatingModel, height, width):
        self.t1 = cv2.getTickCount()
        frame_read = videostream.read()
        frame_current = frame_read.copy()
        frame_rgb = cv2.cvtColor(frame_current, cv2.COLOR_BGR2RGB)
        frame_resize = cv2.resize(frame_rgb, (width, height))

        frame_faces = None
        frame_gray = None
        #if config.shouldDetectFace() or config.shouldBlurFace():
        #    frame_faces, frame_gray = self.faceDetector(frame_current)
            
        # Condition and Normalize pixel values
        frame_norm = numpy.expand_dims(frame_resize, axis=0)
        if isFloatingModel:
            frame_norm = (numpy.float32(frame_norm) - config.getInputMean()) / config.getInputStd()

        return frame_current, frame_norm, frame_faces, frame_gray

    def annotateFrame(self, config, detector, frame_current, src_name, frame_faces, frame_gray, boxes, classes, scores):
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

        status_text = "Publish Kafka: "
        if config.shouldPublishKafka():
            status_text += "YES"
        else:
           status_text += "NO"

        '''
        status_text = "       Detect Face: "
        if config.shouldDetectFace():
            status_text += "YES"
        else:
            status_text += "NO "

        status_text += "      Blur Face: "
        if config.shouldBlurFace():
            status_text += "YES"
        else:
            status_text += "NO "
        '''    
            
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
