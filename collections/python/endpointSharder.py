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
import re
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

output_handler = logging.StreamHandler()
formatter = CustomJsonFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
output_handler.setFormatter(formatter)
LOG = logging.getLogger()
while len(LOG.handlers) > 0:
    LOG.handlers.pop()
LOG.addHandler(output_handler)
# if (len(LOG.handlers) > 0): # Check here whatever. Or try/except. You get the idea...
#     formatter = logging.Formatter('(time) (severity) (message) (filename) (lineno)')
#     LOG.handlers[0].setFormatter(formatter)
LOG.setLevel(logging.INFO)
LOG.propagate = False 

content2FileType = {"audio/x-wav":"wav", 
                    "audio/x-mp3":"mp3",
                    "audio/x-flac":"flac",
                    "audio/webm":"weba",
                    "audio/x-aac":"aac",
                    "audio/x-aiff": "aif",
                    "audio/x-caf":"caf",
                    "audio/x-matroska":"mka",
                    "audio/x-mpegurl":"m3u",
                    "audio/x-ms-wax":"wax",
                    "audio/x-ms-wma":"wma",
                    "audio/x-pn-realaudio":"ra",
                    "audio/x-pn-realaudio-plugin":"rmp",
                    "audio/xm":"xm",
                    "audio/mpeg":"mp3",
                    "audio/mp4":"m4a",
                    }
SQS_QUEUE_URL_PREFIX = os.getenv("SQS_QUEUE_URL_PREFIX","https://sqs.us-west-1.amazonaws.com/700188841304/")
SQS_QUEUE_NAME = os.getenv("SQS_QUEUE_NAME","coldword-cstage-test1")
SQS_QUEUE_URL = "%s%s"%(SQS_QUEUE_URL_PREFIX,SQS_QUEUE_NAME)
# S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "webex-ai-meeting-assets-cint-uscentral1-0")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "webex-ai-meeting-assets-cstage-uswest2-0")
REGION = os.getenv("REGION", "us-west-1")
SHARDING_AGGRESSIVENESS = int(os.getenv("SHARDING_AGGRESSIVENESS", "0"))
USE_NEW_SHARDER = os.getenv("USE_NEW_SHARDER", False)
StatusProcessing        = "processing"
StatusRecordingUploaded = "RecordingUploaded" 
StatusCallEnded = "CallEnded"
StatusTranscriptReady="TranscriptReady"
EventTypeSharderStarted                 = "sharder_started" 
EventTypeSharderRecordingUploaded       = "sharder_recording_uploaded"
AUDIO_FOLDER = os.getenv("AUDIO_FOLDER", "/tmp/")
aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
NUMBER_OF_THREADS = int(os.getenv('NUMBER_OF_THREADS',"1"))
NUMBER_OF_PROCESSES= int(os.getenv('NUMBER_OF_PROCESSES',"2"))
DEFAULT_SAMPLE_RATE = 16000
   
class endpointSharder(threading.Thread):
     
    def __init__(self, name, queue=None): 
        super().__init__(group=None, name=name)
        self.__name__ = name
        LOG.info({"message":"Initializing endpoint sharder %s on process %s" % (SQS_QUEUE_URL, name) } )
        self.__sqs__ = boto3.client(
            'sqs',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID',''),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY',''),
            region_name=REGION)
        self.__s3__ = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID',''),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY',''),
            region_name=REGION) 
        self.__ledger__ = ledger()
        self.__wrapi__ = wrapi()
        self.__reprocess_queue__ = queue
        self.__oldSharder__ = oldSharder(queue)
        
    def getMessage(self):
       
        # sample message
        # {"Records":
        #   [{"meetingId":"7ec4c3ed-bc50-476a-8ce0-3046500c070f",
        #    "eventSource": "aws:s3",
        #    "fileName":"offline_audio_upload.flac",
        #    "s3":{"bucket":{"name":"webex-ai-meeting-assets-cstage-uswest2-0"},
        #      "object":{"key":"7e/c4/c3/7ec4c3ed-bc50-476a-8ce0-3046500c070f/audio/offline_audio_upload.flac"}}}]}
        # # # s3://webex-ai-meeting-assets-cstage-uswest2-0/a3/d5/fc/a3d5fce4-46a0-4f1d-a6f8-28d284c4790f/audio/offline_audio_upload.flac
        # {"Records":
        #   [{"eventSource": "asr",
        #     "meetingId":"002d6e08-0d03-4d57-95dc-5709f9de320f",
        #     "uri":https://www2.cs.uic.edu/~i101/SoundFiles/preamble.wav"
        #    }]
        # }
        #    "uri":"https://webex-ai-meeting-assets-cstage-uswest2-0.s3-us-west-1.amazonaws.com/00/2d/6e/002d6e08-0d03-4d57-95dc-5709f9de320f/audio/hotword_recording.mp3"
        # "https://salesassets-origin.cisco.com/adaptivemedia/audio?id=65f1a27ded12334016309927f493be2eb66f0eef""
       
        #s3://webex-ai-meeting-assets-cstage-uswest2-0/00/10/3c/00103c3b-aa23-4bda-aa4a-66778515890f/audio/offline_audio_upload.flac
        # # s3://webex-ai-meeting-assets-cstage-uswest2-0/a3/d5/fc/a3d5fce4-46a0-4f1d-a6f8-28d284c4790f/audio/offline_audio_upload.flac
        
        try:
            # LOG.info("receive message from %s as user %s" % (SQS_QUEUE_URL, aws_access_key_id) ) 
            response = self.__sqs__.receive_message(
                QueueUrl=SQS_QUEUE_URL,
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
            success = self.process_message(body)
            if success:
                # Delete received message from queue
                # LOG.info("start delete message")
                self.__sqs__.delete_message(
                    QueueUrl=SQS_QUEUE_URL,
                    ReceiptHandle=receipt_handle
                )
                # LOG.info({"message":'Received and deleted message'} )
             
        except Exception as ex:
            LOG.info({"message": "no message recevied %s"} % str(ex)) 
    
    @measure
    def process_message(self, body):  
        try:
            success = False
            LOG.info({"message": "%s" % body})
            record = json.loads(body)
            if record["Records"][0]["eventSource"] == "aws:s3":
                bucket= record["Records"][0]["s3"]["bucket"]["name"]
                key = record["Records"][0]["s3"]["object"]["key"]  
                meetingId = key.split("/")[3]
                # LOG.info("download file %s %s %s" %(bucket, key, meetingId))
                if not self.downloadFile(bucket, key, meetingId):
                    raise Exception ("Failed to download file from s3, terminate %s" % meetingId)
            else:
                url = record["Records"][0]["uri"] 
                meetingId = record["Records"][0]["meetingid"]
                LOG.info({"message": "meetingId=%s, url=%s" %(meetingId, url)})
                #https://webex-ai-meeting-assets-cstage-uswest2-0.s3-us-west-1.amazonaws.com/00/2d/6e/002d6e08-0d03-4d57-95dc-5709f9de320f/audio/hotword_recording.mp3
                if "amazonaws.com" in url:
                    try:
                        m= re.search(r'https://(.*)?.s3.*?/(.+)$', url)
                        bucket = m.group(1)
                        key = m.group(2)
                        if not self.downloadFile(bucket, key, meetingId):
                            LOG.error({"message": "failed to download from s3 bucket %s, key %s for meeting" % (bucket, key, meetingId)})
                            raise Exception ("Failed to download file from s3, terminate %s" % meetingId)
                    except Exception as ex:
                        #as the second choice, download it as public URL anyway.
                        if not self.downloadFromUrl(url, "", meetingId):
                            LOG.error({"message": "failed to download from AWS as regular %s for meeting %s" %(url, meetingId,)})
                            raise Exception ("Failed to download s3 file from url, terminate %s" % url)
                else:    
                    if not self.downloadFromUrl(url, "", meetingId):
                        LOG.error({"message": "failed to download %s for meeting %s" %(url, meetingId,)})
                        raise Exception ("Failed to download file from url, terminate %s" % url)
            startProcessing = {
                    'event_type': EventTypeSharderStarted,
                    'event': {
                        'created_at': datetime.utcnow().isoformat("T") + "Z",
                    },
                    'status': StatusProcessing ,
                }
            (trainable, ensemble, start_at_utc, source, language, sharder, status) = self.__wrapi__.get_meeting_info(meeting_id=meetingId)
            if status is None or status == StatusTranscriptReady \
                or status == StatusRecordingUploaded: #some other pod has processed this. directly return
                LOG.info({"message": "processed already status=%s" % status, "VOICEA_MEETING_ID": meetingId,})
                return True
            
            self.__ledger__.post_to_ledger(meeting_id=meetingId,sts = startProcessing) 
            sts = self.__oldSharder__.shard(path=AUDIO_FOLDER, meetingId=meetingId, \
                trainable=trainable, ensemble=ensemble, \
                    start_at_utc=start_at_utc, source=source,\
                         language=language, sharder=sharder)
           
            if sts is None: #when we skip the processing.
                return True  
            #do it one more time, to make sure: check before post next status. 
            (trainable, ensemble, start_at_utc, source, language, sharder, status) = self.__wrapi__.get_meeting_info(meeting_id=meetingId)
            if status is None \
                or status == StatusRecordingUploaded: #some other pod has processed this. directly return
                LOG.info({"message": "processed already status=%s" % status, "VOICEA_MEETING_ID": meetingId,})
                return True
            
            self.__ledger__.post_to_ledger(meeting_id=meetingId, sts=sts) 
            success = self.__wrapi__.post_to_wrapi(meeting_id=meetingId, sts=sts) 
            if success:
                self.cleanup(meetingId)
            
        except Exception as ex:
            LOG.error({"message":"Exception when process message %s" % str(ex), "VOICEA_MEETING_ID": meetingId,})
            success = False
        return success
    
    def getFileType(self, contentType):
        try:
            fType =  content2FileType[contentType]
        except Exception as ex:
            fType = "wav"
        return fType
    
    def downloadFromUrl(self, url, token, meetingId):
        success = False
        try:
            waveFile = AUDIO_FOLDER + meetingId + ".wav"
            #only download when not exist already, what is the file format?
            # if not (os.path.isfile(originFile) and os.path.exists(originFile)):
            r = requests.get(url, allow_redirects=True)
            fileType = self.getFileType(r.headers["Content-Type"])
            originFile = AUDIO_FOLDER + meetingId + ".orig." + fileType
            LOG.info({"message":"download file", "VOICEA_MEETING_ID": meetingId, "file": originFile,})
            with open(originFile, 'wb') as data:
                data.write(r.content)
                    
            
            success = self.convertFileFormat(originFile, waveFile)
        except Exception as ex:
            LOG.warn({"message":"failed to download file or convert file: for VOICEA_MEETING_ID %s, exception: %s" % (meetingId, str(ex))})
            
        return success
    
    # @measure
    def downloadFile(self, bucket, key, meetingId):
        success = False
        try:
            fileType = key.split(".")[-1]
            flacFile = AUDIO_FOLDER + meetingId + "." + fileType
            LOG.info({"message":"download file for VOICEA_MEETING_ID: %s file: %s" %(meetingId, flacFile)})
            waveFile = AUDIO_FOLDER + meetingId + ".wav"
            #only download when not exist already
            if not (os.path.isfile(flacFile) and os.path.exists(flacFile)):
               with open(flacFile, 'wb') as data:
                    self.__s3__.download_fileobj(bucket, key, data)
            success = self.convertFileFormat(flacFile, waveFile)
        except Exception as ex:
            LOG.warn({"message":"failed to download file: for VOICEA_MEETING_ID %s, exception: %s" % (meetingId, str(ex))})

        return success
    
    def convertFileFormat(self, originFile, waveFile):
        success = True
        sampleRate = self.getSampleRate(originFile)
        # LOG.info({"message":"Convert file", "wavefile": waveFile, "sampleRate=":sampleRate, "originFile":originFile,} )
        if not (os.path.isfile(waveFile) and sampleRate == DEFAULT_SAMPLE_RATE):
            os.system("sox --clobber %s -r %s -c 1 -b 16 %s " % (originFile, DEFAULT_SAMPLE_RATE, waveFile) )
        if not (os.path.exists(waveFile)):
            success = False
        LOG.info({"message":"Convert file", "wavefile": waveFile, "sampleRate=":sampleRate, "originFile":originFile,"result success": success} )
        
        return success
    
    def getSampleRate(self, fileName):
        try:
            cmd = "sox --i %s | grep 'Sample Rate' " % (fileName)
            sr = os.popen(cmd).read()
            return sr.split(":")[1].strip()
        except  Exception as ex:
            LOG.error({"message":"exception: when run sox"% str(ex)})
            return DEFAULT_SAMPLE_RATE
        
    # @measure
    def cleanup(self, meetingId):
        try:
            # Get a list of all the file paths that ends with .txt from in specified directory
            fileList = glob.glob(AUDIO_FOLDER + meetingId + "*")
            # Iterate over the list of filepaths & remove each file.
            for filePath in fileList:
                try:
                    os.remove(filePath)
                except:
                    LOG.error({"message":"Error while deleting file : %s VOICEA_MEETING_ID %s"% (filePath, meetingId,)})
            # os.remove(meetingId) #remove the whole meeting folder. 
        except Exception as ex:
            LOG.warn({"message": "failed to remove files for VOICEA_MEETING_ID: %s, exception: %s" % (meetingId, str(ex))})


    def run(self):
        while True:
            try:   
                self.getMessage() 
            except:
                # LOG.warn({"message": ": " + (str(ex),) } )
                time.sleep(1)
                pass


def reprocessor(q=None):
    if q is None:
        q = queue.Queue()
    # print ("reprocessor thread started")
    while True:
        item = q.get()
        LOG.info({"message":"current reprocess queue %i" % q.qsize()})
        success = oldSharder.Process_Failed_Shard(item)
        time.sleep(1)
        if success:
            q.task_done()
        else:
            item.setTryNum(item.getTryNum() + 1)
            q.put(item)
        

def runServer(name):
    server =  endpointSharder(name=name, queue=None)
    server.run()

def main(args):
    #thread with reproess queue.
    ####### for debugging ######### 
    # message = '{"Records":[{"eventVersion":"2.1","eventSource":"aws:s3","awsRegion":"us-west-2","eventTime":"2021-05-20T20:14:28.765Z","eventName":"ObjectCreated:CompleteMultipartUpload","userIdentity":{"principalId":"AWS:AIDA2GBUB2VMNX3TIGAYU"},"requestParameters":{"sourceIPAddress":"104.154.184.68"},"responseElements":{"x-amz-request-id":"PQM2ABKYZXXPYYCN","x-amz-id-2":"kZoCCbqWpCy721f5JhmExOu0PKVpfPkprBStaY57n+PkcbLzkb55XOgs8Twa9EFX45K3s6NtHfc0CnVt5/vshN3TT0KWSxKL"},"s3":{"s3SchemaVersion":"1.0","configurationId":"SQS_COLDWORD_PARTNER_OFFLINE_AUDIO_mp3","bucket":{"name":"webex-ai-meeting-assets-cint-uscentral1-0","ownerIdentity":{"principalId":"AEMYPAXFCVUYB"},"arn":"arn:aws:s3:::webex-ai-meeting-assets-cint-uscentral1-0"},"object":{"key":"06/23/b7/0623b73c-3e6f-4a38-81d2-ec4ca87d200f/audio/partner_offline_audio_upload.mp3","size":3112560,"eTag":"1aa0ddb50ce2d2532ca91fb325205008-1","versionId":"fJ_gQSbTJyezh4JIe2ZPkf4wm0Z5a7eA","sequencer":"0060A6C325E52A2AA8"}}}]}'
    # ed = endpointSharder(name="test", queue=None)
    # ed.process_message(message)
    ####### end for debugging #######
    q = queue.Queue()
    threads =[]
    for i in range(NUMBER_OF_THREADS):
        threadName = "thread-%i" % i
        thread = endpointSharder(name =threadName, queue=q)
        thread.start()
        threads.append(thread) 
    # turn-on the reprocessing thread
    reprocessorThread = threading.Thread(target=reprocessor, name="reprocessor", kwargs={'q' : q})
    reprocessorThread.start() 
    # Wait for all threads to complete
    for t in threads:
            t.join() 
    reprocessorThread.join()
    
    # multiple process
    # for i in range(NUMBER_OF_PROCESSES):
    #     Process(target=runServer, args=(i,q)).start()
    
    #multiprocess, with pool
    with Pool(NUMBER_OF_PROCESSES) as pool:
        try:
            pool.map(runServer, range(NUMBER_OF_PROCESSES))
        except Exception as ex:
            print('pool.apply() exception %s ' % str(ex))
        else:
            raise AssertionError('expected ZeroDivisionError')
    

   
if __name__ == '__main__':
    main(sys.argv[1:])




 
