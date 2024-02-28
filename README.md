
## Edge deployment of container workload and ML model

**Machine Inferencing and Object Detection** examples using `TensorFlow Lite and PyTorch` frameworks. Implemented with **OpenCV + Python + Docker**

### Introduction

This python based example implementation uses multiple containers and can be deployed on devices with aarch64 CPU-architecture, for example Raspberry Pi 5, using the following frameworks. The end-to-end deployment of containerized services is the focus of these examples NOT the accuracy or performance of the ML model, though occasionally that is mentioned.

- Tensorflow Lite 
- PyTorch (TODO)
<!---

<img width="1439" alt="Screen Shot 2021-06-14 at 11 37 38 AM" src="https://user-images.githubusercontent.com/49573998/121942318-330db900-cd05-11eb-83c2-2b713b097ae9.png">

--->

#### High level existing features:
- Object detection using various frameworks 
- OpenCV based image capture and annotation
- MJPEG based streaming available on http:<edge-device-ip-address:5000> 
- A simple Web UI to interactively upload config using MMS to edge nodes.
- HTTP and kafka message bridge

#### Improvements
- Updated tensorflow-lite Docker container to use Python 3.10 and OpenCV 4.8.1 with tflite runtime v2.12
- Created Docker compose file to simplify development, allow for better control of microservices, and make deployment easier and more secure

### Contents
#### Publish
Development of containers, services, policies and corresponding defintion files.
See `publish` directory.

#### Register
Instructions to register an edge device node to detect objects in a video stream
See `register` directory.

### How to Run
1. Clone the repository
   - Run git clone
2. Create and source your **ENVIRONMENT** variables
   - Outside the repository, create a file called `APP_ENV`
   - Define the required **ENVIRONMENT** variables - refer to step 4 in the `README.md` file  in the `register` folder for the required variables (in this implementation, you only need upto `CR_DOCKER_APIKEY`)
     - I defined two `CR_DOCKER_APIKEY` variables, one with read-write access (`..._RW_`) and one with read-only access (`..._RO`). This is to ensure the services run by Docker compose only have read-only access, while my development files can have read-write access to push images to Dockerhub. I recommend doing the same, or variables in the associated Makefiles and compose.yaml files will need to be changed.
   - Before building or publishing services, be sure to source this file in the terminal that you are using
3. Build the Docker images
   - In `publish/src/http`, run `make build` and then `make push`
   - In `publish/src/infer`, run `make tflite-build` and then `make tflite-push`
4. Define environment variables for Docker compose
   - Based on the environment variables in the `compose.yaml` file in the `register/docker-compose` folder, create a file called `.env` and provide the appropriate definitions. Use the image names created in the previous build step.
   - For the file and RTSP inputs, if there is no input simply type "-"
5. Start the services
   - To run all the services at once, while in the `register/docker-compose` folder, run `docker compose up`
     - To run specific services, run `docker compose up <SERVICE NAME>`
   - To stop the services, run `docker compose down`



#### Research, reference and acknowledgements

  https://opencv.org
  
  https://www.tensorflow.org/lite
  
  https://github.com/EdjeElectronics/TensorFlow-Object-Detection-on-the-Raspberry-Pi
  
  https://stackoverflow.com/questions/tagged/tensorflow
  
  OpenVINO
