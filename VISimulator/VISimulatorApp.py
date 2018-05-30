import time
import sys
import threading
from kivy.clock import Clock, mainthread
from configparser import SafeConfigParser
import re
import os
import glob
import requests
import json
import random
import cv2
import numpy as np
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.bar import Bar
from kivy.uix.label import Label
from kivy.uix.slider import Slider

default_config = 'VISimulator.config'
no_defect_path = ''
defect_path = ''
image_wildcard = ''

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
    scale = int(height / SCALE_SIZE)
    thickness = int(height / SCALE_SIZE) * 2
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
    thick = thickness * int(height / SCALE_SIZE)
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
    thick = 4 * int(height / SCALE_SIZE)
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
        'user': os.environ['VIUSER'], 'tenant': config['Cloud']['Tenant'],
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

class Timer:
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start

class VISimulator(BoxLayout):

    stop = threading.Event()

    def __init__(self, **kwargs):
        super(VISimulator, self).__init__(**kwargs)

        # Create list of sliders
        rates_box = self.ids.rates_box

        img_path = config['Images']['Directory']

        self.sliders = {}

        for root, subdirs, files in os.walk(img_path):
            for subdir in subdirs:
                # Create layout
                slider_layout = BoxLayout()
                slider_layout.orientation = 'horizontal'
                slider_layout.size_hint_y = 0.15
                slider_layout.height = '48dp'

                # Create label
                slider_label = Label(text=subdir)

                # Create slider
                slider = Slider()
                slider.min = 0.0
                slider.max = 1.0
                slider.value = 0.5
                slider.step = 0.1

                # Add widgets
                slider_layout.add_widget(slider_label)
                slider_layout.add_widget(slider)

                self.ids.rates_box.add_widget(slider_layout)

                # Add to sliders dictionary
                self.sliders[subdir] = slider

    def updateStatus(self, status):
        self.ids.response_status.text = str(status)
        if str(status) == "200":
            self.ids.response_status.color = (0,1,0,1)
        else:
            self.ids.response_status.color = (1,0,0,1)

    def updateResponseTime(self, time):
        self.ids.response_time.text = "{:10.4f}".format(time)
        if time > 5:
            self.ids.response_time.color = (1,0,0,1)
        elif time > 2:
            self.ids.response_time.color = (1,1,0,1)
        else:
            self.ids.response_time.color = (0,1,0,1)

    def updateImage(self, src):
        self.ids.image_path.text = src

        # img = Image()
        # img.source='blank.png'
        # self.ids.image_layout.add_widget(img)

    @mainthread
    def updateResults(self, status, responseTime, imagePath, responseText):
        self.updateStatus(status)
        self.updateResponseTime(responseTime)

    @mainthread
    def updateProgress(self, img_count, pct):
        if img_count == -1:
            self.ids.progress.text = 'Not Running'
        else:
            self.ids.progress.text = 'Progress: {} images, {:.1f}%'.format(img_count, pct)

        self.ids.pb.value = pct

    def prepareImages(self):

        image_wildcard = config['Images']['WildcardPattern']

        self.file_dict = {}
        if not self.sliders:
            self.files = glob.glob(os.path.join(config['Images']['Directory'], image_wildcard))
        else:
            for key, value in self.sliders.items():
                self.file_dict[key] = glob.glob(os.path.join(config['Images']['Directory'], key, image_wildcard))

    def getImage(self):

        img_set = None
        # No sliders - return image from the path
        if not self.sliders:
            img_set = self.files
        else:
            # Sliders - get cumulative sum
            keys = list(self.sliders.keys())
            sum = 0.0
            for key, value in self.sliders.items():
                sum += value.value

            group = None
            if sum == 0.0:
                # All sliders at zero - select file at random
                img_set = self.file_dict[random.choice(keys)]
            else:
                # Find the key to use
                rand = random.random() * sum
                cum = 0.0
                for key, value in self.sliders.items():
                    cum += value.value
                    if rand < cum:
                        img_set = self.file_dict[key]
                        break

        return random.choice(img_set)

    def simulation(self):

        # print ("Starting simulation")

        start_time = time.time()
        last_time = start_time
        current_duration = 0
        # print("Start Time: %s", time.ctime(start_time))

        self.prepareImages()

        num_images = 0

        # Repeat until duration finishes
        while not(self.stop.is_set()) and \
            ((time.time() - start_time) < (self.ids.durationSlider.value * 60)):

            required_duration = 60 / self.ids.requestRateSlider.value

            # Select image at random based on defect rate
            img_path = self.getImage()

            score_type = config['Cloud']['ModelType']

            score_time = time.clock()
            r = cloud_score_image(img_path, config, score_type)
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

                # Display the scored image
                img = displayImage(img_path)
                updateImage(img, det, conf, dets, duration)

            else:
                # Score failed
                print("{}: {}".format(r.status_code, r.text))

            current_time = time.time()
            current_duration = current_time - last_time

            progress = ((current_time - start_time) / (self.ids.durationSlider.value * 60)) * 100

            self.updateProgress(num_images + 1, progress)

            sleep_int = 0.1
            if current_duration < required_duration:
                sleep_int = required_duration - current_duration

            time.sleep(sleep_int)

            last_time = time.time()

            # Get keyboard input
            k = cv2.waitKey(1)
            action = False

            if k%256 == 27:
                # ESC pressed - break from loop
                print("Escape hit, closing...")
                observer.stop()
                break

            num_images += 1

        # print ("Exiting simulation")
        self.stopSimulation()

    def startSimulation(self):
        self.stop.clear()
        self.ids.btn.background_color = (1, 0, 0, 0.5)
        self.ids.btn.text = 'Stop Simulation'
        threading.Thread(target=self.simulation).start()

    def stopSimulation(self):
        self.stop.set()
        self.ids.btn.background_color = (0, 1, 0, 0.5)
        self.ids.btn.text = 'Start Simulation'
        if self.ids.btn.state == 'down':
            self.ids.btn.state = 'normal'
        self.updateProgress(-1, 0.0)

    def click(self):
        if self.ids.btn.state == 'down':
            self.startSimulation()
        else:
            self.stopSimulation()



class VISimulatorApp(App):

    scorer = None

    def build(self):
        return VISimulator()

    def on_stop(self):
        # The Kivy event loop is about to stop, set a stop signal;
        # otherwise the app window will close, but the Python process will
        # keep running until all secondary threads exit.
        self.root.stop.set()

    @mainthread
    def updateResults(self, status, responseTime, imagePath, responseText):
        return self.root.updateResults(status, responseTime,imagePath, responseText)

if __name__ == '__main__':
    args = sys.argv[1:]

    # Parse config file
    config = SafeConfigParser()
    config_path = args[0] if args else default_config
    config.read(config_path)

    app = VISimulatorApp()

    app.run()
