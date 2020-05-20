from flask import Flask
from flask import Response
from flask import render_template
from flask import send_file
from flask import request

import base64
import json
import os
import requests
import subprocess
import uuid
import threading
import time
import logging

EVENTSTREAMS_BROKER_URLS = os.environ['EVENTSTREAMS_BROKER_URLS']
EVENTSTREAMS_API_KEY = os.environ['EVENTSTREAMS_API_KEY']
EVENTSTREAMS_ENHANCED_TOPIC = os.environ['EVENTSTREAMS_ENHANCED_TOPIC']

PUBLISH_KAFKA_COMMAND = ' kafkacat -P -b ' + EVENTSTREAMS_BROKER_URLS + ' -X api.version.request=true -X security.protocol=sasl_ssl -X sasl.mechanisms=PLAIN -X sasl.username=token -X sasl.password="' + EVENTSTREAMS_API_KEY + '" -t ' + EVENTSTREAMS_ENHANCED_TOPIC + ' '

hzn_org_id = os.environ['HZN_ORGANIZATION']
ieam_url = os.environ['APP_IEAM_URL']
username = os.environ['APP_APIKEY_USERNAME']
password = os.environ['APP_APIKEY_PASSWORD']
object_type = os.environ['APP_MMS_OBJECT_TYPE_CONFIG']
object_id = os.environ['APP_MMS_OBJECT_ID_CONFIG']

server = Flask(__name__)

g_stream_frame = None
g_lock = threading.Lock()

def generate_stream_MJEPG_WIP():
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

def generate_stream_MJEPG():
    global g_stream_frame, g_lock

#    g_stream_frame = None
    
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

#            time.sleep(2)
#            g_stream_frame = None

# Stream resource url_for. To be called in HTML as <img width="640" heigh="480" src="{{ url_for('stream_video') }}"/>
@server.route('/stream_video')
def stream_video():
    return Response(generate_stream_MJEPG(), mimetype = "multipart/x-mixed-replace; boundary=frame")

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

@server.route('/update/config', methods=['GET', 'PUT', 'POST'])
def update_config_pattern():

    obj_type_d = object_type_pattern(object_id, object_type, hzn_org_id, "pattern-sg.edge.example.tfvisual.tflite-amd64", "")

    config_d = {}

    if request.args.get('overlay') == 'on':
        config_d['SHOW_OVERLAY'] = 'true'
    else:
        config_d['SHOW_OVERLAY'] = 'false'

    if request.args.get('face') == 'on':
        config_d['DETECT_FACE'] = 'true'
    else:
        config_d['DETECT_FACE'] = 'false'

    if request.args.get('blur') == 'on':
        config_d['BLUR_FACE'] = 'true'
    else:
        config_d['BLUR_FACE'] = 'false'

    if request.args.get('kafka') == 'on':
        config_d['PUBLISH_KAFKA'] = 'true'
    else:
        config_d['PUBLISH_KAFKA'] = 'false'
    
    if request.args.get('stream') == 'on':
        config_d['PUBLISH_STREAM'] = 'true'
    else:
        config_d['PUBLISH_STREAM'] = 'false'

    obj_type_json_str = json.dumps(obj_type_d)
    config_json_str = json.dumps(config_d)

    url_css_put = ieam_url + '/ec-css/api/v1/objects' + '/' + hzn_org_id + '/' + object_type + '/' + object_id
    req_obj_type = requests.put(url_css_put, auth = (hzn_org_id + '/' + username, password), data=obj_type_json_str, verify=False)

    url_css_put_data = ieam_url + '/ec-css/api/v1/objects' + '/' + hzn_org_id + '/' + object_type + '/' + object_id + '/data'
    req_config = requests.put(url_css_put_data, auth = (hzn_org_id + '/' + username, password), data=config_json_str, verify=False)
    
    url_css_status = ieam_url + '/ec-css/api/v1/objects' + '/' + hzn_org_id + '/' + object_type + '/' + object_id + '/' + 'status'
    req = requests.get(url_css_status, auth = (hzn_org_id + '/' + username, password), verify=False)
    response = server.response_class(response=req.content + str.encode('====') + req_obj_type.content + str.encode('====') + req_config.content,
                                     status=200,
                                     mimetype='text/plain')

    return response

@server.route('/css/status', methods=['GET', 'POST'])
def css_status():
    url_css_status = ieam_url + '/ec-css/api/v1/objects' + '/' + hzn_org_id + '/' + object_type + '/' + object_id + '/' + 'status'

    req = requests.get(url_css_status, auth = (hzn_org_id + '/' + username, password), verify=False)
    response = server.response_class(response=req.content + str.encode(url_css_status),
                                     status=200,
                                     mimetype='text/plain')
    return response

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    server.run(debug=True, host='0.0.0.0')
