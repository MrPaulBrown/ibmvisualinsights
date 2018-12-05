import math
import sys
import os
import getopt
import cv2

def padSquareImage(filename, outputdir):

    img = cv2.imread(filename)

    if img is not None:

        basename, fname = os.path.split(filename)
        rootname, file_extension = os.path.splitext(fname)

        # get image height, width
        (h, w) = img.shape[:2]

        min_size = min(h, w)
        max_size = max(h, w)

        pad_size = int((max_size - min_size) / 2)

        BLACK = [0,0,0]

        if h < w:
            pad = cv2.copyMakeBorder(img,pad_size,pad_size,0,0,cv2.BORDER_CONSTANT,value=BLACK)
        elif w < h:
            pad = cv2.copyMakeBorder(img,0,0,pad_size,pad_size,cv2.BORDER_CONSTANT,value=BLACK)
        else:
            pad = img

        padfn = "{}_pad{}".format(rootname, file_extension)
        pad_filename = os.path.join(outputdir, padfn)

        cv2.imwrite(pad_filename, pad)

    else:
        # Problem reading file
        print("Failed to read file: {}".format(filename))


def doPadSquare(input, output):
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
            padSquareImage(filename, output)
    else:
        padSquareImage(input, output)

def main(argv):
    input = ''
    output = ''
    xsize = 0
    ysize = 0
    min_overlap = 0
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["input=","output="])
    except getopt.GetoptError:
        print('VIImagePadSquare.py -i <input> -o <output>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('VIImagePadSquare.py -i <input> -o <output>')
            sys.exit()
        elif opt in ("-i", "--input"):
            input = arg
            if not os.path.exists(input):
                print('-i <input> path does not exist')
                sys.exit(2)
        elif opt in ("-o", "--output"):
            output = arg

    doPadSquare(input, output)

if __name__ == "__main__":
    main(sys.argv[1:])
