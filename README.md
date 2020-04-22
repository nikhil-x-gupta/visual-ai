## IEAM 4.0 - OpenCV and TensorFlow Lite based Object Classification

### Introduction

A python based implementation using two containers with detection time below < 0.4 sec without any GPU accelerator on Intel NUC using coco_ssd_mobilenet_v1_1.0 model

- Image capture and classification
- Http and kafka message bridge

### Build, Publish and Use in a shared IEAM environment

Using a shared instance creates several challenges when services, patterns and policies need to be published in a common exchange without multiple developers clobbering over each other.

### Issues

- Developers need to identify their service, pattern and policies among many similar assets (concept of owner)
- Developers may have project for demo, dev, test and more ( group the assets)
- Developers need to use their own docker repository (specify own docker account)

The tooling outlined below addresses these concerns and builds on top of existing infrastructure

### Automated Steps

Start with reviewing Makefile for targets.

Build and publish images to docker and services to exchange. Can be executed again and again.

    make

Publish pattern

    make publish-pattern

Publish business-policy

    make add-business-policy

### ENVIRONMENT variables

Must define following ENVIRONMENT variables to build application, add policies and register edge node.

Enviornment variables EDGE_OWNER, EDGE_DEPLOY provide flexiblity for different developers to use the same exchange without clobering over each other.

    export EDGE_OWNER=<a-two-or-three-letter-distinctive-initial-of-your-name>  # sg.dev  
    export EDGE_DEPLOY=<deploy-target> # e.g: example.tfvisual

    export DOCKER_BASE=<docker-base> # e.g. Change this this your docker base 

    export HZN_ORG_ID=mycluster
    export HZN_EXCHANGE_USER_AUTH=iamapikey:<iam-api-key>
    export HZN_EXCHANGE_NODE_AUTH="<UNIQUE-NODE-ANME>:<node-token>"
    export APP_NODE_NAME=<UNIQUE-NODE-ANME>

### Application specific

    export DEVICE_ID=<unique-device-id>
    export DEVICE_NAME="<short device name"
    export SHOW_OVERLAY=true # false to hide OVERLAY

### Event Streams

    export EVENTSTREAMS_BASIC_TOPIC=<your-event-stream-topic>
    export EVENTSTREAMS_ENHANCED_TOPIC=<your-event-stream-topic>
    export EVENTSTREAMS_API_KEY=<your-event-stream-api-key>
    export EVENTSTREAMS_BROKER_URLS="your-event-stream-brokers"

### Create node

    hzn exchange node create -n $HZN_EXCHANGE_NODE_AUTH

### Register node - NUC (amd64)
Use script to register node

policy

    ./node_register_app.sh -e ENV_TFVISUAL_DEV -r -l

pattern

    ./node_register_app.sh -e ENV_TFVISUAL_DEV -r -p
