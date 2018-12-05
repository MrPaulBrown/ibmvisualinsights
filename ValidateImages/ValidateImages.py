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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# import pylab as pl
# from scipy import stats

default_config = 'ValidateImages.config'

from sklearn.metrics import confusion_matrix
import pandas as pd

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

# Parse edge scoring response object (classification)
def vi_parse(text):

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

    return best_det

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

    categories = []
    actuals = []
    preds = []
    image_count = 0
    correct = 0
    costs = {}

    with open(config['Results']['Scores'], mode='w', newline='') as csv_file:

        fieldnames = ['Filename', 'Actual', 'Predicted']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        if os.path.isdir(input):
            for d in os.listdir(input):
                dirname = os.path.join(input, d)
                if os.path.isdir(dirname):
                    # Add directory name to list of categories
                    categories.append(d)
                    for f in os.listdir(dirname):
                        pred = ''
                        fname = os.path.join(dirname, f)
                        if score_type == 'VI':
                            r = cloud_score_image(fname, config, 'cls')
                            if r.status_code == 200:
                                pred = vi_parse(r.text)
                                actuals.append(d)
                                preds.append(pred)
                        else:
                            r = paiv_score_image(fname, config)
                            if r.status_code == 200:
                                pred = paiv_parse(r.text)
                                actuals.append(d)
                                preds.append(pred)

                        writer.writerow({'Filename': fname, 'Actual': d, 'Predicted': pred})

                        image_count += 1
                        if pred == d:
                            correct += 1

            print("Image Count: {}, Correct: {}, Overall Accuracy: {}".format(image_count, correct, correct / image_count))
            cm = confusion_matrix(actuals, preds)
            print(cm)
            cm_as_df=cm2df(cm, categories)
            cm_as_df.to_csv(config['Results']['Confusion'])

            ## and output:
            #cm_as_df

            # pl.matshow(cm)
            # pl.title('Confusion matrix of the classifier')
            # pl.colorbar()
            # pl.show()

        else:
            print('-o <output> path is not a directory')
            sys.exit(2)
