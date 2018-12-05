import requests
from configparser import SafeConfigParser
import random
import glob
import time
import os
import sys
import numpy as np
import json
import csv
from sklearn.metrics import confusion_matrix
import pandas as pd
import urllib3
import re
from os import path
import glob
import requests
import json
import random
import cv2
import numpy as np

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# import pylab as pl
# from scipy import stats

default_config = 'ValidateImagesOD.config'

from sklearn.metrics import confusion_matrix
import pandas as pd


# Palette used by detection annotation
color_palette = [
    (255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255),
    (128,0,0), (0,128,0), (0,0,128), (128,128,0), (128,0,128), (0,128,128),
    (64,0,0), (0,64,0), (0,0,64), (64,64,0), (64,0,64), (0,64,64),
    (192,0,0), (0,192,0), (0,0,192), (192,192,0), (192,0,192), (0,192,192)
    ]

def cm2df(cm, labels):
    df = pd.DataFrame()
    # rows
    for i, row_label in enumerate(labels):
        rowdata={}
        # columns
        for j, col_label in enumerate(labels):
            rowdata[col_label]=cm[i,j]
        df = df.append(pd.DataFrame.from_dict({row_label:rowdata}, orient='index'))
    return df[labels]



def precision_recall_fscore_support_metrics2df(prfs, labels):
    df = pd.DataFrame()
    for p,r,f,s,label in zip(prfs[0], prfs[1], prfs[2], prfs[3], dataset.target_names):
        rowdata={}
        rowdata['precision']=p
        rowdata['recall']=r
        rowdata['f1-score']=f
        rowdata['support']=s
        df = df.append(pd.DataFrame.from_dict({label:rowdata}, orient='index'))
    return df[['precision','recall','f1-score','support']]

# Score image on cloud
def cloud_score_image(image_path, config):

    # Pick up options
    url = config['Score']['URL']
    cell = config['Score']['Cell']
    product = config['Score']['Product']

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
OD_LABELS = False

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
        fps = int(1 / duration)
        score_dur_ms = int(duration * 1000)
        showText(frame, "{:4d} ms, {:4d} FPS".format(score_dur_ms, fps), 0.5, 0.95, TEXT_COLOR)

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

    return frame

# Shows the detections
def writeDets(writer, fname, dets):

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

            writer.writerow({'filename': fname, 'type': det, 'confidence': conf, 'x': x, 'y': y, 'width': w, 'height': h})

# Scores image to edge
def paiv_score_image(image_path, config):

    url = config['Score']['URL']

    # Open file and load into content
    files = {'files': open(image_path, 'rb')}

    # score against the Edge API
    try:
        r = requests.post(url, files=files, verify=False)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    return r

# Parse PAIV classification
def paiv_parse(text):

    det = ''
    try:
        # Parse the response
        parsed = json.loads(text)

        # Iterate through the detections, finding the one with the highest confidence
        cls = parsed['classified']
        if cls != None:
            det = next(iter(cls))
        else:
            print("No classification")

    except ValueError:  # includes simplejson.decoder.JSONDecodeError
        # If text can't be parsed then print text to console
        print("Response Error: {}", text)

    print(det)
    return det


def getFileSet(image_path, image_wildcard):
    return glob.glob(os.path.join(image_path, image_wildcard))

def scoreImages(fileset, duration, url, modelID):

    end_time = time.perf_counter() + duration
    image_count = 0
    sum_dur = 0.0
    min_dur = None
    max_dur = None

    durations = list()

    while (time.perf_counter() < end_time):
        image = random.choice(fileset)
        iter_start = time.perf_counter()
        score_image(image, url, modelID)
        iter_dur = time.perf_counter() - iter_start
        durations.append(iter_dur)

    durs = np.array(durations)
    print(str(stats.describe(durs)))

if __name__ == '__main__':
    args = sys.argv[1:]

    # Parse config file
    config = SafeConfigParser()
    config_path = args[0] if args else default_config
    config.read(config_path)

    input = config['Images']['Directory']
    score_type = config['Score']['Type']

    print(score_type)

    categories = []
    actuals = []
    preds = []
    image_count = 0
    correct = 0
    costs = {}

    with open(config['Results']['Scores'], mode='w', newline='') as csv_file:

        fieldnames = ['filename', 'type', 'confidence', 'x', 'y', 'width', 'height']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        if os.path.isdir(input):
            for f in os.listdir(input):
                fname = os.path.join(input, f)
                if score_type == 'VI':
                    r = cloud_score_image(fname, config)
                    if r.status_code == 200:

                        dets = parseODResponse(r.text)

                        img = cv2.imread(fname)
                        img = showDets(img, img, dets)
                        outfname = os.path.join(config['Results']['OutputDirectory'], f)
                        cv2.imwrite(outfname, img)

                        writeDets(writer, fname, dets)
                else:
                    #TBD
                    print('Scoring not implemented!')

        else:
            print('-o <output> path is not a directory')
            sys.exit(2)
