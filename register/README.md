### README

1. Verify the output of following command. It should return one IP address that you use to ssh into the edge device. e.g. **e 192.168.x.x your-hostname**

        hostname -i
        
   The output of above command should not be the local loopback address (e.g. 127.0.x.x) or have mutiple addresses. If that is the case then edit **/etc/hosts** and make an entry for your hostnaame 

        <ip-address> <your-hostname> 
        
  Verify the result of the above command again.
  
2. Copy **node_policy_tflite.json** and **user_input_app_tflite.json** locally 
  
3. Setup ENV variables. Add all of the following **export** in a file and **source** them before registrering the node. These ENVIRONMENT variables are required to build application, add policies and register edge node. Review and provide values based on your environment.

```
#### Enviornment variables EDGE_OWNER, EDGE_DEPLOY to identify service
export EDGE_OWNER=sg.edge           # Keep this value
export EDGE_DEPLOY=example.visual.  # Keep this value
    
#### IEAM specific. Update values in < > brackets
# Keep this value
export HZN_ORG_ID=mycluster  
# Update iam-api-key with the value provided to you
export HZN_EXCHANGE_USER_AUTH=iamapikey:<iam-api-key> 
# Update with arbitrary values for your node 
export HZN_EXCHANGE_NODE_AUTH="<UNIQUE-NODE-NAME>:<node-token>"
# No change needed here
export HZN_DEVICE_ID=`grep HZN_DEVICE_ID /etc/default/horizon | cut -d'=' -f2` 

#### Application specific 
# Provide any arbitrary name as the node should appear in IEAM. Keep it same as above
export APP_NODE_NAME=<UNIQUE-NODE-ANME> 
# Provide any arbitrary id for the node that may identify your edge-node
export DEVICE_ID=<device-id>
# Provide any arbitrary short name for the node 
export DEVICE_NAME="<short device name"
# Automtically created based on work done in step 1 above.
export DEVICE_IP_ADDRESS=`hostname -i`  
  
#### Application specific for MMS. Used by UI for configration update via MMS 
# Automtically created. Keep this as such
export APP_IEAM_API_CSS_OBJECTS=https://`grep -viE '^$|^#' /etc/default/horizon |  grep HZN_EXCHANGE_URL | cut -d'=' -f2 | cut -d'/' -f3`/edge-css/api/v1/objects
# Provide same api-key value provided to you
export APP_APIKEY_PASSWORD=<api-key-provided-to-you>
# Keep this as such
export APP_MMS_OBJECT_ID_CONFIG="config.json"
# Keep this as such
export APP_MMS_OBJECT_TYPE_CONFIG="tflite-mmsconfig"
# Automtically updated. Keep this as such. 
export APP_MMS_OBJECT_SERVICE_NAME_CONFIG="$EDGE_OWNER.$EDGE_DEPLOY.mms"
# Keep this as such. Will change in future
export APP_MMS_OBJECT_ID_MODEL="mobilenet-tflite-1.0.0-mms.tar.gz"
# Keep this as such. 
export APP_MMS_OBJECT_TYPE_MODEL="tflite-mmsmodel"
# Automtically updated. Keep this as such.
export APP_MMS_OBJECT_SERVICE_NAME_MODEL="$EDGE_OWNER.$EDGE_DEPLOY.mms"   
 
# Keep this as such.
export APP_BIND_HORIZON_DIR=/var/tmp/horizon
    
# Keep these as such. face detection disabled for now as haarscascade based detection is not reliable
export SHOW_OVERLAY=true # false to hide OVERLAY
export DETECT_FACE=false
export BLUR_FACE=false
export PUBLISH_KAFKA=false # To send kafka stream
export PUBLISH_STREAM=true # to send local mjpeg stream and view in browser
export VIEW_COLUMN=1

#### RTSP Streams
# Keep this as such if do not have any RTSP_STREAM
export RTSP_STREAMS=""
# If have RTSP_STREAM setup, then add as below separated by comma
export RTSP_STREAMS=rtsp://<ip-address>:<port>/rtsp,rtsp://<ip-address>:<port>/rtsp

#### For streaming content to IBM Event Streams
export EVENTSTREAMS_ENHANCED_TOPIC=<your-event-stream-topic>
export EVENTSTREAMS_API_KEY=<your-event-stream-api-key>
export EVENTSTREAMS_BROKER_URLS="your-event-stream-brokers"

'''

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
