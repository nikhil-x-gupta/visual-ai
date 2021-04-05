#
# vinoDetector.py
#
# Sanjeev Gupta, April 2020

import importlib.util
import logging
import numpy
import time
import cv2

class VinoDetector:
    def __init__(self, config):
        spec = importlib.util.find_spec('openvino')
        if spec:
            from openvino.inference_engine import IECore

            self.inference_interval = 0

            self.ie = IECore()

            self.modelXML = config.getModelPathVinoXML()
            self.modelBin = config.getModelPathVinoBin()
            print ("{:.7f} VinoDetector model {}d".format(time.time(), self.modelXML))

            self.net = self.ie.read_network(model=self.modelXML, weights=self.modelBin)

            print ("{:.7f} VinoDetector initialized".format(time.time()))

            for input_key in self.net.input_info:
                if len(self.net.input_info[input_key].input_data.layout) == 4:
                    n, c, h, w = self.net.input_info[input_key].input_data.shape
                    print ("{:.7f} VinoDetector n={} c={} h={} w={}".format(time.time(), str(n), str(c), str(h), str(w)))
                    self.n = n
                    self.c = c
                    self.width = w
                    self.height = h

            print ("{:.7f} VinoDetector loading inferencing model".format(time.time()))
            self.exec_net = self.ie.load_network(network=self.net, device_name="MYRIAD")
            print ("{:.7f} VinoDetector model loaded".format(time.time()))

    def prepareBlob(self):
        n = self.getN()
        c = self.getC()
        h = self.getHeight()
        w = self.getWidth()

        #print("Preparing input blobs")
        assert (len(self.net.input_info.keys()) == 1 or len(self.net.input_info.keys()) == 2), "Sample supports topologies only with 1 or 2 inputs"

        self.out_blob = next(iter(self.net.outputs))
        input_name, input_info_name = "", ""

        for input_key in self.net.input_info:
            if len(self.net.input_info[input_key].layout) == 4:
                input_name = input_key

                #print ("input_name="+input_name)
                #print("Batch size is {}".format(self.net.batch_size))

                self.net.input_info[input_key].precision = 'U8'
            elif len(self.net.input_info[input_key].layout) == 2:
                input_info_name = input_key
                self.net.input_info[input_key].precision = 'FP32'

                if self.net.input_info[input_key].input_data.shape[1] != 3 and self.net.input_info[input_key].input_data.shape[1] != 6 or self.net.input_info[input_key].input_data.shape[0] != 1:
                    print ('ERROR: Invalid input info. Should be 3 or 6 values length.')

        blob = {}

        if input_info_name != "":
            infos = numpy.ndarray(shape=(n, c), dtype=float)
            for i in range(n):
                infos[i, 0] = h
                infos[i, 1] = w
                infos[i, 2] = 1.0

            blob[input_info_name] = infos

        #print('Preparing output blobs')

        output_name, output_info = "", self.net.outputs[next(iter(self.net.outputs.keys()))]
        for output_key in self.net.outputs:
            if self.net.layers[output_key].type == "DetectionOutput":
                output_name, output_info = output_key, self.net.outputs[output_key]

        if output_name == "":
            print ("ERROR:Can't find a DetectionOutput layer in the topology")

        output_dims = output_info.shape
        if len(output_dims) != 4:
            print ("ERROR:Incorrect output dimensions for SSD model")
        max_proposal_count, object_size = output_dims[2], output_dims[3]

        if object_size != 7:
            print ("ERROR:Output item should have 7 as a last dimension")

        output_info.precision = "FP32"

        return input_name, blob

    def getN(self):
        return self.n

    def getC(self):
        return self.c

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height
            
    def infer(self, blob):
        t1 = time.time()

        #print ("Loading model to the device")
        #exec_net = self.ie.load_network(network=self.net, device_name="MYRIAD")

        self.res = self.exec_net.infer(inputs=blob)
        self.inference_interval = time.time() - t1

        return self.inference_interval

    def getResults(self, images_hw, frame_current):
        #print("INFO: Processing output blobs")
        res = self.res[self.out_blob]
        boxes, classes, scores = {}, {}, {}
        data = res[0][0]
        for number, proposal in enumerate(data):
            if proposal[2] > 0:
                imid = numpy.int(proposal[0])
                ih, iw = images_hw[imid]
                label = numpy.int(proposal[1])
                confidence = proposal[2]
                xmin = numpy.int(iw * proposal[3])
                ymin = numpy.int(ih * proposal[4])
                xmax = numpy.int(iw * proposal[5])
                ymax = numpy.int(ih * proposal[6])
                if proposal[2] > 0.5:
                    if not imid in boxes.keys():
                        boxes[imid] = []
                    boxes[imid].append([xmin, ymin, xmax, ymax])

                    if not imid in classes.keys():
                        classes[imid] = []
                    classes[imid].append(label)

                    if not imid in scores.keys():
                        scores[imid] = []
                    scores[imid].append(confidence)

        return boxes, classes, scores

    def getModel(self):
        modelXML = '/tmp/face-detection-adas-0001.xml'
        modelBin = '/tmp/face-detection-adas-0001.bin'
        return {'XML': modelXML, 'BIN': modelBin }

    def getLabels(self):
        return self.labels

    def getInferenceInterval(self):
        return self.inference_interval

    def getInputDetailsIndex(self):
        return self.getInputDetails()[0]['index']

    def getInputDetails(self):
        return self.interpreter.get_input_details()

    def getOutputDetails(self):
        return self.interpreter.get_output_details()

    def getFloatingModel(self):
        return True
        #return (self.getInputDetails()[0]['dtype'] == numpy.float32)

    def getInferResults(self, images, images_hw, frame_current):
        input_name, blob = self.prepareBlob()
        blob[input_name] = images
        inference_interval = self.infer(blob)
        boxes, classes, scores =  self.getResults(images_hw, frame_current)

        return inference_interval, boxes, classes, scores 
        
