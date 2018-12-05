import math
import sys
import os
import getopt
import cv2
import xml.etree.ElementTree as ET

def readCenters(annotation):
    centers = []
    if os.path.exists(annotation):
        try:
            tree = ET.parse(annotation)
            for obj in tree.getroot().iter('object'):

                print(obj)
                name = obj.find('name').text
                bbox = obj.find('bndbox')

                x = int(bbox.find('xmin').text) + int((int(bbox.find('xmax').text) - int(bbox.find('xmin').text))/2)
                y = int(bbox.find('ymin').text) + int((int(bbox.find('ymax').text) - int(bbox.find('ymin').text))/2)

                center = {
                    'name' : name,
                    'x' : x,
                    'y' : y}

                print(center)
                centers.append(center)
        except ET.ParseError:
            print("Error parsing XML")

    return centers

def cropROIImage(filename, annotation, outputdir, x, y):

    print('reading centers')

    # Read Annotations to get the box centers
    centers = readCenters(annotation)

    if len(centers) > 0:

        # print("Tiling: {}".format(filename))
        # print("Output dir: {}".format(outputdir))

        print('reading image')

        img = cv2.imread(filename)

        if img is not None:

            basename, fname = os.path.split(filename)
            rootname, file_extension = os.path.splitext(fname)

            # get image height, width
            (h, w) = img.shape[:2]

            count = 0

            for center in centers:

                xmin = int(center['x'] - (x/2))
                xmax = int(center['x'] + (x/2))
                ymin = int(center['y'] - (y/2))
                ymax = int(center['y'] + (y/2))

                xpadl = 0
                xpadr = 0
                ypadl = 0
                ypadr = 0
                if xmin < 0:
                    xpadl = abs(xmin)
                    xmin = 0
                if ymin < 0:
                    ypadl = abs(xmin)
                    ymin = 0
                if xmax > w:
                    xpadr = xmax - w
                    xmax = w
                if ymax > h:
                    ypadr = ymax - h
                    ymax = h

                print('crop: {}, ({},{}),({},{})'.format(center['name'], xmin, ymin, xmax, ymax))

                crop = img[ymin:ymax, xmin:xmax]

                if xpadl + xpadr + ypadl + ypadr > 0:
                    crop = cv2.copyMakeBorder(img,ypadl,ypadr,xpadl,xpadr,cv2.BORDER_CONSTANT,value=[0,0,0])

                cropfn = "{}_{}_{}{}".format(rootname, center['name'], count, ".jpg")
                crop_filename = os.path.join(outputdir, cropfn)

                cv2.imwrite(crop_filename, crop)

                count += 1

        else:
            # Problem reading file
            print("Failed to read file: {}".format(filename))

def doCropROI(input, annotations, output, xsize, ysize):
    print('Input is {}'.format(input))
    print('Annotations is {}'.format(input))
    print('Output is {}'.format(output))
    print('x, y is {}, {}'.format(xsize, ysize))

    if xsize < 100 or ysize < 100:
        print('Image size too small')
        sys.exit(2)

    if not os.path.exists(output):
        try:
            os.makedirs(output)
        except OSError:
            print('Error creating output directory')
            sys.exit(2)
    elif not os.path.isdir(output):
        print('-o <output> path is not a directory')
        sys.exit(2)

    if os.path.isdir(input):
        if os.path.isdir(annotations):
            for f in os.listdir(input):
                filename = os.path.join(input, f)
                annotation = os.path.join(annotations, os.path.splitext(f)[0]) + ".xml"
                cropROIImage(filename, annotation, output, xsize, ysize)
        else:
            print('-a <annotations> path is not a directory')
    else:
        if os.path.isdir(annotations):
            print('-a <annotations> path is a directory')
        else:
            cropROIImage(input, annotations, output, xsize, ysize)

def main(argv):
    input = ''
    output = ''
    xsize = 0
    ysize = 0
    try:
        opts, args = getopt.getopt(argv,"hi:a:o:x:y:",["input=","annotations=","output=","xsize=","ysize="])
    except getopt.GetoptError:
        print('VIImageCropROI.py -i <input> -a <annotations> -o <output> -x <x size> -y <y size>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('VIImageCropROI.py -i <input> -a <annotations> -o <output> -x <x size> -y <y size>')
            sys.exit()
        elif opt in ("-i", "--input"):
            input = arg
            if not os.path.exists(input):
                print('-i <input> path does not exist')
                sys.exit(2)
        elif opt in ("-a", "--annotations"):
            annotations = arg
            if not os.path.exists(annotations):
                print('-a <annotations> path does not exist')
                sys.exit(2)
        elif opt in ("-o", "--output"):
            output = arg
        elif opt in ("-x", "--xsize"):
            try:
                xsize = int(arg)
            except ValueError:
                print('-x <x size> option requires an integer value')
                sys.exit(2)
        elif opt in ("-y", "--ysize"):
            try:
                ysize = int(arg)
            except ValueError:
                print('-y <y size> option requires an integer value')
                sys.exit(2)

    doCropROI(input, annotations, output, xsize, ysize)

if __name__ == "__main__":
    main(sys.argv[1:])
