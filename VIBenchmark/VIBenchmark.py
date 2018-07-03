import requests
from configparser import SafeConfigParser
import random
import glob
import time
import os
import sys
import numpy as np
from scipy import stats

default_config = 'VIBenchmark.config'

# Scores image to edge
def score_image(image_path, url, modelID):

    # Json body for request
    json = { 'modelID': modelID, 'imageFile': image_path }

    # score against the Edge API
    try:
        r = requests.post(url, json=json)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    return r

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

    image_path = config['Images']['Directory']
    image_wildcard = config['Images']['WildcardPattern']
    url = config['Score']['URL']
    modelID = config['Score']['ModelID']
    duration = int(config['Benchmark']['Duration'])

    fileset = getFileSet(image_path, image_wildcard)

    scoreImages(fileset, duration, url, modelID)
