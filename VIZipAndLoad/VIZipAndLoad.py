import os
import sys
import zipfile
import requests
import json
from distutils.util import strtobool

headers = {
    'User': os.environ['VIUSER'],
    'APIKEY': os.environ['VIAPIKEY'],
    }
parameters = {
    'user': os.environ['VIUSER'],
    'solution': 'vi',
    'tenant': 'T1'
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

if __name__ == '__main__':
    args = sys.argv[1:]

    is_defect = True

    if len(args) > 1:
        is_defect = string_to_bool(args[1])

    # Get dictionary of existing data groups
    dataGroups = requestDataGroups()

    # Iterate through directory in args
    for root, subdirs, files in os.walk(args[0]):
        for subdir in subdirs:

            # Create a zip for each sub directory
            zipfname = zipDirectory(root, subdir)

            # Look up to see if data group exists
            if subdir in dataGroups:
                id = dataGroups[subdir]
            else:
                # Data group does not exist - create a new one
                print("Creating data group: {}".format(subdir))
                id = requestCreateDataGroup(subdir, is_defect)

            # If data group ID OK, add the zip to the data group
            if id != None:
                print("Adding zip: {} to data group: {}".format(zipfname, id))
                requestAddZipToDataGroup(id, zipfname)
