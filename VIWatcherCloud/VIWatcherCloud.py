import time
import sys
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from configparser import SafeConfigParser
import re
from os import path
import requests
import json
import cv2
import platform
import os
import numpy as np

# Name of config file
default_config = 'VIWatcherCloud.config'

# Palette used by detection annotation
color_palette = [
    (255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255),
    (128,0,0), (0,128,0), (0,0,128), (128,128,0), (128,0,128), (0,128,128),
    (64,0,0), (0,64,0), (0,0,64), (64,64,0), (64,0,64), (0,64,64),
    (192,0,0), (0,192,0), (0,0,192), (192,192,0), (192,0,192), (0,192,192)
    ]

# Parse edge scoring response object (classification)
def parseResponse(text):

    # Set best detection and confidence
    best_det = None
    best_conf = 0.0

    try:
        # Parse the response
        parsed = json.loads(text)

        # Iterate through the detections, finding the one with the highest confidence
        dets = parsed['detections']
        if dets != None:
            if len(dets) == 1:
                prob_types = dets[0]['probableTypes']
                for det in prob_types:
                    det_type = det['type']
                    det_conf = float(det['confidence'])
                    if det_conf > best_conf:
                        best_det = det_type
                        best_conf = det_conf

    except ValueError:  # includes simplejson.decoder.JSONDecodeError
        # If text can't be parsed then print text to console
        print("Response Error: {}", text)

    return (best_det, best_conf)

# Parse the response from the OD model
def parseODResponse(text):

    dets = None
    try:
        # Parse and return the detections object
        parsed = json.loads(text)
        dets = parsed['detections']

    except ValueError:  # includes simplejson.decoder.JSONDecodeError
        # If text can't be parsed then print text to console
        print("Response Error: {}", text)

    return dets

SCALE_SIZE = 480
TEXT_COLOR = (0, 255, 0)
OD_LABELS = True

def drawText(img, text, x, y, scale, color, thickness):
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)

# Draws the text in the window
def showText(img, text, xpct, ypct, color):

    height = np.size(img, 0)
    width = np.size(img, 1)
    x = int(width * xpct)
    y = int(height * ypct)
    scale = max(1, int(height / SCALE_SIZE))
    thickness = min(max(2, int(height / SCALE_SIZE) * 2), 10)
    drawText(img, text, x, y, scale, color, thickness)

def showDuration(frame, duration):
    if duration > 0.0:
        showText(frame, "{:.2f}s".format(duration), 0.80, 0.95, TEXT_COLOR)

# Draws the classification result
def showClass(frame, det, conf):
    showText(frame, "{} ({:2.1f}%)".format(det, conf), 0.01, 0.06, TEXT_COLOR)

# Draws a detection rectangle
def drawRect(img, xmin, ymin, xmax, ymax, color, conf):
    thickness = int((conf / 100) * 4) + 1
    height = np.size(img, 0)
    thick = thickness * max(1, int(height / SCALE_SIZE))
    cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, thick)
    if OD_LABELS:
        scale = max(1, int(height / SCALE_SIZE))
        thickness = min(max(1, int(height / SCALE_SIZE) -1), 8)
        drawText(img, "{:2d}%".format(int(conf)), xmax + 5, ymax, scale, color, thickness)


# Draws a line for the key
def drawKeyLine(img, ypct, widthpct, color):
    height = np.size(img, 0)
    width = np.size(img, 1)
    y = int(height * (ypct - 0.01))
    xmin = int(width * 0.01)
    xmax = int(width * (widthpct - 0.01))
    thick = 4 * max(1, int(height / SCALE_SIZE))
    cv2.line(img, (xmin, y), (xmax, y), color, thick)

# globals
max_color_num = 0
colors = {}
max_pos = 0.05
positions = {}

def getColor(det):
    global max_color_num, colors
    if det in colors:
        return colors[det]
    else:
        color = color_palette[max_color_num]
        colors[det] = color
        max_color_num += 1
        return color

def getPosition(det):
    global max_pos, positions
    if det in positions:
        return positions[det]
    else:
        pos = max_pos
        positions[det] = pos
        max_pos += 0.05
        return pos


# Shows the detections
def showDets(frame, cropped_frame, dets):
    global colors

    for d in dets:
        # Get det and confidence
        probableTypes = d['probableTypes']
        det = probableTypes[0]['type']
        conf = probableTypes[0]['confidence']

        if det != '':
            # get positions
            position = d['position']
            x = position['x']
            y = position['y']
            w = position['width']
            h = position['height']

            color = getColor(det)

            # Draw the detection rectangle
            drawRect(cropped_frame, x, y, x+w, y+h, color, conf)

    # Draw the keys
    for det, color in colors.items():
        y = getPosition(det)
        drawKeyLine(frame, y, 0.05, color)
        showText(frame, "{}".format(det), 0.05, y, color)

def cloud_score_image(image_path, config, score_type):

    # Pick up options
    url = config['Cloud']['URL']
    cell = config['Cloud']['Cell']
    product = config['Cloud']['Product']

    # Open file and load into content
    data = open(image_path, 'rb').read()

    # Request parameters
    params = {'productType': product, 'cell': cell,
        'user': os.environ['VIUSER'],
        'solution': 'vi'}

    # Request headers
    headers = {'user': os.environ['VIUSER'], 'APIKey':os.environ['VIAPIKEY'], 'Content-Type': 'application/binary' }

    # score against the Cloud Scoring API
    try:
        r = requests.post(url, params=params, headers=headers, data=data)
    except requests.exceptions.RequestException as e:
        print(e)

    return r

def displayImage(image_path):

    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is not None:
        cv2.imshow("score", img)

    return img

def updateImage(img, det, conf, dets, duration):

    # Show the class or draw the detections on the snapshot
    if det:
        showClass(img, det, conf)
    if dets:
        showDets(img, img, dets)

    showDuration(img, duration)

    cv2.imshow("score", img)

class WatcherHandler(PatternMatchingEventHandler):

    # def __init__(self, patterns=None, ignore_patterns=None,
    #              ignore_directories=False, case_sensitive=False,
    #              config):
    #     super(ChocoHandler, self).__init__(patterns, ignore_patterns, ignore_directories, case_sensitive)

    def score(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        # the file will be processed there
        img = displayImage(event.src_path)

        # Need to test for None as dropped images aren't always readable
        if img is not None:

            score_type = config['Cloud']['ModelType']

            score_time = time.clock()
            r = cloud_score_image(event.src_path, config, score_type)
            duration = time.clock() - score_time

            if r.status_code == 200:

                dets = None
                det = None
                conf = None

                if score_type == 'cls':
                    # Get det and conf from classifier
                    (det, conf) = parseResponse(r.text)
                else:
                    # Get dets from OD response
                    dets = parseODResponse(r.text)

                updateImage(img, det, conf, dets, duration)

            else:
                # Score failed
                print("{}: {}".format(r.status_code, r.text))

    def log(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        # the file will be processed there
        print("{}: {}".format(event.src_path, event.event_type))  # print now only for degug

    def match(self, event):
        regex = config['Images']['Regex']
        match = False
        if regex == '':
            match = True
        else:
            match = re.match(config['Images']['Regex'], path.basename(event.src_path))
        return match

    def on_modified(self, event):
        self.log(event)

        match = self.match(event)

        # On Windows, score on modified event
        if match and platform.system() == "Windows":
            # print('Matches pattern!')
            self.score(event)

    def on_created(self, event):
        self.log(event)

        match = self.match(event)

        # Other platforms, score on created event
        if match and platform.system() != "Windows":
            self.score(event)

if __name__ == '__main__':
    args = sys.argv[1:]

    # Parse config file
    config = SafeConfigParser()
    config_path = args[0] if args else default_config
    config.read(config_path)

    handler = WatcherHandler(patterns=[ config['Images']['WildcardPattern'] ])

    observer = Observer()
    observer.schedule(handler, path=config['Images']['Directory'])
    observer.start()

    # Create the score window if it doesn't exist
    cv2.namedWindow("score", cv2.WINDOW_NORMAL)

    try:
        while True:

            # Get keyboard input
            k = cv2.waitKey(1)
            action = False

            if k%256 == 27:
                # ESC pressed - break from loop
                print("Escape hit, closing...")
                observer.stop()
                break

    except KeyboardInterrupt:
        observer.stop()

    observer.join()
    cv2.destroyAllWindows()
