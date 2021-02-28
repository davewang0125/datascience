from jsonlogging import *
import ast  
import logging
import time 
import json 
import base64
import collections
import contextlib
import sys
import wave
import os
import webrtcvad
import boto3
import requests
from requests.auth import HTTPBasicAuth 
from pydub import AudioSegment
import base64
from wrapi import wrapi
from ledger import ledger
from sharder import sharder, Frame
from oldSharder import oldSharder
from trainable import trainableService
from datetime import datetime
import threading
import queue
from eventlog import CustomJsonFormatter
from measure import measure
import glob
from multiprocessing import Pool, Process
import flask
import signal
from waitress import serve
import waitress
from flask import Flask, jsonify, request
from flask_api import status
from flask_monitor import Monitor, ObserverLog


output_handler = logging.StreamHandler(sys.stdout)
formatter = CustomJsonFormatter('(time) (severity) (message) (filename) (lineno)')
output_handler.setFormatter(formatter)
LOG = logging.getLogger()
LOG.addHandler(output_handler)
LOG.setLevel(logging.INFO)
LOG.propagate = False 
run_process = True
SQS_QUEUE_URL_PREFIX = os.getenv("SQS_QUEUE_URL_PREFIX","https://sqs.us-west-1.amazonaws.com/700188841304/")
SQS_QUEUE_NAME = os.getenv("SQS_QUEUE_NAME","coldword-cstage-test1")
SQS_QUEUE_URL = "%s%s"%(SQS_QUEUE_URL_PREFIX,SQS_QUEUE_NAME)
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "webex-ai-meeting-assets-cstage-uswest2-0")
REGION = os.getenv("REGION", "us-west-1")
SHARDING_AGGRESSIVENESS = int(os.getenv("SHARDING_AGGRESSIVENESS", "0"))
USE_NEW_SHARDER = os.getenv("USE_NEW_SHARDER", False)
StatusProcessing        = "processing"
StatusRecordingUploaded = "RecordingUploaded" 
StatusCallEnded = "CallEnded"
EventTypeSharderStarted                 = "sharder_started" 
EventTypeSharderRecordingUploaded       = "sharder_recording_uploaded"
AUDIO_FOLDER = os.getenv("AUDIO_FOLDER", "/tmp/")
aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
NUMBER_OF_THREADS = int(os.getenv('NUMBER_OF_THREADS',"1"))
DEFAULT_SAMPLE_RATE = 16000
NUMBER_OF_PROCESSES = int(os.getenv("NUMBER_OF_PROCESSES", 1))   

# multiple process


# def handler_stop_signals(signum, frame):
#     global run_process 
#     run_process = False 
#     LOG.info("SIGTERM received")
#     # server.close()
#     sys.exit(0)
    
def create_app(config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        # SECRET_KEY="dev",
        # store the database in the instance folder
        # DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/hello")
    def hello():
        return "Hello, World!"

    @app.route('/createMeeting', methods=['POST'])
    def createMeeting():
        """ Handl """
        while run_process:
            input_text = request.form.get('url', request.form.get('t'))
            if not input_text:
                DownloadFile(url)
            
            try:
                return jsonify({'result': str(run_process)})
            except Exception as e:
                LOG.error({'message': 'Error running post processor', 'error': e}, exc_info=True)
                return jsonify({'result': str(input_text)})
        else:
            return 'system not ready', status.HTTP_500_INTERNAL_SERVER_ERROR

   

    @app.route('/liveness', methods=['GET'])
    def handle_liveness(): 
        if run_process:
            return 'alive', status.HTTP_200_OK
        else:
            return 'dead', status.HTTP_500_INTERNAL_SERVER_ERROR

    @app.route('/test', methods=['GET'])
    def test(): 
        return 'test success', status.HTTP_200_OK 

    @app.route('/readiness', methods=['GET'])
    def handle_readiness():
        if run_process:
            return 'ready', status.HTTP_200_OK
        else:
            return 'not ready', status.HTTP_500_INTERNAL_SERVER_ERROR

    # apply the blueprints to the app
    # from flaskr import auth, blog

    # app.register_blueprint(auth.bp)
    # app.register_blueprint(blog.bp)

    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule("/", endpoint="index")

    return app
 
# app = create_app()
# API_SERVER_PORT_NUMBER = int(os.environ.get('API_SERVER_PORT_NUMBER', 5005))
# NUMBER_THREADS = int(os.environ.get('NUMBER_THREADS', 2))
# CONNECTION_LIMIT = int(os.environ.get('CONNECTION_LIMIT', 1500))
# BACKLOG = int(os.environ.get('BACKLOG', 2048))
# server = waitress.create_server(app, host='localhost', port=API_SERVER_PORT_NUMBER, threads=NUMBER_THREADS, connection_limit=CONNECTION_LIMIT, backlog=BACKLOG)
