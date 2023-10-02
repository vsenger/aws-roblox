import argparse
import os
import subprocess
import sys
from contextlib import closing
from tempfile import gettempdir

import boto3
import cv2
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from playsound import playsound
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json
#abobrinha paermsao gorg azeitona, brocolis com queijo e alho, calabresa e dois kibes
# Define ENDPOINT, CLIENT_ID, PATH_TO_CERT, PATH_TO_KEY, PATH_TO_ROOT, MESSAGE, TOPIC, and RANGE
ENDPOINT = "a2p4fyajwx9lux-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "testDevice"
PATH_TO_CERT = "/Users/vsenger/minecraft-iot/8f2b2f776911332a0fea819064421830e592b55f32c4a6262918700841fc5c32-certificate.pem.crt"
PATH_TO_KEY = "/Users/vsenger/minecraft-iot/8f2b2f776911332a0fea819064421830e592b55f32c4a6262918700841fc5c32-private.pem.key"
PATH_TO_ROOT = "/Users/vsenger/minecraft-iot/AmazonRootCA1.pem"
MESSAGE = "Hello World"
TOPIC = "test/testing"
RANGE = 20
print("passando")
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=ENDPOINT,
            cert_filepath=PATH_TO_CERT,
            pri_key_filepath=PATH_TO_KEY,
            client_bootstrap=client_bootstrap,
            ca_filepath=PATH_TO_ROOT,
            client_id=CLIENT_ID,
            clean_session=False,
            keep_alive_secs=6
            )
print("Connecting to {} with client ID '{}'...".format(
        ENDPOINT, CLIENT_ID))
# Make the connect() call
connect_future = mqtt_connection.connect()
# Future.result() waits until a result is available
connect_future.result()
print("Connected!")

def teste():
    print("teste")

def publish_iot(topic1, message1):
    print('Begin Publish ' + topic1)
    mqtt_connection.publish(topic=topic1, payload=message1, qos=mqtt.QoS.AT_LEAST_ONCE)
    print('Publish End')
    #disconnect_future = mqtt_connection.disconnect()
    #disconnect_future.result()
    #json.dumps(message1)
def detect_labels(client, image_blob):
    return client.detect_labels(
        Image={'Bytes': image_blob})


def label_is_present_confidence(labels, label):
    for l in labels:
        if l['Name'] == label:
            return l['Confidence']
    return 0

def label_is_present(labels, label):
    for l in labels:
        if l['Name'] == label:
            return True
    return False


def generate_audio(text, fileName):
    if (not os.path.isfile(fileName)):
    #chamada da poli para gerar o arq. mp3
        client = boto3.client('polly')
        response = client.synthesize_speech(
            OutputFormat='mp3',
            TextType='text',
            VoiceId='Vitoria',
            LanguageCode='pt-BR',
            Text=text
        )
        file = open(fileName, 'wb')
        file.write(response['AudioStream'].read())
        file.close()
    playsound(fileName)


def resize_bbox(img, bbox):
    return {
        'Left': int(bbox['Left'] * img.shape[1]),
        'Top': int(bbox['Top'] * img.shape[0]),
        'Height': int(bbox['Height'] * img.shape[0]),
        'Width': int(bbox['Width'] * img.shape[1])
    }


def draw_bounding_box(img, bbox, color=(255, 0, 0)):
    pt1 = (bbox['Left'], bbox['Top'])
    pt2 = (bbox['Left'] + bbox['Width'], bbox['Top'] + bbox['Height'])
    cv2.rectangle(img, pt1, pt2, color, thickness=2)


def draw_text(img, bbox, text,
              bg_color=(255, 0, 0), text_color=(255, 255, 255)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    thickness = 2
    size = cv2.getTextSize(text, font, font_scale, thickness)[0]

    x, y = (bbox['Left'], bbox['Top'])
    cv2.rectangle(img, (x, y-size[1]), (x+size[0], y), bg_color, cv2.FILLED)
    cv2.putText(img, text, (x, y), font, font_scale, text_color, thickness)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            'Without any arguments, it will highlight all labels that have a '
            'bounding box.\n\nWith the argument -l, it will highlight only '
            'the informed labels (quotes are\nneeded for labels made up with '
            'two or more words).\n'
            'Ex: %(prog)s -l Person "Mobile Phone" Glasses'))
    parser.add_argument('-l', dest='labels', nargs='+', help=(
        'labels to highlight (separated by whitespace)'))
    args = parser.parse_args()
    teste()
    if args.labels:
        interested = args.labels
        print(f'Highlighting: {interested}')
    else:
        interested = None
        print('Highlighting all labels that have a bounding box')

    client = boto3.client('rekognition')
    cap = cv2.VideoCapture(0)

    frame_skip = 5
    frame_count = 0
    mask = False

    protegido = False
    hat = False
    glasses = False
    doctor = False
    while True:
        # Grab a single frame of video
        ret, frame = cap.read()
        if not ret:
            raise RuntimeError('Failed to capture frame')

        if frame_count % frame_skip == 0:  # only analyze every n frames
            print(f'frame: {frame_count}')

            # Resize frame to 1/2 for faster processing
            small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

            # Encode to JPG and send to rekognition
            ret, encoded = cv2.imencode('.jpg', small)
            if not ret:
                raise RuntimeError('Failed to encode frame')
            response = detect_labels(client, encoded.tostring())
            #print(response)
            labels = response['Labels']

            print(labels)

            #print(labels[0]['Confidence'])
            #confidence = response['Confidence']
            if(label_is_present(labels, 'Person') and label_is_present(labels, 'Doctor')):
                if not doctor:
                    cf = label_is_present_confidence(labels, 'Doctor')
                    print("doctor")
                    print(cf)
                    if(cf>65):
                        publish_iot('control/lamp','0')
                        generate_audio('Máscara detectada, pode entrar no evento!', 'mascara.mp3')
                        doctor=True
                        
            elif(label_is_present(labels, 'Person') and doctor):
                doctor=False
                publish_iot('control/lamp','1')
                generate_audio('Você está sem máscara, acesso não liberado ao evento!', 'tiroumascara.mp3')

            if(label_is_present(labels, 'Person') and label_is_present(labels, 'Hat')):
                if not hat:
                    cf = label_is_present_confidence(labels, 'Hat')
                    print("hat")
                    print(cf)
                    if(cf>90):
                        publish_iot('control/lamp','0')
                        generate_audio('Chapéu detectado!', 'hat.mp3')
                        hat=True
                        
            elif(label_is_present(labels, 'Person') and hat):
                hat=False
                publish_iot('control/lamp','1')
                generate_audio('Você tirou o chapéu', 'tirouchapeu.mp3')
                print('Você tirou o chapéu')

            if (label_is_present(labels, 'Person') and label_is_present(labels, 'Helmet')):
                if not protegido and label_is_present_confidence(labels, 'Helmet')>90:
                    generate_audio('Você está protegido', 'safe.mp3')
                    protegido = True
                    message = {"helmet" : "1"}
                    publish_iot('gaming/sensor/aicamera',message)
                    print('Você está protegido')

            elif (label_is_present(labels, 'Person') and protegido):
                protegido = False
                generate_audio('Você está desprotegido', 'unsafe.mp3')
                print('Você está desprotegido')

                message = {"helmet" : "0"}
                publish_iot('gaming/sensor/aicamera',message)
                
                print(protegido)

            # Iterate over detected labels
            label_height = 30
            for label in response['Labels']:
                if interested is None or label['Name'] in interested:
                    for instance in label['Instances']:
                        color = (20, 200, 240)
                        bbox = resize_bbox(frame, instance['BoundingBox'])

                        # Annotate labels with bounding boxes
                        text = label['Name']
                        draw_bounding_box(frame, bbox, color)
                        draw_text(frame, bbox, text, color)

            cv2.imshow("Press 'Q' to quit", frame)

        frame_count += 1

        # Hit 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
