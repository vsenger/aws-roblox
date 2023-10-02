import os
import sys
import boto3
from pygame import mixer # Load the required library
from contextlib import closing
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
import subprocess
from tempfile import gettempdir

def generate_audio():
    #chamada da poli para gerar o arq. mp3
    client = boto3.client('polly')
    response = client.synthesize_speech(
        OutputFormat='mp3',
        TextType='text',
        VoiceId='Vitoria',
        LanguageCode='pt-BR',
        Text='Você está protegido'
    )

    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            output = os.path.join(gettempdir(),"safe.mp3")

            try:
                # Open a file for writing the output as a binary stream
                with open(output, "wb") as file:
                    file.write(stream.read())
            except IOError as error:
                # Could not write to file, exit gracefully
                print(error)
                sys.exit(-1)

def play_audio():
    mixer.init()
    mixer.music.load('C:/Users/giroln/Desktop/rekognition-webcam-demo/rekognition-webcam-demo/safe.mp3')
    mixer.music.play()


generate_audio()
play_audio()


