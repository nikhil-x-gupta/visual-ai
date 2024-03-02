#
# mviDetector.py
#
# Sanjeev Gupta, Feb 24, 2021
#
# Uses an all contained container max_mvi detector deployed as a required service

import numpy
import requests
import subprocess
import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

class MVIDetector:
    def __init__(self, config):
        self.config = config

        self.detectorURL = config.getDetectorURL()

        print ("{:.7f} MVIDetector self.detectorURL".format(time.time()), self.detectorURL, end="\n", flush=True)

        self.modelPath = "."
        self.labels=["Mask", "NoMask"]

        self.inference_interval = 0
        self.outputResults = {}

    def getModelPath(self):
        return self.modelPath

    def getLabels(self):
        return self.labels

    def inferJpgFile(self, frame_image_jpg_file):
        t1 = time.time()
        try:
            frame_jpg = open(frame_image_jpg_file, 'rb')
            files = {'imagefile': frame_jpg}

            session = requests.Session()
            retries = Retry(total=10,
                            backoff_factor=0.1,
                            status_forcelist=[ 500, 502, 503, 504 ])
            session.mount('http://', HTTPAdapter(max_retries=retries))
            response = session.post(self.detectorURL, files=files)

            self.outputDetails = response.json()

            self.inference_interval = time.time() - t1
            return self.inference_interval
        except requests.exceptions.RequestException as err:
            print ("Oops: Something Else",err, end="\n", flush=True)
        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh, end="\n", flush=True)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc, end="\n", flush=True)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt, end="\n", flush=True)

        return ""
    
    def getInferenceInterval(self):
        return self.inference_interval

    def getOutputDetails(self):
        return self.outputDetails

    def getHeight(self):
        #return self.getInputDetails()[0]['shape'][1]
        return 480

    def getWidth(self):
        #return self.getInputDetails()[0]['shape'][2]
        return 640

    def getFloatingModel(self):
        return False

    def getResults(self):
        outputDetails = self.getOutputDetails()
        boxes = []
        classes = []
        scores = []
        num = 0
        if outputDetails['result'] == 'success':
            for record in outputDetails['classified']:
                num += 1
                dim = [record['ymin'], record['xmin'], record['ymax'], record['xmax']]
                boxes.append(dim)
                classes.append(record['label'])
                scores.append(record['confidence'])

        return boxes, classes, scores, num

    def getInferResults(self, frame_current, index, opencv):
        frame_image_jpg_file = "/tmp/frame-image-mvi-" + str(index) + ".jpg"
        opencv.writeImageFileJpg(frame_image_jpg_file, frame_current)
        inference_interval = self.inferJpgFile(frame_image_jpg_file)
        boxes, classes, scores, num = self.getResults()
        return inference_interval, boxes, classes, scores 
    
