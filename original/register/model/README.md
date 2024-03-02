## Deploy Machine Learning model using IEAM Model Management System (MMS) 

### Concept
Deploying machine learning model on edge nodes using Model Management System (MMS), requires publishing model into IEAM Cloud Sync Service (CSS).  The edge agents running on the edge nodes pull the qualified models. The model is delivered to the edge nodes as an asynchronous process and it is upto the already running containerized application service to make use of the just delivered ML model. 

While user simply publishes the ML model into IEAM and edge nodes receive the model in time, internally, the entire publishing process goes through several discrete steps: 

1. User publishes the model using a `publish defintition file` (similar to service definition) and the ML model file itself.
2. The uploading step, stores the model file in IEAM in a separate storage called CSS. 
3. The `publish definition file`, with its own set of consraints, works with the service definition file for a given service and determines which node and which service needs to have this model file.
4. When such a qualifying node reaches out to IEAM, the ML model file delivery process to the edge node begins.
5. File is fetched by the edge node and is stored locally on the edge node.
6. The containerized service running on the edge node can query the system if there is a new ML model file. 
7. Upon such confirmation, the containerized application service can pull the newly delivered ML model and start using in its code.

User only performs the step 1. A properly written application, covering steps 6 and 7, makes use of the just delivered model. 

### Application Specific

In this example application, a separate container `mmsmodel` manages the step 6. Step 7 is part of the application code to pull in the newly delivered model and recalibrate the ML inferencing engine.

For the system to work in an scalable fashion, the application requires (configuarble) certain directory structure. 

1. Application expects `/var/local/horizon` on the edge node, where all the newly delivered model files are stored for the application to make use of.
2. The `publish.definition.file` makes use of the `description` field to specify certain sub-directory structure to organize many applications on the same nooe and avoid overwriting each other.
3. A convenient `publish_model.sh` is provided to organize and ease the publishing step.  

### Pre-requisite for publish_model script

#### publish_model.sh 
1. The script requires model and its version organized in certain directory structure. See example.
2. The model files must be named based on framework and version. See example.

#### model.publish.definition.json
1. Follow the guideline as described in IEAM doc
2. Uses several fields to capture some meta information that is passed to the application by the publisher, and to be used by the application.
3. This application uses `description` field specifically and has guidelines for few other fields. 

**objectID** - User specified unique objectID used in `-i` option of `hzn mms` commands. I use ML model file name. 

**objectType** - User specified obejctType used in `-t` option of `hzn mms` commands. I use `mmsmodel` for ML models

**description and sub-fields**

- subdir  : Subdirectory to organize delivered model. **Used by the application.**

- fmwk    : ML model framework (Can be used by the application. Currently not used) 
- net     : ML network (Can be used by the application as additional info in UI. Currently not used) 
- dataset : Dataset used to train the model (Can be used by the application as additional info in UI. Currently not used)
- version : ML model version number. (Can be used by the application. Currently not used)
- format  : ML model package format. (Can be used by the application. Currently not used) 

**An exampple: model.publish.definition.json**
```
{
    "objectID": "tflite-model-1.0.0-mms.zip",
    "objectType": "mmsmodel",
    "destinationOrgID": "$HZN_ORG_ID",
    "destinationPolicy": {
        "properties": [],
      	"constraints": [
            "owner == $EDGE_OWNER",
            "deploy == $EDGE_DEPLOY",
            "tflite == true"
      	],
      	"services": [
            {
                "orgID": "$HZN_ORG_ID",
                "arch": "*",
                "serviceName": "$EDGE_OWNER.$EDGE_DEPLOY.mmsmodel",
                "version": "[0.0.0,INFINITY)"
            }
        ]
    },
    "description": "{\"fmwk\":\"tflite\",\"net\":\"ssd_mobilenet_v1_1.0_quant\",\"dataset\":\"2018_06_29-coco\",\"version\":\"1.0.0\",\"format\":\"zip\",\"subdir\":\"ml/model/tflite\"}"
}
```





