import os
import sys
import zipfile
import requests
import json
from distutils.util import strtobool
from argparse import ArgumentParser
import random
from requests_toolbelt.multipart import encoder

headers = {
    'User': os.environ['VIUSERCTP'],
    'APIKEY': os.environ['VIAPIKEYCTP'],
    }
parameters = {
    'user': os.environ['VIUSERCTP'],
    'solution': 'vi',
    }

# headers = {
#     'User': os.environ['VIUSER'],
#     'APIKEY': os.environ['VIAPIKEY'],
#     }
# parameters = {
#     'user': os.environ['VIUSERCTP'],
#     'solution': 'vi',
#     }

def string_to_bool(string):
    return bool(strtobool(str(string)))

def requestDataGroups():

    dataGroups = {}
    # url = 'https://iotm.predictivesolutionsapps.ibmcloud.com/ibm/iotm/service/dataGroup'
    url = 'https://ctp-iotm.predictivesolutionsapps.ibmcloud.com/ibm/iotm/service/dataGroup'
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

    url = 'https://ctp-iotm.predictivesolutionsapps.ibmcloud.com/ibm/iotm/service/dataGroup'
    # url = 'https://iotm.predictivesolutionsapps.ibmcloud.com/ibm/iotm/service/dataGroup'

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

    url = 'https://ctp-iotm.predictivesolutionsapps.ibmcloud.com/ibm/iotm/service/dataFileBinary'
    # url = 'https://iotm.predictivesolutionsapps.ibmcloud.com/ibm/iotm/service/dataFileBinary'
    # url = 'http://httpbin.org/post'

    params = parameters.copy()
    params['groupId'] = id

    heads = headers.copy()
    # heads['Content-Disposition'] = 'form-data; name="files[]"; filename="{}"'.format(basename)

    # try:
        # session = requests.Session()
        # with open(zipfname, 'rb') as f:
        #     form = encoder.MultipartEncoder({
        #         "file": (zipfname, f, "application/zip")
        #     })
        #
        #     r = session.post(url, params=params, headers=heads, data=form)
        # session.close()
        #
        # print(r)


    body = { 'file': (basename, open(zipfname, 'rb'), 'application/zip') }
    try:
        r = requests.post(url, params=params, headers=heads, files=body)

    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    print("Add zip: Status Code: {}".format(r.status_code))
    print("Response: {}".format(r.text))

if __name__ == '__main__':

    parser = ArgumentParser(description="Zip directory contents and load to VI")
    parser.add_argument("-d", "--directory", dest="dirname",
        help="zip and load directory")
    parser.add_argument("-p", "--prefix", dest="prefix",
        help="group name prefix", default='')
    feature_parser = parser.add_mutually_exclusive_group(required=False)
    feature_parser.add_argument('--defect', dest='is_defect', action='store_true')
    feature_parser.add_argument('--no-defect', dest='is_defect', action='store_false')
    parser.set_defaults(feature=True)

    args = parser.parse_args()

    # Get dictionary of existing data groups
    dataGroups = requestDataGroups()

    # Iterate through directory in args
    for root, subdirs, files in os.walk(args.dirname):
        for zipf in files:

            zipfbase = os.path.basename(zipf)
            zipfroot = os.path.splitext(zipfbase)[0]
            zipfname = os.path.join(root, zipf)
            grpname = args.prefix + zipfroot
            print(grpname)

            # Look up to see if data group exists
            if grpname in dataGroups:
                id = dataGroups[grpname]
            else:
                # Data group does not exist - create a new one
                print("Creating data group: {}".format(grpname))
                id = requestCreateDataGroup(grpname, args.is_defect)

            # If data group ID OK, add the zip to the data group
            if id != None:
                print("Adding zip: {} to data group: {}".format(zipfname, id))
                requestAddZipToDataGroup(id, zipfname)
