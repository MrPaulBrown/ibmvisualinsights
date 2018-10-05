import os
import sys
import zipfile
import requests
import json
from distutils.util import strtobool
from argparse import ArgumentParser
import random

headers = {
    'User': os.environ['VIUSER'],
    'APIKEY': os.environ['VIAPIKEY'],
    }
parameters = {
    'user': os.environ['VIUSER'],
    'solution': 'vi',
    }

def string_to_bool(string):
    return bool(strtobool(str(string)))

def requestDataGroups():

    dataGroups = {}
    url = 'https://iotm.predictivesolutionsapps.ibmcloud.com/ibm/iotm/service/dataGroup'
    try:
        r = requests.get(url, params=parameters, headers=headers)

    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    if r.status_code == 200:
        try:
            parsed = json.loads(r.text)

            # Populate dataGroups dict
            for dg in parsed:
                if 'groupName' in dg and 'id' in dg:
                    dataGroups[dg['groupName']] = dg['id']

        except ValueError:
            print("JSON Parse Error: {}".format(r.text))
    else:
        print("Response Status Code: {}".format(r.status_code))
        print("Response: {}".format(r.text))

    return dataGroups

def requestCreateDataGroup(name, is_defect):

    url = 'https://iotm.predictivesolutionsapps.ibmcloud.com/ibm/iotm/service/dataGroup'

    json_body = [
        {
            "groupName": name,
            "description": "",
            "parameters": {
                "isHybrid": "false",
                "isDefect": "true" if is_defect else "false"
            }
        }
    ]

    id = None

    try:
        r = requests.post(url, params=parameters, headers=headers, json=json_body)

    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    if r.status_code == 201:
        try:
            print(r.text)
            parsed = json.loads(r.text)

            id = parsed[0]['id']

        except ValueError:
            print("JSON Parse Error: {}".format(r.text))
    else:
        print("Response Status Code: {}".format(r.status_code))
        print("Response: {}".format(r.text))

    return id

def requestAddZipToDataGroup(id, zipfname):

    basename = os.path.basename(zipfname)

    url = 'https://iotm.predictivesolutionsapps.ibmcloud.com/ibm/iotm/service/dataFileBinary'

    params = parameters.copy()
    params['groupId'] = id

    heads = headers.copy()
    heads['Content-Disposition'] = 'form-data; name="files[]"; filename="{}"'.format(basename)

    body = { 'file': (basename, open(zipfname, 'rb'), 'application/zip') }

    try:
        r = requests.post(url, params=params, headers=heads, files=body)

    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    print("Add zip: Status Code: {}".format(r.status_code))
    print("Response: {}".format(r.text))

def createZip(zipfname):
    print("Zip filename: {}".format(zipfname))
    zipf = zipfile.ZipFile(zipfname, 'w', zipfile.ZIP_DEFLATED)
    return zipf

def addToZip(zipf, file):
    # print("Writing: {}".format(file))
    zipf.write(file, os.path.basename(file))

def closeZip(zipf):
    print("Closing zip")
    zipf.close()

def zipDirectory(root, subdir):

    # Zip name
    zipfname = os.path.join(root, os.path.basename(subdir) + ".zip")

    # Create zip file
    zipf = createZip(zipfname)

    # Create zip for sub folder
    # Iterate through files, add jpgs to zip
    for r, subs, files in os.walk(os.path.join(root, subdir)):
        for f in files:
            fname, fext = os.path.splitext(f)
            if fext == ".jpg":
                addToZip(zipf, os.path.join(r, f))

    # Close Zip
    closeZip(zipf)

    return zipfname

def zipDirectorySplit(root, subdir, trainpct):

    # Zip name
    trn_zipfname = os.path.join(root, "trn_" + os.path.basename(subdir) + ".zip")
    tst_zipfname = os.path.join(root, "tst_" + os.path.basename(subdir) + ".zip")

    # Create zip file
    trn_zipf = createZip(trn_zipfname)
    tst_zipf = createZip(tst_zipfname)

    # Create zip for sub folder
    # Iterate through files, add jpgs to zip
    for r, subs, files in os.walk(os.path.join(root, subdir)):
        for f in files:
            fname, fext = os.path.splitext(f)
            if fext == ".jpg":
                if random.random() < trainpct:
                    addToZip(trn_zipf, os.path.join(r, f))
                else:
                    addToZip(tst_zipf, os.path.join(r, f))

    # Close Zip
    closeZip(trn_zipf)
    closeZip(tst_zipf)

    return (trn_zipfname, tst_zipfname)

class Range(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end
    def __eq__(self, other):
        return self.start <= other <= self.end

if __name__ == '__main__':

    parser = ArgumentParser(description="Zip directory contents and load to VI")
    parser.add_argument("-d", "--directory", dest="dirname",
        help="zip and load directory")
    feature_parser = parser.add_mutually_exclusive_group(required=False)
    feature_parser.add_argument('--defect', dest='is_defect', action='store_true')
    feature_parser.add_argument('--no-defect', dest='is_defect', action='store_false')
    parser.set_defaults(feature=True)
    parser.add_argument("-s", "--split", dest="trainpct",
        help="training split proportion (0.0 - 1.0)",
        type=float, default=1.0, choices=[Range(0.0, 1.0)])
    parser.add_argument("-p", "--prefix", dest="prefix",
        help="group name prefix", default='')

    args = parser.parse_args()

    # Get dictionary of existing data groups
    dataGroups = requestDataGroups()

    split = args.trainpct != 1.0

    # Iterate through directory in args
    for root, subdirs, files in os.walk(args.dirname):
        for subdir in subdirs:

            if split:
                # Create a zip for each sub directory
                trn_zipfname, tst_zipfname = zipDirectorySplit(root, subdir, args.trainpct)
            else:
                # Create a zip for each sub directory
                zipfname = zipDirectory(root, subdir)

            grpname = args.prefix + subdir

            # Look up to see if data group exists
            if grpname in dataGroups:
                id = dataGroups[grpname]
            else:
                # Data group does not exist - create a new one
                print("Creating data group: {}".format(grpname))
                id = requestCreateDataGroup(grpname, args.is_defect)

            # If data group ID OK, add the zip to the data group
            if id != None:
                if split:
                    print("Adding zip: {} to data group: {}".format(trn_zipfname, id))
                    requestAddZipToDataGroup(id, trn_zipfname)
                    print("Adding zip: {} to data group: {}".format(tst_zipfname, id))
                    requestAddZipToDataGroup(id, tst_zipfname)
                else:
                    print("Adding zip: {} to data group: {}".format(zipfname, id))
                    requestAddZipToDataGroup(id, zipfname)
