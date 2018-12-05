import math
import sys
import os
import getopt
import cv2

def zoomImage(filename, outputdir, iter, max_pct):

    # print("Tiling: {}".format(filename))
    # print("Output dir: {}".format(outputdir))

    img = cv2.imread(filename)

    if img is not None:

        basename, fname = os.path.split(filename)
        rootname, file_extension = os.path.splitext(fname)

        # get image height, width
        (h, w) = img.shape[:2]
        size = min(h, w)

        for i in range(iter):

            pct = i * ((max_pct / iter) / 100)

            if pct > 0.0:
                offset = size * pct

                xmin = int(offset/2)
                xmax = int(w - offset/2)
                ymin = int(offset/2)
                ymax = int(h - offset/2)
                crop = img[ymin:ymax, xmin:xmax]
            else:
                crop = img

            cropfn = "{}_{}{}".format(rootname, i, file_extension)
            crop_filename = os.path.join(outputdir, cropfn)

            cv2.imwrite(crop_filename, crop)

    else:
        # Problem reading file
        print("Failed to read file: {}".format(filename))

def doZoom(input, output, iter, max_pct):
    print('Input is {}'.format(input))
    print('Output is {}'.format(output))
    print('Iterations is {}'.format(iter))
    print('Max percent is {}'.format(max_pct))

    if max_pct <= 0 or max_pct > 90:
        print('Max percentage should be between 1 and 90')
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
            zoomImage(filename, output, iter, max_pct)
    else:
        zoomImage(input, output, iter, max_pct)

def main(argv):
    input = ''
    output = ''
    iter = 10
    max_pct = 20
    try:
        opts, args = getopt.getopt(argv,"hi:o:r:p:",["input=","output=","iter=","max_pct="])
    except getopt.GetoptError:
        print('VIImageZoom.py -i <input> -o <output> -r <iterations> -p <max percentage>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('VIImageZoom.py -i <input> -o <output> -r <iterations> -p <max percentage>')
            sys.exit()
        elif opt in ("-i", "--input"):
            input = arg
            if not os.path.exists(input):
                print('-i <input> path does not exist')
                sys.exit(2)
        elif opt in ("-o", "--output"):
            output = arg
        elif opt in ("-r", "--iterations"):
            try:
                iter = int(arg)
            except ValueError:
                print('-r <iterations> option requires an integer value')
                sys.exit(2)
        elif opt in ("-p", "--max_pct"):
            try:
                max_pct = int(arg)
            except ValueError:
                print('-p <max_pct> option requires an integer value')
                sys.exit(2)

    doZoom(input, output, iter, max_pct)

if __name__ == "__main__":
    main(sys.argv[1:])
