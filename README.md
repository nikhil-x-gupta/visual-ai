## IBM Edge Application Manager (IEAM)
### Edge deployment of container workload and ML model

`TensorFlow Lite` and `OpenVINO` based **Machine Inferencing and Object Detection** example implemented using **IEAM + MMS + OpenCV + Python**

### Introduction

This python based example implementation uses three containers and can be deployed on **Intel NUC(amd64), Jeston Nano(arm64) and RaspberryPi 4(arm32)** using Tensorflow Lite and/or OpenVINO

- Image capture and classification
- HTTP and kafka message bridge
- MJPEG based streaming available on http:<edge-device-ip-address:5000> 
- A simple Web UI to interactivly upload config using MMS to edge nodes.
- Frameworks - TensorFlow Lite and OpenVINO
- Intel Neural Compute Stick 2 (NCS2)
- Movidius MyriadX VPU
- coco_ssd_mobilenet_v1_1.0 model 
- OpenVINO with NCS2 and Movidius VPU

### Publish
Development of containers, services, policies and corresponding defintion files.
See `publish` directory.

### Register
Instructions to register an edge device node to detect objects in a video stream
See `register` directory.

### Research, reference and acknowledgements

  https://opencv.org
  
  https://www.tensorflow.org/lite
  
  https://github.com/EdjeElectronics/TensorFlow-Object-Detection-on-the-Raspberry-Pi
  
  https://stackoverflow.com/questions/tagged/tensorflow
  
  OpenVINO
    
