#!/usr/local/bin/python3
import itertools
import logging
import grpc
import speech_pb2
import speech_pb2_grpc
import os
import io
import wave
import pyaudio
import uuid
from argparse import ArgumentParser
from six.moves import queue
from webex_ci_sso import sso_access
import datetime
from datetime import datetime, timedelta
import time
from gvision import get_speechhints_from_video 

parser = ArgumentParser(description='Audio Client')
parser.add_argument('--speech_hints', type=str, default="")
parser.add_argument('--language_code', type=str, default="en-US")
parser.add_argument('--sample_rate', type=int, default=16000)
parser.add_argument('--encoding', type=str, default="LPCM")
parser.add_argument('--enable_automatic_punctuation', type=bool, default=False)
parser.add_argument('--enable_training', type=bool, default=False)
parser.add_argument('--file', type=str, default="")
parser.add_argument('--streaming', type=bool, default=False)
parser.add_argument('--longrunning', type=bool, default=False)
parser.add_argument('--url', type=str, default="")
parser.add_argument('--callback_url', type=str, default="")
parser.add_argument('--engine', type=str, default="nutcracker") 
parser.add_argument('--video', type=str, default="demo3.mp4")

args = parser.parse_args()

def _load_credential_from_file(filepath):
    real_path = os.path.join(os.path.dirname(__file__), filepath)
    with open(real_path, 'rb') as f:
        return f.read()


_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.INFO)

# _SERVER_ADDR_TEMPLATE = '127.0.0.1:8080'
_SERVER_ADDR_TEMPLATE ="asr-proxy.uswest2-0.cstage.vcra.co:443"
# _SERVER_ADDR_TEMPLATE ="asr-proxy.uscentral1-0.cint.vcra.co:443"
#_SERVER_ADDR_TEMPLATE ="asr-proxy.uswest1-0.cprod.vcra.co:443"


#ci related:
USER_ID=os.getenv("CI_USER_ID","voicea-asr-sample-client-bts")
USER_PASSWD=os.getenv("CI_USER_PASSWD", "CULP.tfio.12.GKMN.rskl.06.AQRF.qbsv.3457") 
USER_REALM=os.getenv("CI_ORG_ID","a93dde14-65b7-4a59-81dd-28962a8473e3")
BROKER_HOST=os.getenv("BORKER_HOST", "idbrokerbts.webex.com")
CLIENT_ID=os.getenv("CI_CLIENT_ID", "C6ac166d70e8ea8a59e0a341c7690ddc0e3de836bc1c702d31c211501358b594b")
CLIENT_SECRET=os.getenv("CI_CLIENT_SECRET", "19d82f38891800bcd9bc636d986b6a0d037ec0fc7aae72161e60c7eb0c67e930")
SCOPE=os.getenv("CI_SCOPE", "Identity:SCIM Identity:Organization Identity:Config webex-voice-assistant:meetings")
__ci_token__ = "" 
__token_expire__ = None
__sso__ = sso_access(orgId=USER_REALM, machineAccount=USER_ID, machineAccountPW=USER_PASSWD, oauth_host=BROKER_HOST)
 
class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)


class FileStream(object):
    def __init__(self, file_name, rate, chunk_size):
        self.file_name = file_name
        self.rate = rate
        self.chunk_size = chunk_size
        self.file = open(self.file_name, 'rb')

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.file.close()

    def generator(self):
        chunks = chunk_array(self.file.read(), self.chunk_size)
        for chunk in chunks:
            yield chunk


def make_channel():
    """Creates a secure channel with auth credentials from the environment."""
    # Grab application default credentials from the environment
    creds = grpc.ssl_channel_credentials()
    #options = (('grpc.ssl_target_name_override', 'nutcracker.grpc.staging.vcra.co',),)
    #secure
    return grpc.secure_channel(_SERVER_ADDR_TEMPLATE, creds)
    #non-secure
    # return grpc.insecure_channel(_SERVER_ADDR_TEMPLATE)


def getAccessToken():
    global __ci_token__
    global __token_expire__
    if 1==1:
        if __ci_token__ == "" or \
           (__token_expire__ - datetime.utcnow()).total_seconds() < 5:
            __ci_token__, __token_expire__ = __sso__.getAccessToken(CLIENT_ID, CLIENT_SECRET, scope=SCOPE)
        
        print ("token", __ci_token__)
        return __ci_token__
    return None

def chunk_array(arr, length):
    return [arr[0+i:length+i] for i in range(0, len(arr), length)]


def recognize(stub, fname):
    with open(fname, 'rb') as f:
        data = f.read()
    trackingId = 'asr_client_python_'+str(uuid.uuid4())
    print("Tracking ID will be "+ str(trackingId))
    RATE = args.sample_rate
    metadata = (('authorization', 'Bearer ' + getAccessToken()),
                    ('trackingid', str(trackingId)), 
                    ('engine', args.engine))
    request_config = speech_pb2.RecognitionConfig(sample_rate_hertz=RATE,max_alternatives=1)
    request_config.enable_automatic_punctuation = args.enable_automatic_punctuation
    request_config.enable_training = args.enable_training        
    print(request_config)
    request_audio = speech_pb2.RecognitionAudio(content=data)
    recognize_request = speech_pb2.RecognizeRequest(config=request_config,
                                                    audio=request_audio)
    response = stub.Recognize(recognize_request, metadata=metadata)

    alignments = []
    print(response.results)
    if len(response.results) > 0:
        t = response.results[0].alternatives[0].transcript
        return t
    return ""

def longRunningRecognize(stub, url, fileName, callbackUrl):
    trackingId = 'asr_client_python_'+str(uuid.uuid4())
    print("Tracking ID will be "+ str(trackingId))
    if fileName: #not supported yet
        with open(fileName, 'rb') as f:
            data = f.read()
        RATE = args.sample_rate
        metadata = (('authorization', 'Bearer ' + getAccessToken()),
                         ('trackingid', str(trackingId)))
        request_config = speech_pb2.RecognitionConfig(sample_rate_hertz=RATE,max_alternatives=1)
        request_config.enable_automatic_punctuation = args.enable_automatic_punctuation
        request_config.enable_training = args.enable_training        
        print(request_config)
        request_audio = speech_pb2.RecognitionAudio(content=data)
        
        recognize_request = speech_pb2.LongRunningRecognizeRequest(config=request_config,
                                                        audio=request_audio, 
                                                        callback_url=callbackUrl)
        
    else:
        RATE = args.sample_rate
        metadata = (('authorization', 'Bearer ' + getAccessToken()),
                         ('trackingid', str(trackingId))) 
        request_config = speech_pb2.RecognitionConfig(sample_rate_hertz=RATE,max_alternatives=1)
        request_config.enable_automatic_punctuation = args.enable_automatic_punctuation
        request_config.enable_training = args.enable_training        
        request_audio = speech_pb2.RecognitionAudio(uri=url)
        recognize_request = speech_pb2.LongRunningRecognizeRequest(config=request_config,
                                                        audio=request_audio,
                                                        callback_url=callbackUrl)
        print(recognize_request)
            
        #in case it is url, we can post a message directly for sharder to pickup on server side
    response = stub.LongRunningRecognize(recognize_request, metadata=metadata)
    if len(response.name) > 0:
        print("Job Id is "+ str(response.name))
        return response.name
    return ""

def getLongRunningRecognizeOperation(stub, meetingId):
    try:
        trackingId = 'asr_client_python_'+str(uuid.uuid4())
        metadata = (('authorization', 'Bearer ' + getAccessToken()),
                            ('trackingid', str(trackingId))) 
        operationRequest = speech_pb2.LongRunningRecognizeOperationRequest(name=meetingId)
        operation = stub.GetLongRunningRecognizeOperation(operationRequest, metadata=metadata)
        if operation.done:
            transcripts = "".join(alt.transcript for alt in operation.response.results[0].alternatives)
            # t = "".join(tx for tx in transcripts)
            print ( "transcripts: %s" % transcripts)
            return (True, transcripts)
        else:
            print("Transcript is not ready yet, current progress: %i" % operation.metadata.progress_percent)
            return (False, None)
    except Exception as ex:
        print("failed ex %s" % ex)
        

def deleteLongRunningRecognizeOperation(stub, meetingId):
    try:
        trackingId = 'asr_client_python_'+str(uuid.uuid4())
        metadata = (('authorization', 'Bearer ' + getAccessToken()),
                            ('trackingid', str(trackingId))) 
        operationRequest = speech_pb2.LongRunningRecognizeOperationRequest(name=meetingId)
        stub.DeleteLongRunningRecognizeOperation(operationRequest, metadata=metadata)
    except Exception as ex:
        print ("failed to delete the meeting %s" % ex)

def main():
    print(args.speech_hints)
    speech_hints = []
    if args.speech_hints != "":
       speech_hints = args.speech_hints.split(",")

    if args.video != "":
        videofile = args.video
        print ("--video <demo3.mp4 by default>")
        if len(videofile) <=0:
            videofile = "/Users/dengshan/git/scripts/python/VideoOcr/demo3.mp4"
        speechhints = get_speechhints_from_video(videofile)
        
    # In practice, stream should be a generator yielding chunks of audio data.
    stream = []
    RATE = args.sample_rate
    CHUNK = int(RATE / 10)  # 100ms
    channel = make_channel()
    stub = speech_pb2_grpc.SpeechStub(channel)
    s = MicrophoneStream(RATE, CHUNK)
    
    if args.longrunning:
        file = args.file
        url = args.url
        if url == None or len(url)==0:
            #url = "https://www.ee.columbia.edu/~dpwe/sounds/mr/spkr0.wav"
            url = "https://www2.cs.uic.edu/~i101/SoundFiles/preamble.wav"
            
            
        callback = args.callback_url
        meetingId = longRunningRecognize(stub, url=url, fileName=file, callbackUrl=callback)
        done = False
        while not done:
            (done, transcripts) = getLongRunningRecognizeOperation(stub, meetingId)
            time.sleep(5)
        
        print ("final transcripts: %s" % transcripts)
        print ("meeting delete: %s" % meetingId)
        deleteLongRunningRecognizeOperation(stub, meetingId) 

    elif args.file != "":
        s = FileStream(args.file, RATE, CHUNK)
        if not args.streaming:
            return recognize(stub,args.file)
        else:
            stream_recognize(s, speech_hints, RATE, CHUNK, channel, stub)
    elif args.video != "" :
        audiofile = "%s%s" % (args.video.strip(), ".wav")
        if not args.streaming:
            s = FileStream(audiofile, RATE, CHUNK)
            stream_recognize(s, speech_hints, RATE, CHUNK, channel, stub)
        else: #use microphone
            stream_recognize(s, speech_hints, RATE, CHUNK, channel, stub)
    else:
        stream_recognize(s, speech_hints, RATE, CHUNK, channel, stub)

def stream_recognize(s, speech_hints, RATE, CHUNK, channel, stub):
    if s is not None:
        with s as stream:
            audio_generator = stream.generator()
            request_config = speech_pb2.RecognitionConfig(sample_rate_hertz=RATE)
            if len(speech_hints) > 0:
                request_config.speech_contexts.append(speech_pb2.SpeechContext(phrases=speech_hints))
            if args.language_code != "":
                request_config.language_code = args.language_code
            if args.encoding == "MULAW":
                request_config.encoding = speech_pb2.RecognitionConfig.MULAW
            else:
                request_config.encoding = speech_pb2.RecognitionConfig.LINEAR16
            request_config.enable_automatic_punctuation = args.enable_automatic_punctuation
            request_config.enable_training = args.enable_training        
            print(request_config)

            streaming_request_config = speech_pb2.StreamingRecognitionConfig(config=request_config,
                                                                            single_utterance=False,
                                                                            interim_results=False)
            config_request = (speech_pb2.StreamingRecognizeRequest(streaming_config=streaming_request_config) for i in range(1))
            requests = (speech_pb2.StreamingRecognizeRequest(audio_content=chunk) for chunk in audio_generator)
            trackingId = 'asr_client_python_'+str(uuid.uuid4())
            print("Tracking ID will be "+ str(trackingId))
            print("engine:", args.engine)

            metadata = (('authorization', 'Bearer ' + getAccessToken()),
                        ('trackingid', str(trackingId)), 
                        ('engine', args.engine))
            recognize_responses = stub.StreamingRecognize(itertools.chain(config_request, requests), metadata=metadata)
            print(recognize_responses)

            for response in recognize_responses:
                print(response)

if __name__ == '__main__':
    main()

