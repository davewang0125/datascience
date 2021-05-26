from google.cloud import vision
import os
import io
import cv2
import numpy as np
from PIL import Image
from google.cloud import vision
from google.cloud import storage
import time 
from argparse import ArgumentParser
# from google.cloud.vision import types 
from google.oauth2 import service_account
from compare_image import imagecompare 
from speechhints import clean_speech_hint_list,filter_common_words
from audioProcessor import * 
parser = ArgumentParser(description='gvision Client')
parser.add_argument('--video', type=str, default="demo3.mp4")

SIMILARITY_THRESHOLD = 0.05
credentials = service_account.Credentials.from_service_account_file("/Users/dengshan/myGoogleCredential.json")
# client = language.LanguageServiceClient(credentials=credentials)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/Users/dengshan/myGoogleCredential.json"
# export GOOGLE_APPLICATION_CREDENTIALS="/Users/dengshan/myGoogleCredential.json"
client_options = {'api_endpoint': 'vision.googleapis.com'}
client = vision.ImageAnnotatorClient(client_options=client_options)
def detect_text(path):
    """Detects text in the file."""
    result = []
    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    # print('Texts:')
    for text in texts:
        # print('\n"{}"'.format(text.description))
        result.append(text.description)
        
        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])

        # print('bounds: {}'.format(','.join(vertices)))
    return result
    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

def process_video_stream():
    cap = cv2.VideoCapture(0)
    return process_videostream(cap)
    
def process_video_file(videoFile):
        cap = cv2.VideoCapture(videoFile)
        nFrames  = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        # cv2.SetCaptureProperty(cap, cv2.cv.CV_CAP_PROP_POS_AVI_RATIO, 1)
        #total 1059 frame, fps = 25. 30
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        fps1 = nFrames / 30;
        
        # cap = cv2.VideoCapture("https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-mp4-file.mp4")
        #cap = cv2.VideoCapture("/Users/dengshan/git/scripts/python/VideoOcr/zoom_0.mp4")
        # cap = cv2.VideoCapture("/Users/dengshan/Downloads/helm-brownbag1.mp4")
        # cap = cv2.VideoCapture("/Users/dengshan/Downloads/HOw to start a presentation.mp4")
        return process_videostream(cap)

def process_audiostream(videoFile):
        s = getAudioStream(videoFile)
        
def get_speechhints_from_video(videofile):
        speechhints = []
        results = process_video_file(videofile)
        for result in results:
            (_, sh) = result
            for x in sh: 
                speechhints.append(x) 
        print("processed video file and got speech hints:\n", speechhints)
        return speechhints
    
def process_videostream(cap):
        i = 0
        frameRate = 100
        framecnt = 0
        ret = True
        imc = imagecompare()
        while(ret):
            # Capture frame-by-frame
            ret, frame = cap.read()
            framecnt = framecnt + 1
            # if frame:
                #  break 
            if i % frameRate == 0: 
                file = 'live' + str(i) + '.png'
                cv2.imwrite( file,frame)
                if i > 100:
                    pfile = 'live' + str(i-frameRate) + '.png'
                    (nnorm, znorm) = imc.compare_image_files(file, pfile)
                    # print (pfile, file, nnorm, znorm)
                    if nnorm > SIMILARITY_THRESHOLD and znorm > SIMILARITY_THRESHOLD:
                        wordlist = (detect_text(file)) 
                        # print (wordlist)
                        cleaned = clean_speech_hint_list(wordlist)
                        speechhints = filter_common_words(cleaned)
                        # print("frame:", framecnt, "i=", i, "cleaned=====", cleaned, "====", speechhints)
                        yield (framecnt, speechhints)
            i = i + 1    
            # Display the resulting frame
            # cv2.imshow('frame',frame)

        if not cap.isOpened():
            print ("File Cannot be Opened")

        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()

def main():
        videofile = args.video
        speechhints = get_speechhints_from_video(videofile)
        print("speech hints:", speechhints)
        audio = getAudioStream_fromVideo(videofile)
        print ("generated a wav file ready for transcribe: %s.wav" % videofile.strip())
         
if __name__ == '__main__':
    main()
