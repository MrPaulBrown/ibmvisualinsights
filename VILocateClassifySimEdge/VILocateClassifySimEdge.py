import time
import sys
import os
import threading
import _thread
from configparser import SafeConfigParser
import re
from os import path
import glob
import requests
import json
import random
import cv2
import numpy as np
import math
import imutils
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

default_config = 'VILocateClassifySimEdge.config'

# Palette used by detection annotation
color_palette = [
    (255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255),
    (128,0,0), (0,128,0), (0,0,128), (128,128,0), (128,0,128), (0,128,128),
    (64,0,0), (0,64,0), (0,0,64), (64,64,0), (64,0,64), (0,64,64),
    (192,0,0), (0,192,0), (0,0,192), (192,192,0), (192,0,192), (0,192,192)
    ]

# Scores image to edge
def score_image(image_path, config, score_type):

    # Pick up options
    url = config['Edge']['URL']
    if score_type == 'cls':
        modelID = config['Edge']['ModelID']
    else:
        modelID = config['Edge']['ModelID']

    # Json body for request
    json = { 'modelID': modelID, 'imageFile': image_path }

    # score against the Edge API
    try:
        r = requests.post(url, json=json, verify=False)
       # print(r.status_code)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(2)

    return r

# Score image on edge
def edge_score_image(image_path, config, score_type):

    r = None

    # Pick up options
    url = config['Edge']['URL']
    if score_type == 'cls':
        cell = config['Edge']['CLSCell']
        product = config['Edge']['CLSProduct']
    else:
        cell = config['Edge']['ODCell']
        product = config['Edge']['ODProduct']

    # Open file and load into content
    data = open(image_path, 'rb').read()

    # Request parameters
    params = {'productType': product, 'cell': cell}

    # Request headers
    headers = {'Content-Type': 'application/binary', 'Authorization': 'Basic YWRtaW46cGFzc3cwcmRA' }

    # score against the Cloud Scoring API
    try:
        r = requests.post(url, params=params, headers=headers, data=data, verify=False)
    except requests.exceptions.RequestException as e:
        print(e)

    return r

# Score image on cloud
def cloud_score_image(image_path, config, score_type):

    # Pick up options
    url = config['Cloud']['URL']
    if score_type == 'cls':
        cell = config['Cloud']['CLSCell']
        product = config['Cloud']['CLSProduct']
    else:
        cell = config['Cloud']['ODCell']
        product = config['Cloud']['ODProduct']

    # Open file and load into content
    data = open(image_path, 'rb').read()

    # Request parameters
    params = {'productType': product, 'cell': cell,
        'user': os.environ['VIUSER'], 'tenant': config['Cloud']['Tenant'],
        'solution': 'vi'}

    # Request headers
    headers = {'user': os.environ['VIUSER'], 'APIKey': os.environ['VIAPIKEY'], 'Content-Type': 'application/binary' }

    # score against the Cloud Scoring API
    try:
        r = requests.post(url, params=params, headers=headers, data=data)
    except requests.exceptions.RequestException as e:
        print(e)

    return r

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

def showDuration(frame, duration, score_duration):
    if duration > 0.0:
        fps = int(1 / duration)
        score_dur_ms = int(score_duration * 1000)
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
        scale = max(1, int(height / SCALE_SIZE) - 1)
        thickness = int(height / SCALE_SIZE) * 2
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
def showDets(frame, cropped_frame, dets, posx, posy):
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

def getBaseImages(image_path):
    if os.path.exists(image_path):
        if os.path.isdir(image_path):
            images = os.listdir(image_path)
            return images
        else:
            print("Image path isn't a directory: {}".format(image_path))
            return None
    else:
        print("Image path doesn't exist: {}".format(image_path))
        return None

def blur_image(img):
    return cv2.blur(img,(5,5))

def lighten_image(img, value):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img

def darken_image(img, value):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = value
    v[v < lim] = 0
    v[v >= lim] -= value

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img

def rotate_image(mat, angle):

    return imutils.rotate(mat, angle)

# Simulates video and scores it
def simulateVideo(config):

    global OD_LABELS

    # get image
    image_path = config['Record']['ImageDirectory']
    images = getBaseImages(image_path)
    output_path = config['Record']['OutputDirectory']
    image_number = 0
    od_width = int(config['ODRegion']['width'])
    od_height = int(config['ODRegion']['height'])
    cls_width = int(config['CLSRegion']['width'])
    cls_height = int(config['CLSRegion']['height'])

    if images != None:

        cv2.namedWindow("camera", cv2.WINDOW_NORMAL)
        cv2.namedWindow("crop", cv2.WINDOW_NORMAL)
        print("reading image: {}".format(images[image_number]))
        img = cv2.imread(os.path.join(image_path, images[image_number]))
        (h, w) = img.shape[:2]
        posx = max(0, int(w/2 - od_width/2))
        posy = max(0, int(h/2 - od_height/2))

        score = False

        # Set up timers
        last_time = time.clock()
        duration = 0
        det = None
        conf = 0.0
        dets = None
        move_step = 10
        rot = 0

        while True:

            frame = img.copy()
            crop_frame = frame[posy:posy+od_height, posx:posx+od_width]

            drawRect(frame, max(0, posx-1), max(0, posy-1), min(w, posx+od_width+1), min(h, posy+od_height+1), [128,128,128], 1)

            # Get keyboard input
            k = cv2.waitKey(0)
            cloud_score = False

            if k%256 == 27:
                # ESC pressed - break from loop
                print("Escape hit, closing...")
                break
            elif k%256 == 119 or k%256 == 87:
                # W pressed
                posy = max(0, posy-move_step)
            elif k%256 == 115 or k%256 == 83:
                # S pressed
                posy = min(h-od_height, posy+move_step)
            elif k%256 == 97 or k%256 == 65:
                # A pressed
                posx = max(0, posx-move_step)
            elif k%256 == 100 or k%256 == 68:
                # D pressed
                posx = min(w-od_width, posx+move_step)
            elif k%256 == 32:
                # Space pressed - toggle scoring
                score = not score
            elif k%256 >= 48 and k%256 <= 57:
                # (0-9) pressed - switch image ID if changed
                if (k%256 - 48) != image_number:
                    image_number = k%256 - 48
                    print("reading image: {}".format(images[image_number]))
                    img = cv2.imread(os.path.join(image_path, images[image_number]))
                    (h, w) = img.shape[:2]
                    if (posx > w - od_width):
                        posx = w - od_width
                    if (posy > h - od_height):
                        posy = h - od_height
            elif k%256 == 99 or k%256 == 67:
                # C pressed (Clear effects)
                img = cv2.imread(os.path.join(image_path, images[image_number]))
                rot = 0
            elif k%256 == 114 or k%256 == 82:
                # R pressed (Rotate)
                rot += 10
                img = cv2.imread(os.path.join(image_path, images[image_number]))
                img = rotate_image(img, rot)
                (h, w) = img.shape[:2]
                if (posx > w - od_width):
                    posx = w - od_width
                if (posy > h - od_height):
                    posy = h - od_height
            elif k%256 == 108 or k%256 == 76:
                # L pressed (Lighten)
                img = lighten_image(img, 10)
            elif k%256 == 107 or k%256 == 75:
                # K pressed (Lighten)
                img = darken_image(img, 10)
            elif k%256 == 98 or k%256 == 66:
                # K pressed (Lighten)
                img = blur_image(img)
            elif k%256 == 108 or k%256 == 76:
                # L - toggle labels
                OD_LABELS = not OD_LABELS

            # Set dets to None for the iteration
            dets = None
            det = None
            score_duration = 0.0

            if score:

                # Crop area of OD
                od_score_img = img[posy:posy+od_height, posx:posx+od_width]

                # Create image path Name
                image_basename = path.join(output_path, "{}".format(time.time()))
                image_filename = image_basename + ".jpg"

                # Write image to file
                cv2.imwrite(image_filename, od_score_img)

                # Score image on edge
                score_start_time = time.perf_counter()
                r = edge_score_image(image_filename, config, "od")
                # r = score_image(image_filename, config, "od")
                score_duration = time.perf_counter() - score_start_time

                if r.status_code == 200:

                    # print(r.text)

                    # Get dets from OD response
                    dets = parseODResponse(r.text)

                    # If cloud scoring
                    if cloud_score:
                        # Score the image on a thread - asyncronous
                        threading.Thread(target=cloud_score_image,
                            args=(image_filename, config, score_type),
                            kwargs={},
                            ).start()
                else:
                    # Score failed
                    print("{}: {}".format(r.status_code, r.text))

                # Keep file if cloud scoring
                if not cloud_score:
                    # Not cloud scoring - remove file
                    os.remove(image_filename)

            # Calc timings
            current_time = time.perf_counter()
            duration = current_time - last_time
            last_time = current_time

            # Show the class and draw the detections on the frames
            if det:
                showClass(frame, det, conf)
            if dets:
                showDets(crop_frame, crop_frame, dets, posx, posy)

            # Show timer / frame rate
            showDuration(crop_frame, duration, score_duration)

            # print("Duration: {:f}".format(score_duration))

            # Show the frames in a window
            cv2.imshow("camera", frame)
            cv2.imshow("crop", crop_frame)

    cv2.destroyAllWindows()

def printHelp():
    print('Commands:')
    print('Esc: Quit')
    print('WASD: Move Camera')
    print('C: Clear (reset) Image')
    print('B: Blur Image')
    print('R: Rotate image')
    print('L: Lighten image')
    print('K: DarKen image')
    print('Space: Action (score image to cloud)')
    print('L: Toggle object detection confidence labels')
    print('(0-9): Switch to image #0-9 (default 0)')

if __name__ == '__main__':
    args = sys.argv[1:]

    # Parse config file
    parser = SafeConfigParser()
    config_path = args[0] if args else default_config
    config = parser.read(config_path)

    # Print help text
    printHelp()

    # Start recording
    simulateVideo(parser)
