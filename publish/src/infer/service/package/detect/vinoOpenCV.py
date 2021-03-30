#
# vinoOpenCV.py
#
# Sanjeev Gupta, April 2020

import cv2
import datetime
import numpy 

from .baseOpenCV import BaseOpenCV

class VinoOpenCV(BaseOpenCV):
    def __init__(self):
        super().__init__()

    # new method signature override name
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

    def annotateFrame(self, config, detector, frame_current, src_name, frame_faces, frame_gray, boxes_dict, classes_dict, scores_dict):
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

        super().addStatus(config, frame_current, src_name)

        return entities_dict 
