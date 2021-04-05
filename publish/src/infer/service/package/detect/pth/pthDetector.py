#
# pthDetector.py
#
# Sanjeev Gupta, Mar 21, 2021
#

import time

import torch
import torchvision
from torchvision import transforms

from package.util import util

class PTHDetector:
    def __init__(self, config, classes=None):
        self.config = config

        self.classes = ['__background__'] + classes
        self.device = self.getTorchDevice()

        self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
        in_features = self.model.roi_heads.box_predictor.cls_score.in_features
        self.model.roi_heads.box_predictor = torchvision.models.detection.faster_rcnn.FastRCNNPredictor(in_features, len(classes) + 1)
        self.model.to(self.device)
        self.model.load_state_dict(torch.load(self.config.getModelPathPTH(), map_location=self.device))
        self.model.eval()

    def getInferResults(self, frame_normalized):
        t1 = time.time()
        predictions = self.predict(frame_normalized)
        classes, boxes, scores = predictions
        self.inference_interval = time.time() - t1
        return self.inference_interval, boxes, classes, scores

   def predict(self, images):
        # Create a list of images if a single image
        is_single_image = not util.isIterable(images)
        images = [images] if is_single_image else images

        results = []
        with torch.no_grad():
            tensors = self.transformTensor()
            images = [tensors(image) for image in images]
            # Position on CPU/GPU
            images = [image.to(self.device) for image in images]
            preds = self.model(images)
            # Tensor to CPU as  needed
            preds = [{key: value.to(torch.device('cpu')) for key, value in pred.items()} for pred in preds]
            for pred in preds:
                # Predicted index to string classes
                result = ([self.classes[value] for value in pred['labels']], pred['boxes'], pred['scores'])
                results.append(result)

        return results[0] if is_single_image else results

    def getHeight(self):
        return 480

    def getWidth(self):
        return 640

    def getFloatingModel(self):
        return False

    def getTorchDevice(self):
        return torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    def transformNormalize(self):
        return transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

    def transformTensor(self):
        return transforms.Compose([transforms.ToTensor(), self.transformNormalize()])

