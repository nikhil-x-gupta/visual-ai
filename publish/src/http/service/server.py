from flask import Flask
from flask import Response
from flask import render_template
from flask import request

import base64
import json
import os
import requests
import subprocess
import uuid
import threading
import time

EVENTSTREAMS_BROKER_URLS = os.environ['EVENTSTREAMS_BROKER_URLS']
EVENTSTREAMS_API_KEY = os.environ['EVENTSTREAMS_API_KEY']
EVENTSTREAMS_ENHANCED_TOPIC = os.environ['EVENTSTREAMS_ENHANCED_TOPIC']

PUBLISH_KAFKA_COMMAND = ' kafkacat -P -b ' + EVENTSTREAMS_BROKER_URLS + ' -X api.version.request=true -X security.protocol=sasl_ssl -X sasl.mechanisms=PLAIN -X sasl.username=token -X sasl.password="' + EVENTSTREAMS_API_KEY + '" -t ' + EVENTSTREAMS_ENHANCED_TOPIC + ' '

# edge-css/api/v1/objects
ieam_api_css_objects = os.environ['APP_IEAM_API_CSS_OBJECTS']
username = os.environ['APP_APIKEY_USERNAME']
password = os.environ['APP_APIKEY_PASSWORD']

hzn_org_id = os.environ['HZN_ORGANIZATION']
object_id_cfg = os.environ['APP_MMS_OBJECT_ID_CONFIG']
object_type_cfg = os.environ['APP_MMS_OBJECT_TYPE_CONFIG']
object_service_name_cfg = os.environ['APP_MMS_OBJECT_SERVICE_NAME_CONFIG']

server = Flask(__name__)

g_stream_frame = None
g_lock = threading.Lock()

def generate_stream_MJPEG_WIP():
    global g_stream_frame, g_lock
    
    count = 0
    while True:
        with g_lock:
            if g_stream_frame is None:
                image_name = 'test-image-' + str(count) + '.jpg'
                image_path = os.path.join('/static', image_name)
                with open(image_path, "rb") as image:
                    frame_read = image.read()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_read + b'\r\n')
                time.sleep(0.1)            
                return
            else:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + g_stream_frame + b'\r\n')

def generate_stream_MJPEG():
    global g_stream_frame, g_lock

    count = 0
    while True:
        if g_stream_frame is None:
            image_name = 'test-image-' + str(count) + '.jpg'
            image_path = os.path.join('/static', image_name)
            if (count > 4):
                count = 0
            time.sleep(1)
            with open(image_path, "rb") as image:
                frame_read = image.read()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_read + b'\r\n')
        else:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + g_stream_frame + b'\r\n')

# Stream resource url_for. To be called in HTML as <img width="640" heigh="480" src="{{ url_for('stream_video') }}"/>
@server.route('/stream_video')
def stream_video():
    return Response(generate_stream_MJPEG(), mimetype = "multipart/x-mixed-replace; boundary=frame")

# End point for the host as http://<ip-address>:5000/stream 
@server.route('/stream')
def stream():
    return render_template('stream.html')

# Default URL http://<ip-address>:5000/
@server.route('/')
def index():
    return render_template('index.html')

# Used by client to publish MJPEG streaming content
@server.route('/publish/stream', methods=['POST'])
def publish_stream():
    global g_stream_frame, g_lock
    if request.headers['Content-Type'] == 'application/json':
        with g_lock:
            g_stream_frame = base64.b64decode(request.json["detect"]["image"])
    return ""

@server.route('/publish/kafka', methods=['POST'])
def publish_kafka():
    if request.headers['Content-Type'] == 'application/json':
        json_str = json.dumps(request.json)
        TMP_FILE = '/tmp/kafka-' + str(uuid.uuid4()) + '.json'
        with open(TMP_FILE, 'w+') as tmp_file:
            tmp_file.write(json_str)
            tmp_file.close()
            discard = subprocess.run(PUBLISH_KAFKA_COMMAND + TMP_FILE + '; rm ' + TMP_FILE, shell=True)
    return ""

def object_type_pattern(obj_id, obj_type, dest_org_id, dest_type, dest_id):
    obj_type_d = {}

    obj_type_d['objectID'] = obj_id
    obj_type_d['objectType'] = obj_type
    obj_type_d['destinationOrgID'] = dest_org_id
    obj_type_d['destinationType'] = dest_type
    obj_type_d['destinationID'] = dest_id

    dict = {}
    dict['meta'] = obj_type_d

    return dict

def object_type_config_policy(org_id, obj_service_name, obj_id, obj_type):
    obj_type_d = {}

    service_d = {}

    service_d['orgID'] = org_id
    service_d['arch'] = "*"
    service_d['serviceName'] = obj_service_name
    service_d['version'] = "[0.0.0,INFINITY)"
    
    services = []
    services.append(service_d)

    destination_policy_d = {}
    destination_policy_d['properties'] = []
    destination_policy_d['constraints'] = []
    destination_policy_d['services'] = services

    obj_type_d['objectID'] = obj_id
    obj_type_d['objectType'] = obj_type
    obj_type_d['destinationOrgID'] = org_id
    obj_type_d['destinationPolicy'] = destination_policy_d

    dict = {}
    dict['meta'] = obj_type_d

    return dict

@server.route('/update/config', methods=['POST'])
def update_config_policy():
    if request.headers['Content-Type'] == 'application/json':
        obj_type_d = object_type_config_policy(hzn_org_id, object_service_name_cfg, object_id_cfg, object_type_cfg)

        config_d = {}

        if request.json["overlay"]:
            config_d['SHOW_OVERLAY'] = 'true'
        else:
            config_d['SHOW_OVERLAY'] = 'false'

        if request.json["face"]:
            config_d['DETECT_FACE'] = 'true'
        else:
            config_d['DETECT_FACE'] = 'false'

        if request.json["blur"]:
            config_d['BLUR_FACE'] = 'true'
        else:
            config_d['BLUR_FACE'] = 'false'

        if request.json["kafka"]:
            config_d['PUBLISH_KAFKA'] = 'true'
        else:
            config_d['PUBLISH_KAFKA'] = 'false'
    
        if request.json["stream"]:
            config_d['PUBLISH_STREAM'] = 'true'
        else:
            config_d['PUBLISH_STREAM'] = 'false'

        # Always on Forcing PUBLISH_STREAM : TODO: Consider removing
        config_d['PUBLISH_STREAM'] = 'true'

        obj_type_json_str = json.dumps(obj_type_d)
        config_json_str = json.dumps(config_d)

        # using python requests to make API call
        url_css_put = ieam_api_css_objects + '/' + hzn_org_id + '/' + object_type_cfg + '/' + object_id_cfg
        # url_css_put = ieam_url + '/edge-css/api/v1/objects' + '/' + hzn_org_id + '/' + object_type_cfg + '/' + object_id_cfg
        res_obj_type = requests.put(url_css_put, auth = (hzn_org_id + '/' + username, password), data=obj_type_json_str, verify=False)

        # if res_obj_type.status_code < 300:
        # using python requests to make API call
        url_css_put_data = ieam_api_css_objects + '/' + hzn_org_id + '/' + object_type_cfg + '/' + object_id_cfg + '/data'
        # url_css_put_data = ieam_url + '/edge-css/api/v1/objects' + '/' + hzn_org_id + '/' + object_type_cfg + '/' + object_id_cfg + '/data'
        res_obj_data = requests.put(url_css_put_data, auth = (hzn_org_id + '/' + username, password), data=config_json_str, verify=False)

        #if res_obj_data.status_code < 300:
        # using python requests to make API call
        url_css_status = ieam_api_css_objects + '/' + hzn_org_id + '/' + object_type_cfg + '/' + object_id_cfg + '/' + 'status'
        # url_css_status = ieam_url + '/edge-css/api/v1/objects' + '/' + hzn_org_id + '/' + object_type_cfg + '/' + object_id_cfg + '/' + 'status'
        res_css_status = requests.get(url_css_status, auth = (hzn_org_id + '/' + username, password), verify=False)

        # req_json_str = "request.json:" + json.dumps(request.json) + ":request.json"
        # response = server.response_class(response=res_css_status.content + str.encode(' :obj_type_json_str: ') + str.encode(obj_type_json_str) + str.encode(' :obj_type_json_str') + str.encode('config_json_str: ') + str.encode(config_json_str) + str.encode(' :config_json_str') + str.encode(' ==rjs== ') + str.encode(req_json_str) + str.encode(' ==rjs== '), status=res_css_status.status_code, mimetype='text/plain')

        response = server.response_class(response=res_css_status.content, status=res_css_status.content.status_code, mimetype='text/plain')
        return response
    else:
        response = server.response_class(response=str.encode("No-JSON"), status=200, mimetype='text/plain')
        return response
        
@server.route('/css/status', methods=['GET', 'POST'])
def css_status():
    # url_css_status = ieam_url + '/ec-css/api/v1/objects' + '/' + hzn_org_id + '/' + object_type + '/' + object_id + '/' + 'status' 
    # url_css_status = ieam_url + '/edge-css/api/v1/objects' + '/' + hzn_org_id + '/' + object_type_cfg + '/' + object_id_cfg + '/' + 'status'
    url_css_status = ieam_api_css_objects + '/' + hzn_org_id + '/' + object_type_cfg + '/' + object_id_cfg + '/' + 'status'

    req = requests.get(url_css_status, auth = (hzn_org_id + '/' + username, password), verify=False)
    response = server.response_class(response=req.content + str.encode(url_css_status), status=req.status_code, mimetype='text/plain')

    return response

if __name__ == '__main__':
    server.run(debug=True, host='0.0.0.0')
