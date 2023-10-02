import boto3
import cv2
import os
import sys
from contextlib import closing
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
import subprocess
from tempfile import gettempdir


def detect_faces(client, image_blob):
    return client.detect_faces(
        Image={'Bytes': image_blob},
        Attributes=['ALL'])


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
    mixer.music.load('safe.mp3')
    mixer.music.play()

if __name__ == '__main__':
    client = boto3.client('rekognition')
    cap = cv2.VideoCapture(0)

    frame_skip = 10
    frame_count = 0

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
            response = detect_faces(client, encoded.tostring())
            
            # Iterate over detected faces
            for face in response['FaceDetails']:
                age_low = face['AgeRange']['Low']
                age_high = face['AgeRange']['High']
                gender = face['Gender']['Value'][0]

                color = (255, 0, 0) if gender == 'M' else (0, 0, 255)
                bbox = resize_bbox(frame, face['BoundingBox'])

                # Annotate age and gender information
                text = f'{age_low}-{age_high} {gender}'
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
