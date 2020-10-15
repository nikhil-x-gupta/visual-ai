### README

1. Verify the output of following command. It should return one IP address that you use to ssh into the edge device. 

        hostname -i
        
  It should not be the local loopback address. If that is the case then edit /etc/hosts and make an entry like *ip-address hostname* and verify the result of the above command again.
  
2. Copy node_policy_tflite.json and user_input_app_tflite.json locally
  
3. Setup ENV variables
### ENVIRONMENT variables

Must define following ENVIRONMENT variables to build application, add policies and register edge node. Preferebly save in the script directory and use when invoking device registration. 

Enviornment variables EDGE_OWNER, EDGE_DEPLOY provide flexiblity for different developers to use the same exchange without clobering over each other.

    export EDGE_OWNER=sg.edge  
    export EDGE_DEPLOY=example.visual

#### IEAM specific

    export HZN_ORG_ID=mycluster
    export HZN_EXCHANGE_USER_AUTH=iamapikey:<iam-api-key>
    export HZN_EXCHANGE_NODE_AUTH="<UNIQUE-NODE-ANME>:<node-token>"
    export HZN_DEVICE_ID=`grep HZN_DEVICE_ID /etc/default/horizon | cut -d'=' -f2`

#### Application specific
    export APP_NODE_NAME=<UNIQUE-NODE-ANME>
    export DEVICE_ID=<unique-device-id>
    export DEVICE_NAME="<short device name"
    export DEVICE_IP_ADDRESS=`hostname -i`
    
    export APP_IEAM_API_CSS_OBJECTS=https://`grep -viE '^$|^#' /etc/default/horizon |  grep HZN_EXCHANGE_URL | cut -d'=' -f2 | cut -d'/' -f3`/edge-css/api/v1/objects
    export APP_APIKEY_PASSWORD=<api-key-provided-to-you>
    export APP_MMS_OBJECT_ID_CONFIG="config.json"
    export APP_MMS_OBJECT_TYPE_CONFIG="tflite-mmsconfig"
    export APP_MMS_OBJECT_SERVICE_NAME_CONFIG="$EDGE_OWNER.$EDGE_DEPLOY.mms"
    
    export APP_BIND_HORIZON_DIR=/var/tmp/horizon
    
    export APP_MMS_OBJECT_ID_MODEL="<object-model>"
    export APP_MMS_OBJECT_TYPE_MODEL="tflite-mmsmodel"
    export APP_MMS_OBJECT_SERVICE_NAME_MODEL="$EDGE_OWNER.$EDGE_DEPLOY.mms"
    
    # face detection disabled for now as haarscascade based detection is not reliable
    export SHOW_OVERLAY=true # false to hide OVERLAY
    export DETECT_FACE=false
    export BLUR_FACE=false
    export PUBLISH_KAFKA=false # To send kafka stream
    export PUBLISH_STREAM=true # to send local mjpeg stream and view in browser

#### RTSP Streams

    export RTSP_STREAMS=""
    
If you have setuyp 
    export RTSP_STREAMS=rtsp://<ip-address>:<port>/rtsp,rtsp://<ip-address>:<port>/rtsp

#### Event Streams

    export EVENTSTREAMS_BASIC_TOPIC=<your-event-stream-topic>
    export EVENTSTREAMS_ENHANCED_TOPIC=<your-event-stream-topic>
    export EVENTSTREAMS_API_KEY=<your-event-stream-api-key>
    export EVENTSTREAMS_BROKER_URLS="your-event-stream-brokers"

### Create node

    hzn exchange node create -n $HZN_EXCHANGE_NODE_AUTH
    
### Register node using framework TensorFlow lite NUC (amd64), RPI (arm32)
    
    hzn register --policy=node_policy_tflite.json --input-file user_input_app_tflite.json
    hzn register --policy=node_policy_vino.json --input-file user_input_app_vino.json


### View result 

- View streaming output in a browser 
    http://<local-ip-address>:5000/stream
    
- Take spanpshot of annotated frame
    http://<local-ip-address>:5000/test
    
- Get a file output locally (to test on the local machine)
    
        wget http://<local-ip-address>:5000/wget
    
        cat wget | base64 -d > wget.jpg
