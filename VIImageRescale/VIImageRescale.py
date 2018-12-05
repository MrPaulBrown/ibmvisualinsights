import math
import sys
import os
import getopt
import cv2

def rescaleImage(filename, outputdir, x, y):

    # print("Tiling: {}".format(filename))
    # print("Output dir: {}".format(outputdir))

    img = cv2.imread(filename)

    if img is not None:

        basename, fname = os.path.split(filename)
        rootname, file_extension = os.path.splitext(fname)

        # get image height, width
        (h, w) = img.shape[:2]

        resize_img = cv2.resize(img, (y, x))

        resfn = "{}_{}_{}{}".format(rootname, x, y, file_extension)
        res_filename = os.path.join(outputdir, resfn)

        cv2.imwrite(res_filename, resize_img)

    else:
        # Problem reading file
        print("Failed to read file: {}".format(filename))

def doRescale(input, output, xsize, ysize):
    print('Input is {}'.format(input))
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
        for f in os.listdir(input):
            filename = os.path.join(input, f)
            rescaleImage(filename, output, xsize, ysize)
    else:
        rescaleImage(input, output, xsize, ysize)

def main(argv):
    input = ''
    output = ''
    xsize = 0
    ysize = 0
    try:
        opts, args = getopt.getopt(argv,"hi:o:x:y:r:",["input=","output=","xsize=","ysize="])
    except getopt.GetoptError:
        print('VIImageRescale.py -i <input> -o <output> -x <x size> -y <y size>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('VIImageTile.py -i <input> -o <output> -x <x size> -y <y size> -m <min overlap>')
            sys.exit()
        elif opt in ("-i", "--input"):
            input = arg
            if not os.path.exists(input):
                print('-i <input> path does not exist')
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

    doRescale(input, output, xsize, ysize)

if __name__ == "__main__":
    main(sys.argv[1:])
