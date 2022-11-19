import os          
import re
import boto3
from uuid import uuid4


class MeetingClient:
    """ meeting client for demonstrate the calling """

    def __init__(self):
        """ initilize a client """
        self.meeting_id = uuid4()
    
    def create_meeting(self):
        """ create a meeting """
        return self.meeting_id
    
    def upload_audio(self, filename):
        """ upload audio file to s3 bucket """
        s3client = boto3.client("s3")
        s3client.upload(filename, "bucket")
        