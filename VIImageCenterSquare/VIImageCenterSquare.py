import math
import sys
import os
import getopt
import cv2

def squareImage(filename, outputdir, size):

    img = cv2.imread(filename)

    if img is not None:

        basename, fname = os.path.split(filename)
        rootname, file_extension = os.path.splitext(fname)

        # get image height, width
        (h, w) = img.shape[:2]

        if size <= 0:
            size = min(h, w)

        midh = h / 2
        midw = w / 2

        ymin = int(midh - (size / 2))
        ymax = int(midh + (size / 2))
        xmin = int(midw - (size / 2))
        xmax = int(midw + (size / 2))

        crop = img[ymin:ymax, xmin:xmax]

        cropfn = "{}_sq{}".format(rootname, file_extension)
        crop_filename = os.path.join(outputdir, cropfn)

        cv2.imwrite(crop_filename, crop)

    else:
        # Problem reading file
        print("Failed to read file: {}".format(filename))


def doCenterSquare(input, output, size):
    print('Input is {}'.format(input))
    print('Output is {}'.format(output))

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
        for f in os.listdir(input):
            filename = os.path.join(input, f)
            squareImage(filename, output, size)
    else:
        squareImage(input, output, size)

def main(argv):
    input = ''
    output = ''
    xsize = 0
    ysize = 0
    min_overlap = 0
    try:
        opts, args = getopt.getopt(argv,"hi:o:s:",["input=","output=","size="])
    except getopt.GetoptError:
        print('VIImageCenterSquare.py -i <input> -o <output> -s <size>')
        sys.exit(2)

    size = 0;

    for opt, arg in opts:
        if opt == '-h':
            print('VIImageCenterSquare.py -i <input> -o <output> -s <size>')
            sys.exit()
        elif opt in ("-i", "--input"):
            input = arg
            if not os.path.exists(input):
                print('-i <input> path does not exist')
                sys.exit(2)
        elif opt in ("-o", "--output"):
            output = arg
        elif opt in ("-s", "--size"):
            size = int(arg)

    doCenterSquare(input, output, size)

if __name__ == "__main__":
    main(sys.argv[1:])
