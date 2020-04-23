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

import time

EVENTSTREAMS_BROKER_URLS = os.environ['EVENTSTREAMS_BROKER_URLS']
EVENTSTREAMS_API_KEY = os.environ['EVENTSTREAMS_API_KEY']
EVENTSTREAMS_ENHANCED_TOPIC = os.environ['EVENTSTREAMS_ENHANCED_TOPIC']

PUBLISH_KAFKA_COMMAND = ' kafkacat -P -b ' + EVENTSTREAMS_BROKER_URLS + ' -X api.version.request=true -X security.protocol=sasl_ssl -X sasl.mechanisms=PLAIN -X sasl.username=token -X sasl.password="' + EVENTSTREAMS_API_KEY + '" -t ' + EVENTSTREAMS_ENHANCED_TOPIC + ' '

server = Flask(__name__)

def generate_stream_MJEPG_XXX():
    global g_stream_frame, g_lock

    g_stream_frame = None
    
    count = 1
    while True:
        if g_stream_frame is None:
            time.sleep(0.1)            
            return
        else:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + g_stream_frame + b'\r\n')

def generate_stream_MJEPG():
    global g_stream_frame, g_lock

    g_stream_frame = None
    
    count = 1 
    while True:
        if g_stream_frame is None:
            IMAGE_NAME = 'test-image-' + str(count) + '.jpg'
            image_path = os.path.join('/static', IMAGE_NAME)

            if (count > 4):
                count = 1

            print (image_path)
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
    global g_stream_frame
    if request.headers['Content-Type'] == 'application/json':
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

if __name__ == '__main__':
    server.run(debug=False, host='0.0.0.0')
