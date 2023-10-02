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


def detect_labels(client, image_blob):
    return client.detect_labels(
        Image={'Bytes': image_blob})


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
    if args.labels:
        interested = args.labels
        print(f'Highlighting: {interested}')
    else:
        interested = None
        print('Highlighting all labels that have a bounding box')

    client = boto3.client('rekognition')
    cap = cv2.VideoCapture(0)

    frame_skip = 10
    frame_count = 0

    protegido = False

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

            labels = response['Labels']

            if (label_is_present(labels, 'Person') and label_is_present(labels, 'Helmet')):
                if not protegido:
                    generate_audio('Você está protegido', 'safe.mp3')
                    protegido = True
                    print('Você está protegido')

            elif (label_is_present(labels, 'Person') and protegido):
                protegido = False
                generate_audio('Você está desprotegido', 'unsafe.mp3')
                print('Você está desprotegido')
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
