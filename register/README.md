## Instructions to `Register` an edge device node to detect objects in a video stream
    
  These instructions will guide you through the steps to register an edge node to detect objects in a video stream using one of the frameworks.
  - MVI
  - TensorFlow Lite
  - PyTorch
  - OpenVINO

### Pre-requisite
  - API-KEY from the IEAM mgmt hub admin to register the edge node.
  - An Intel NUC or Desktop (x86, amd64) or Raspberry PI4 (arm32) You may use a video file or RTSP stream or USB camera. Using video file can be sometimes tricky based on file formats etc, I have found using an USB camera working the best. 
   
  For OpenVINO
 
  - Either have a Neural Compute Stick 2 (NCS2) plugged in one of the USB ports or Movidius VPU card in the desktop.

### 1. Verify the output of the following command. 
It should return one IP address that you use to ssh into the edge device. e.g. `192.168.x.x your-hostname`

        hostname -i
        
   The output of above command should not be the local loopback address (e.g. 127.0.x.x) or have multiple addresses. If that is the case then edit **/etc/hosts** and make an entry for your hostname as below.

        <ip-address> <your-hostname> 
        
   Verify the result of the above command again.
  
### 2. Prepare node policy and user input files

   - Copy `./node_register_app.sh` on your node.
   - Copy one of the following set of files from this repo on the edge node depending upon the framework that you want to use:
   
   - MVI Local
  
        - node_policy_mvi.json
        - user_input_app_mvi.json
   
   - TensorFlow Lite
        
        - node_policy_tflite.json 
        - user_input_app_tflite.json
  
   - PyTorch
        
        - node_policy_pth_cpu.json
        - node_policy_pth_nano.json
        - user_input_app_pth_cpu.json
        - user_input_app_pth_nano.json
      
   - OpenVINO 
    
        - node_policy_vino.json
        - user_input_app_vino.json
      
### 3. Setup ENV variables. 
   Add all of the following `export` in a file `APP_ENV` and **source** them in your current shell before you can register the node. These ENVIRONMENT variables are required to register the edge node. Review and provide values as per your environment. You may copy and paste this ENV block in an editor.

```
#### Enviornment variables EDGE_OWNER, EDGE_DEPLOY to identify service. Change as needed to organize your service, policy names etc.
export EDGE_OWNER=<change-as-needed> e.g sg.edge           
export EDGE_DEPLOY=<change-as-needed> e.g example.visual 

#### Specify your docker base
export DOCKER_BASE=<change-as-needed> e.g edgedock

### Authenticated docker access ###
export CR_DOCKER_HOST=index.docker.io
export CR_DOCKER_USERNAME=<change-as-needed> e.g edgedock
export CR_DOCKER_APIKEY=<change-as-needed>
##################################

### Authenticated IBM CR access. MVI images are stored locally and NOT published in docker hub ###
export CR_IBM_HOST=us.icr.io
export CR_IBM_USERNAME=iamapikey
export CR_IBM_HOST_NAMESPACE=<change-as-needed> e.g ieam-mvi
export APP_CR_API_KEY_RO_PULL=<change-as-needed>
##################################
    
# Sets the root of the bind volume. Create this before running the applciation with 777 access
export APP_BIND_HORIZON_DIR=/var/local/horizon

### MVI specfic
export APP_BIND_HORIZON_MVI_MDOEL_DIR=$APP_BIND_HORIZON_DIR/ml/model/mvi
export APP_MODEL_MVI_DOCKER_IMAGE_BASE=us.icr.io/<change-as-needed>/vision-dnn-deploy
export APP_MODEL_MVI_ENVIRONMENT='"BASE=CAFFE","OMP_NUM_THREADS=4"'
export APP_MODEL_MVI_COMMAND='"/opt/DNN/bin/setup_env_and_run.sh","/opt/DNN/bin/deploy_zipped_model.py","--gpu","-1"'
export APP_MODEL_MVI_ENVIRONMENT_P100='"BASE=CAFFE","OMP_NUM_THREADS=16"'
export APP_MODEL_MVI_COMMAND_P100='"/opt/DNN/bin/setup_env_and_run.sh","/opt/DNN/bin/deploy_zipped_model.py","--gpu","0"'
export APP_MI_MVI_MODEL_ZIP=mi_mvi_model.zip
export APP_CONFIG_MODEL_MVI_ZIP="/config/dropins/model.zip"
export APP_MODEL_MVI_SERVICE_HOST_PORT=6011
export APP_MODEL_MVI_SERVICE_PORT=5001
export APP_REMOTE_MODEL_MVI_HOST=<remote-host-ip-address-if-using-this>
### MVI specfic

### mms example being used for config management
export APP_MMS_OBJECT_SERVICE_NAME_CONFIG="$EDGE_OWNER.$EDGE_DEPLOY.mmsconfig"

### These values are used by the application and extracted from your environment. Change if you need to
export HZN_DEVICE_ID=`grep HZN_DEVICE_ID /etc/default/horizon | cut -d'=' -f2 | tr '[a-z]' '[A-Z]'`
export HZN_EXCHANGE_NODE_AUTH="$HZN_DEVICE_ID:"`echo $HZN_DEVICE_ID | tr '[A-Z]' '[a-z]'`
export DEVICE_ID=`echo $HZN_DEVICE_ID | tr '[A-Z]' '[a-z]'`
export DEVICE_NAME=<change-as-needed> e.g. "Intel NUC"
# Make sure to update the /etc/hosts with One IP address that should be used by MMS to poll. Following command should rerurn one IP
export DEVICE_IP_ADDRESS=`hostname -i`
export APP_IEAM_API_CSS_OBJECTS=https://`grep -viE '^$|^#' /etc/default/horizon |  grep HZN_EXCHANGE_URL | cut -d'=' -f2 | cut -d'/' -f3`/edg
e-css/api/v1/objects

#### Application startup conditions
export SHOW_OVERLAY=true
export DETECT_FACE=true
export BLUR_FACE=false
export PUBLISH_KAFKA=false
export PUBLISH_STREAM=true
# Command line option -v 
#export APP_VIEW_COLUMNs=3

export EVENTSTREAMS_ENHANCED_TOPIC=<change-as-needed> e,g. es-topic-tflite
export EVENTSTREAMS_API_KEY=<change-as-needed>
export EVENTSTREAMS_BROKER_URLS=<change-as-needed>
```

### 4. Set and update ENV variables

    source APP_ENV

### 5. Register node
Use comprehensive `node_register_app.sh` to register node. Various example commands below with different options 

#### MVI Local
Predictor is running locally on CPU (no GPU) with a specified model. Local detector is started in a separate container with passed model.

`Intel NUC` with 4 video streams : 20 secs
```
./node_register_app.sh -e ~/developer/agent/visual/infer/DEV_ENV_INFER_IEAM42_EDGE -c all -r rtsp://192.168.200.75:8554/rtsp,rtsp://192.168.2
00.79:8554/rtsp -f sample/industrial-control-room-640x360.mp4 -v 2 -k mvi -m model/mvi/caffe-frcnn-facemask-mvi/caffe-frcnn-facemask-mvi-1.0.
0.zip
```

`Intel NUC` with 2 streams : 10 secs
```
./node_register_app.sh -e ~/developer/agent/visual/infer/DEV_ENV_INFER_IEAM42_EDGE -f sample/industrial-control-room-640x360.mp4 -v 1 -k mvi 
-m model/mvi/caffe-frcnn-facemask-mvi/caffe-frcnn-facemask-mvi-1.0.0.zip
```

`Intel NUC` with 1 stream : 5 secs
```
./node_register_app.sh -e ~/developer/agent/visual/infer/DEV_ENV_INFER_IEAM42_EDGE -f sample/industrial-control-room-640x360.mp4 -v 1 -k mvi 
-m model/mvi/caffe-frcnn-facemask-mvi/caffe-frcnn-facemask-mvi-1.0.0.zip
```
#### MVI Remote
Predictor is running locally but accesses a detector running in cloud on GPU P100. Round trip: 0.8 sec 
```
./node_register_app.sh -e ~/developer/agent/visual/infer/DEV_ENV_INFER_IEAM42_EDGE -c all -r rtsp://192.168.200.75:8554/rtsp -k mvi_p100 -v 2
```

#### TensorFlow lite Local

`Intel NUC`
```
./node_register_app.sh -e ~/developer/project/visual/infer/DEV_ENV_INFER_IEAM42_EDGE -c all -r rtsp://192.168.200.75:8554/rtsp,rtsp://192.168
.200.79:8554/rtsp -f sample/industrial-control-room-640x360.mp4 -k tflite -m model/tflite/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip -v 2

./node_register_app.sh -e ~/developer/project/visual/infer/DEV_ENV_INFER_IEAM42_EDGE -c all -r rtsp://192.168.200.75:8554/rtsp -f sample/indu
strial-control-room-640x360.mp4 -k tflite -m model/tflite/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip -v 2
```

#### PyTorch Local

`Intel NUC` Inference time 9-10 secs : pth_cpu
```
./node_register_app.sh -e ~/developer/agent/visual/infer/DEV_ENV_INFER_IEAM42_EDGE -c all -r rtsp://192.168.200.75:8554/rtsp,rtsp://192.168.2
00.79:8554/rtsp -f sample/industrial-control-room-640x360.mp4 -k pth_cpu -m model/pth/pth-frcnn-resnet50-dct-facemask-kaggle-1.0.0-mms.zip -v
```

`Jetson nano`: Pytorch models are bigger in comparison with tflite models

* pth_cpu on Jetson Nano is very slow. In the three video streams below 70, 60, 84s etc secs detection time. Works but not could be better.

```
./node_register_app.sh -e ~/developer/agent/visual/infer/DEV_ENV_INFER_IEAM42_EDGE -r rtsp://192.168.200.75:8554/rtsp,rtsp://192.168.200.79:8
554/rtsp -f /var/local/horizon/sample/video/industrial-control-room-640x360.mp4 -v 2 -k pth_cpu -m model/pth/pth-frcnn-resnet50-dct-facemask-
kaggle-1.0.0-mms.zip 
```

* pth_gpu on Jetson Nano is still slow. In the one video stream 3-4 secs deteection time. Takes longer to load so wait.
```
./node_register_app.sh -e ~/developer/agent/visual/infer/DEV_ENV_INFER_IEAM42_EDGE -r rtsp://192.168.200.75:8554/rtsp -v 1 -k pth_gpu -m mode
l/pth/pth-frcnn-resnet50-dct-facemask-kaggle-1.0.0-mms.zip 

./node_register_app.sh -e ~/developer/agent/visual/infer/DEV_ENV_INFER_IEAM42_EDGE -k pth_gpu -m model/pth/pth-frcnn-resnet50-dct-facemask-ka
ggle-1.0.0-mms.zip -r rtsp://192.168.200.75:8554/rtsp,rtsp://192.168.200.79:8554/rtsp  -v 2
```

#### OpenVINO Local
Default model is included in the detector. Works with one input as there can be only one instace of vinoDetector. TODO: Need to figure
 out a way to share the same instance
```
./node_register_app.sh -e ~/developer/agent/visual/infer/DEV_ENV_INFER_IEAM42_EDGE -c all -r rtsp://192.168.200.75:8554/rtsp -k vino -v 1
```

#### 6. View/access result by one or more methods

- View streaming output in a browser 
    
    `http://<local-ip-address>:5000/stream`
    
- Take snapshot of the annotated frame
    
    `http://<local-ip-address>:5000/test`
    
- Get a file output locally (to test on the local edge node)
    
      wget http://<local-ip-address>:5000/wget
    
      cat wget | base64 -d > wget.jpg`
