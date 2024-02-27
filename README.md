

## IBM Edge Application Manager (IEAM)
### Edge deployment of container workload and ML model

**Machine Inferencing and Object Detection** examples using `TensorFlow Lite, OpenVINO, pyTorch and MVI` frameworks. Implemented with **IEAM + MMS + OpenCV + Python**

#### Introduction

This python based example implementation uses multiple containers and can be deployed on **Intel NUC(amd64), Jetson Nano(arm64) and RaspberryPi 4(arm32)** using following frameworks. The end-to-end deployment of containerized services via IEAM is the focus of these examples NOT the accuracy or performance of the ML model, though occasionally that is mentioned.

- MVI (IBM)
- Tensorflow Lite 
- OpenVINO
- PyTorch 

<img width="1439" alt="Screen Shot 2021-06-14 at 11 37 38 AM" src="https://user-images.githubusercontent.com/49573998/121942318-330db900-cd05-11eb-83c2-2b713b097ae9.png">

#### High level features:
- Object detection using various frameworks 
- OpenCV based image capture and annotation
- MJPEG based streaming available on http:<edge-device-ip-address:5000> 
- A simple Web UI to interactivly upload config using MMS to edge nodes.
- Intel Neural Compute Stick 2 (NCS2)
- Movidius MyriadX VPU
- HTTP and kafka message bridge

#### Publish
Development of containers, services, policies and corresponding defintion files.
See `publish` directory.

#### Register
Instructions to register an edge device node to detect objects in a video stream
See `register` directory.

#### Research, reference and acknowledgements

  https://opencv.org
  
  https://www.tensorflow.org/lite
  
  https://github.com/EdjeElectronics/TensorFlow-Object-Detection-on-the-Raspberry-Pi
  
  https://stackoverflow.com/questions/tagged/tensorflow
  
  OpenVINO
    
