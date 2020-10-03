from jsonlogging import *
import ast  
import logging
import time 
import json  
import collections 
import sys
import wave
import os 
import boto3
import requests  
import base64 
from datetime import datetime
import threading
import queue
from eventlog import CustomJsonFormatter
from measure import measure 

output_handler = logging.StreamHandler(sys.stdout)
formatter = CustomJsonFormatter('(time) (severity) (message) (filename) (lineno)')
output_handler.setFormatter(formatter)
LOG = logging.getLogger()
LOG.addHandler(output_handler)
LOG.setLevel(logging.INFO)
LOG.propagate = False 

SQS_QUEUE_URL_PREFIX = os.getenv("SQS_QUEUE_URL_PREFIX","https://sqs.us-west-1.amazonaws.com/700188841304/")
SQS_QUEUE_NAME = os.getenv("SQS_QUEUE_NAME","coldword-cstage-test1")
SQS_QUEUE_URL = "%s%s"%(SQS_QUEUE_URL_PREFIX,SQS_QUEUE_NAME)
FROM_QUEUE_NAME = os.getenv("FROM_QUEUE_NAME", "coldword-cstage-uswest2-0-dead-letter")
FROM_SQS_QUEUE_URL = "%s%s"%(SQS_QUEUE_URL_PREFIX,FROM_QUEUE_NAME)
REGION = os.getenv("REGION", "us-west-1") 
aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
   
class SQSReplayer(threading.Thread):
     
    def __init__(self, name, queue=None): 
        super().__init__(group=None, name=name)
        self.__name__ = name
        self.__sqs__ = boto3.client(
            'sqs',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID','AKIA2GBUB2VMJKRG4JLA'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY','kJvmKXDmZK1h49PQOCtxppMCj0rggIoTeBo9XvD0'),
            region_name=REGION)
        
    def getMessage(self):
       
        # sample message
        # {"Records":
        #   [{"meetingId":"01012ff3-203f-45d1-bc7e-838f1e49b054",
        #    "fileName":"offline_audio_upload.flac",
        #    "s3":{"bucket":{"name":"webex-ai-meeting-assets-cstage-uswest2-0"},
        #      "object":{"key":"7e/ca/ac/7ecaac13-bffa-4962-9014-7191296c8a0f/audio/offline_audio_upload.flac"}}}]}
        # # s3://webex-ai-meeting-assets-cstage-uswest2-0/a3/d5/fc/a3d5fce4-46a0-4f1d-a6f8-28d284c4790f/audio/offline_audio_upload.flac
       
       
        try:
            # LOG.info("receive message from %s as user %s" % (SQS_QUEUE_URL, aws_access_key_id) ) 
            response = self.__sqs__.receive_message(
                QueueUrl=FROM_SQS_QUEUE_URL,
                AttributeNames=[ 'All' ],
                MessageAttributeNames=[ "filename" ],
                MaxNumberOfMessages=1,
                # VisibilityTimeout=1800,
                # WaitTimeSeconds=2,
                # ReceiveRequestAttemptId="1"
            )
            message = response['Messages'][0]
            body = message["Body"]
            LOG.info({"message":"message received %s" % body})
            receipt_handle = message['ReceiptHandle']
            success = self.post_message(body)
            if success:
                # Delete received message from queue
                # LOG.info("start delete message")
                self.__sqs__.delete_message(
                    QueueUrl=FROM_SQS_QUEUE_URL,
                    ReceiptHandle=receipt_handle
                )
                LOG.info({"message":'Received and deleted message'} )
                
        except Exception as ex:
            LOG.info({"message": "no message recevied "})
             
    
    # @measure
    def post_message(self, body):  
        try:
            success = False
            response = self.__sqs__.send_message(
                QueueUrl=SQS_QUEUE_URL,
                MessageBody=body,
                DelaySeconds=1,
                MessageAttributes={
                },
            )
            # meetingId = record["Records"][0]["meetingId"]
            success = True
            print ("posted:", response["MessageId"])           
        except Exception as ex:
            LOG.error({"message":"Exception when process message %s" % str(ex)})
            success = False
        return success
    
    
    
def main(args):
    if len(args) == 2:
        sys.stderr.write(
            'Usage: example.py <aggressiveness> <path to wav file>\n')
        # sys.exit(1)
        meetingId = args[1]
    else:
        meetingId = "oau"
    
    replayer = SQSReplayer(queue.Queue())
    
    while True:
        replayer.getMessage()
        time.sleep(5)    
    
    
if __name__ == '__main__':
    main(sys.argv[1:])