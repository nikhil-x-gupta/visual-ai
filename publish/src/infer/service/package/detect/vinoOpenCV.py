#
# vinoOpenCV.py
#
# Sanjeev Gupta, April 2020

import base64
import cv2
import datetime
import json
import math
import numpy 
import time
import logging

class VinoOpenCV:
    def __init__(self):
        self.frame_rate  = 1 # seed value. Will get updated
        self.tickFrequency = cv2.getTickFrequency()
        self.t1 = cv2.getTickCount()
        # haarcascade based face classifier not reliable enough
        self.face_cascade = cv2.CascadeClassifier('/usr/local/lib/python3.6/dist-packages/cv2/data/haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier('/usr/local/lib/python3.6/dist-packages/cv2/data/haarcascade_eye.xml')
        
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

    def getFrame(self, config, videostream, n, c, h, w):
        self.t1 = cv2.getTickCount()

        frame_faces = None
        frame_gray = None
        frame_norm = None
        
        images = numpy.ndarray(shape=(n, c, h, w))
        images_hw = []
        for i in range(n):
            frame_read = videostream.read()
            frame_current = frame_read.copy()
            image = frame_read.copy()
            ih, iw = image.shape[:-1]
            images_hw.append((ih, iw))
            if (ih, iw) != (h, w):
                image = cv2.resize(image, (w, h))
            image = image.transpose((2, 0, 1))  # Change data layout from HWC to CHW
            images[i] = image

        return frame_current, frame_norm, frame_faces, frame_gray, images, images_hw

    def annotateFrame(self, config, frame_current, src_name, frame_faces, frame_gray, boxes_dict, classes_dict, scores_dict):
        entities_dict = {}
        for imid in classes_dict:
            for box in boxes_dict[imid]:
                xmin = box[0]
                ymin = box[1]
                xmax = box[2]
                ymax = box[3]
                cv2.rectangle(frame_current, (xmin, ymin), (xmax, ymax), (232, 35, 244), 2)

                # Draw label
                object_name = config.getObjectName()
                label = '%s: %d%%' % (object_name,  int(scores_dict[imid][0] * 100))
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                label_ymin = max(ymin, labelSize[1] + 8)
                cv2.rectangle(frame_current, (xmin, label_ymin - labelSize[1] - 10), (xmin + labelSize[0], label_ymin + baseLine - 10), (255, 255, 255), cv2.FILLED)
                cv2.putText(frame_current, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
            
                details = []
                if object_name in entities_dict:
                    details = entities_dict[object_name]
                else:
                    entities_dict[object_name] = details

                w = int(xmax-xmin)
                h = int(ymax-ymin)
                detail_dict = {}
                detail_dict['h'] = h 
                detail_dict['w'] = w
                detail_dict['cx'] = int(box[0] + w/2)
                detail_dict['cy'] = int(box[1] + h/2)
                detail_dict['confidence'] = float('{0:.2f}'.format(scores_dict[imid][0]))
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

        status_text = "Overlay: "
        if config.shouldShowOverlay():
            status_text += "YES"
        else:
           status_text += "NO "

        status_text += "       Publish Kafka: "
        if config.shouldPublishKafka():
            status_text += "YES"
        else:
           status_text += "NO "
           
        status_text += "       Publish Stream: "
        if config.shouldPublishStream():
            status_text += "YES"
        else:
           status_text += "NO "

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
