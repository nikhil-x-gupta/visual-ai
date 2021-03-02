#
# mviDetector.py
#
# Sanjeev Gupta, Feb 24, 2021
#
# Uses an all contained container max_mvi detector deployed as a required service
# Simple requests based post did not work and ha to augment with Retry block 

import numpy
import requests
import subprocess
import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

class MVIDetector:
    def __init__(self, config):
        self.config = config

        #self.detectorURL = "http://sg.edge.example.visual.max_mvi:5001/inference"
        self.detectorURL = config.getMaxMVIDetectorURL()

        self.modelPath = "."
        self.labels=["Mask", "NoMask"]

        self.inference_interval = 0
        self.outputResults = {}

    def getModelPath(self):
        return self.modelPath

    def getLabels(self):
        return self.labels

    def inferJpgFile(self, frame_image_jpg_file):
        print ("Infer....", end="\n", flush=True)
        t1 = time.time()
        try:
            print ("imageFile detector", end="\n", flush=True)

            print ("imageFile opening ", frame_image_jpg_file, end="\n", flush=True)
            #frame_jpg = open('package/detect/ef3f7ca8-a85c-48ae-84f2-4c65d9aac02a.jpg', 'rb')
            frame_jpg = open(frame_image_jpg_file, 'rb')
            print ("imageFile opened ", end="\n", flush=True)

            files = {'imagefile': frame_jpg}

            session = requests.Session()

            retries = Retry(total=10,
                            backoff_factor=0.1,
                            status_forcelist=[ 500, 502, 503, 504 ])
            session.mount('http://', HTTPAdapter(max_retries=retries))

            print ("imageFile detectorURL posting ", self.detectorURL, end="\n", flush=True)

            response = session.post(self.detectorURL, files=files)

            self.outputDetails = response.json()
            print ("imageFile detectorURL", self.outputDetails, end="\n", flush=True)

            self.inference_interval = time.time() - t1
            print ("imageFile inference_interval", self.inference_interval, end="\n", flush=True)
            print ("imageFile detector return", end="\n", flush=True)
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

    #{"classified": [{"label": "Mask", "confidence": 0.99959, "xmin": 153, "ymin": 73, "xmax": 233, "ymax": 144, "attr": [{}]}, {"label": "Mask", "confidence": 0.98961, "xmin": 38, "ymin": 65, "xmax": 102, "ymax": 114, "attr": [{}]}], "result": "success"}
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
