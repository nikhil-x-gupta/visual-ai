
## Containerized Deployment of Machine Learning Image Processing Pipeline

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
- Supports device camera, file, and RTSP stream inputs
- MJPEG based HTTP streaming
- HTTP and kafka message bridge (TODO)
- Pose detection models (TODO)

#### Software
- Python 3.10
- OpenCV 4.8.1
- Tensorflow-lite runtime v2.12
- Docker compose v2.24
- PyTorch (TODO)

### Contents
#### Build
Development of containers, services, policies and corresponding definition files. See `build` directory.

#### Run
Docker compose and corresponding environment files for running services. See `run` directory.

#### Original
Reference code, not for use

### How to Run
1. Clone the repository
   - Run git clone
2. Define and source your **ENVIRONMENT** variables
   - Outside the repository, create a file called `APP_ENV`
   - Define the following required **ENVIRONMENT** variables
     - You will need to create two API keys in DockerHub for the two `CR_DOCKER_APIKEY` variables, one with read-write access (`..._RW_`) and one with read-only access (`..._RO`). This is to ensure the services run by Docker compose only have read-only access, while my development files can have read-write access to push images to Dockerhub.
       ```
       #### Enviornment variables EDGE_OWNER, EDGE_DEPLOY to identify service.
       export EDGE_OWNER=<change-as-needed> e.g sg.edge           
       export EDGE_DEPLOY=<change-as-needed> e.g example.visual 

       #### Specify your docker login name
       export DOCKER_BASE=<change-as-needed> e.g edgedock

       ### Authenticated docker access ###
       export CR_DOCKER_HOST=index.docker.io
       export CR_DOCKER_USERNAME=<change-as-needed> e.g edgedock
       export CR_DOCKER_APIKEY_RW=<change-as-needed> your read-write DockerHub apikey
       export CR_DOCKER_APIKEY_RO=<change-as-needed> your read-only DockerHub apikey
       ```
   - Before building or publishing services, be sure to source this file in the terminal that you are using
3. Build the Docker images
   - HTTP service
     - Change to `build/src/http` directory
     - Run `make build`
     - Run `make push`
   - TFLite infer service
     - In `build/src/infer`, run `make tflite-build` and then `make tflite-push`
5. Define environment variables for Docker compose
   - Based on the environment variables in the `compose.yaml` file in the `run` folder, create a file called `.env` and provide the appropriate definitions. Use the image names created in the previous build step.
   - For the file and RTSP inputs, if there is no input simply type "-"
6. Start the services
   - To run all the services at once, while in the `run` folder, run `docker compose up`
     - To run specific services, run `docker compose up <SERVICE NAME>`
   - To stop the services, run `docker compose down`



#### Research, reference and acknowledgements

  https://opencv.org
  
  https://www.tensorflow.org/lite
  
  https://github.com/EdjeElectronics/TensorFlow-Object-Detection-on-the-Raspberry-Pi
  
  https://stackoverflow.com/questions/tagged/tensorflow

  https://docs.docker.com/compose/intro/features-uses/
  
  OpenVINO
