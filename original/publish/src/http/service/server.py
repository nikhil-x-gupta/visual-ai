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
import logging

# Screen view columns width based on column
def get_ui_frame():
    try:
        app_view_cols = os.environ['APP_VIEW_COLUMNS']
        view_cols = int(app_view_cols)
    except:
        view_cols = 1

    return 1280 if view_cols == 1 else 640

# Pass "secret" or "env" as url /admin/secret or /admin/env and global dict for mms cred setup
def get_mms_config(cred_src, dict):
    if cred_src == "secret":
        try:
            with open(os.environ['HZN_ESS_AUTH']) as hzn_ess_auth_file:
                tmp_ess_auth = json.load(hzn_ess_auth_file)
                CURL_QUERY_SECRET_COMMAND = "curl https://localhost/api/v1/secrets/APP_APIKEY_PASSWORD -u " + tmp_ess_auth['id'] + ":" + tmp_ess_auth['token'] + " --cacert /ess-cert/cert.pem --unix-socket /var/run/horizon/essapi.sock"
                tmp_data_out = subprocess.run(CURL_QUERY_SECRET_COMMAND, capture_output=True, shell=True)
                tmp_secret_bytes = tmp_data_out.stdout
                tmp_secret_str = tmp_secret_bytes.decode('utf-8')
                tmp_secret_json = json.loads(tmp_secret_str)
                dict['password'] = tmp_secret_json['value']
        except:
            dict.pop('password', None)
    elif cred_src == "env":
        try:
            tmp_val = os.environ['APP_APIKEY_PASSWORD']
            if tmp_val == '-':
                dict.pop('password', None)
            else:
                dict['password'] = tmp_val
        except:
            dict.pop('password', None)
    else:
        None

    tmp_key = 'APP_MMS_OBJECT_SERVICE_NAME_CONFIG'
    dict[tmp_key] = os.environ[tmp_key]
    dict['username'] = os.environ['APP_APIKEY_USERNAME'] 

# kafka publish creds. TODO: Use secret manager
def get_mms_publish_kafka():
    tmp_mms_publish_kafka_dict = {}
    try:
        tmp_key = 'EVENTSTREAMS_BROKER_URLS'
        tmp_env = os.environ[tmp_key]
        if tmp_env != '-':
            tmp_mms_publish_kafka_dict[tmp_key] = tmp_env
    except:
        None

    try:
        tmp_key = 'EVENTSTREAMS_API_KEY'
        tmp_env = os.environ[tmp_key]
        if tmp_env != '-':
            tmp_mms_publish_kafka_dict[tmp_key] = tmp_env
    except:
        None

    try:
        tmp_key = 'EVENTSTREAMS_VISUAL_ML_TOPIC'
        tmp_env = os.environ[tmp_key]
        if tmp_env != '-':
            tmp_mms_publish_kafka_dict[tmp_key] = tmp_env
    except:
        None

    return tmp_mms_publish_kafka_dict

def generate_still_wget():
    global g_stream_frame

    if g_stream_frame is not None:
        b64_frame = (base64.b64encode(g_stream_frame)).decode('utf8')
        yield (b64_frame)

def generate_still_test():
    global g_stream_frame

    if g_stream_frame is not None:
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

def object_type_policy(org_id, obj_service_name, obj_id, obj_type):
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

def mms_config(cred_src, dict):
    get_mms_config(cred_src, dict)
    if dict.get('password') and dict.get('APP_MMS_OBJECT_SERVICE_NAME_CONFIG'):
        tmp_show_config = 'contents'
        tmp_show_warning = 'none' 
    else:
        tmp_show_config = 'none' 
        tmp_show_warning = 'contents'

    return tmp_show_config, tmp_show_warning

object_type_cfg = "mmsconfig"
object_id_cfg = "config.json"
admin_html = 'admin.html'
stream_html = 'stream.html'

# Edge agent injects these in each container
hzn_org_id = os.environ['HZN_ORGANIZATION']
ieam_api_css_objects = os.environ['HZN_EXCHANGE_URL'] + "../../edge-css/api/v1/objects"

# Setup MMS config params
mms_config_publish_dict = {}
show_config, show_warning = mms_config("env", mms_config_publish_dict)

# Initilize event stream creds and ui appearance
mms_publish_kafka_dict = get_mms_publish_kafka()
show_publish_kafka = 'auto:opacity:1' if len(mms_publish_kafka_dict) == 3 else 'none;opacity:0.4'
show_publish_kafka_error = 'none' if len(mms_publish_kafka_dict) == 3 else 'contents'
width = get_ui_frame()

g_stream_frame = None
g_lock = threading.Lock()

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

server = Flask(__name__)

# Stream resource url_for. To be called in HTML as <img width="640" heigh="480" src="{{ url_for('stream_video') }}"/>
@server.route('/stream_video')
def stream_video():
    return Response(generate_stream_MJPEG(), mimetype = "multipart/x-mixed-replace; boundary=frame")

@server.route('/stream')
def stream():
    return render_template(stream_html, width=width, show_warning=show_warning)

# End point for the host as http://<ip-address>:5000/stream 
@server.route('/admin/<cred_src>')
def admin(cred_src):
    show_config, show_warning = mms_config(cred_src, mms_config_publish_dict)
    return render_template(admin_html, width=width, mms_publish_dict=mms_config_publish_dict, mms_publish_kafka_dict=mms_publish_kafka_dict, show_config=show_config, show_warning=show_warning, show_publish_kafka=show_publish_kafka, show_publish_kafka_error=show_publish_kafka_error)

@server.route('/test')
def test():
    return Response(generate_still_test(), mimetype = "multipart/x-mixed-replace; boundary=frame")

@server.route('/wget')
def test_wget():
    return Response(generate_still_wget(), mimetype = "image/jpeg")

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
        PUBLISH_KAFKA_COMMAND = ' kafkacat -P -b ' + mms_publish_kafka_dict['EVENTSTREAMS_BROKER_URLS'] + ' -X api.version.request=true -X security.protocol=sasl_ssl -X sasl.mechanisms=PLAIN -X sasl.username=token -X sasl.password="' + mms_publish_kafka_dict['EVENTSTREAMS_API_KEY'] + '" -t ' + mms_publish_kafka_dict['EVENTSTREAMS_VISUAL_ML_TOPIC'] + ' '
        json_str = json.dumps(request.json)
        TMP_FILE = '/tmp/kafka-' + str(uuid.uuid4()) + '.json'
        with open(TMP_FILE, 'w+') as tmp_file:
            tmp_file.write(json_str)
            tmp_file.close()
            discard = subprocess.run(PUBLISH_KAFKA_COMMAND + TMP_FILE + '; rm ' + TMP_FILE, shell=True)
    return ""

@server.route('/update/config', methods=['POST'])
def update_config_policy():
    if request.headers['Content-Type'] == 'application/json':
        username = mms_config_publish_dict['username']
        password = mms_config_publish_dict['password']

        object_service_name_cfg = mms_config_publish_dict['APP_MMS_OBJECT_SERVICE_NAME_CONFIG']
        obj_type_d = object_type_policy(hzn_org_id, object_service_name_cfg, object_id_cfg, object_type_cfg)

        config_d = {}

        if "overlay" in request.json:
            if request.json["overlay"]:
                config_d['SHOW_OVERLAY'] = 'true'
            else:
                config_d['SHOW_OVERLAY'] = 'false'

        if "face" in request.json:
            if request.json["face"]:
                config_d['DETECT_FACE'] = 'true'
            else:
                config_d['DETECT_FACE'] = 'false'

        if "blur" in request.json:
            if request.json["blur"]:
                config_d['BLUR_FACE'] = 'true'
            else:
                config_d['BLUR_FACE'] = 'false'

        if "kafka" in request.json:
            if request.json["kafka"]:
                config_d['PUBLISH_KAFKA'] = 'true'
            else:
                config_d['PUBLISH_KAFKA'] = 'false'
    
        if "stream" in request.json:
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

        response = server.response_class(response=res_css_status.content, status=res_css_status.content.status_code, mimetype='text/plain')
        return response
    else:
        response = server.response_class(response=str.encode("No-JSON"), status=200, mimetype='text/plain')
        return response
        
@server.route('/css/status', methods=['GET', 'POST'])
def css_status():
    username = mms_config_publish_dict['username']
    password = mms_config_publish_dict['password']

    url_css_status = ieam_api_css_objects + '/' + hzn_org_id + '/' + object_type_cfg + '/' + object_id_cfg + '/' + 'status'

    req = requests.get(url_css_status, auth = (hzn_org_id + '/' + username, password), verify=False)
    response = server.response_class(response=req.content + str.encode(url_css_status), status=req.status_code, mimetype='text/plain')

    return res_str

# TODO: Under development
@server.route('/update/model', methods=['POST'])
def update_model_policy(object_type_model, object_id_model, object_service_name_model):
    if request.headers['Content-Type'] == 'application/json':
        print("updating model - TODO")
        obj_type_d = object_type_policy(hzn_org_id, object_service_name_model, object_id_model, object_type_model)

        config_d = {}

        obj_type_json_str = json.dumps(obj_type_d)
        config_json_str = json.dumps(config_d)
    
if __name__ == '__main__':
    server.run(debug=True, host='0.0.0.0')

