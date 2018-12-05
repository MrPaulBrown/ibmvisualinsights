import math
import sys
import os
import getopt
import cv2

def getNumberOfTiles(size, tile_size, min_overlap):
    return math.ceil(size/(tile_size-min_overlap))

def getOverlap(size, num_tiles, tile_size):
    return abs(((size-tile_size)/(num_tiles-1))-tile_size)

def tileProc(img, filename, outputdir, xsize, ysize, min_overlap):
    # get image height, width
    (h, w) = img.shape[:2]

    xtiles = getNumberOfTiles(w, xsize, min_overlap)
    ytiles = getNumberOfTiles(h, ysize, min_overlap)

    xoverlap = getOverlap(w, xtiles, xsize)
    yoverlap = getOverlap(h, ytiles, ysize)

    # print("xtiles: {}, xoverlap: {}".format(xtiles, xoverlap))
    # print("ytiles: {}, yoverlap: {}".format(ytiles, yoverlap))

    basename, fname = os.path.split(filename)
    rootname, file_extension = os.path.splitext(fname)

    yoffset = 0

    for ytile in range(ytiles):
        xoffset = 0
        for xtile in range(xtiles):

            xmin = xoffset
            xmax = xoffset + xsize
            ymin = yoffset
            ymax = yoffset + ysize
            crop = img[int(ymin):int(ymax), int(xmin):int(xmax)]

            cropfn = "{}_{}_{}{}".format(rootname, ytile, xtile, file_extension)
            crop_filename = os.path.join(outputdir, cropfn)

            # print("{}, ({}, {}) ({}, {})".format(crop_filename, xmin, ymin, xmax, ymax))

            cv2.imwrite(crop_filename, crop)

            xoffset = xmax - xoverlap

        yoffset = ymax - yoverlap

def tileImage(filename, outputdir, xsize, ysize, min_overlap):

    # print("Tiling: {}".format(filename))
    # print("Output dir: {}".format(outputdir))

    img = cv2.imread(filename)

    if img is not None:
        tileProc(img, filename, outputdir, xsize, ysize, min_overlap)
    else:
        # Problem reading file
        print("Failed to read file: {}".format(filename))

def panTileImage(filename, outputdir):

    # print("Tiling: {}".format(filename))
    # print("Output dir: {}".format(outputdir))

    img = cv2.imread(filename)

    if img is not None:

        # get image height, width
        (h, w) = img.shape[:2]

        tile_size = min(h, w)
        tileProc(img, filename, outputdir, tile_size, tile_size, 0)

    else:
        # Problem reading file
        print("Failed to read file: {}".format(filename))


def doPanTileImage(input, output):
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
            panTileImage(filename, output)
    else:
        panTileImage(input, output)


def doTileImage(input, output, xsize, ysize, min_overlap):
    print('Input is {}'.format(input))
    print('Output is {}'.format(output))
    print('x, y is {}, {}'.format(xsize, ysize))
    print('Min overlap is {}'.format(min_overlap))

    if xsize < 100 or ysize < 100:
        print('Image size too small')
        sys.exit(2)

    if min_overlap > (xsize / 2) or min_overlap > (ysize / 2):
        print('Min overlap too big')
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
            tileImage(filename, output, xsize, ysize, min_overlap)
    else:
        tileImage(input, output, xsize, ysize, min_overlap)

def main(argv):
    input = ''
    output = ''
    xsize = 0
    ysize = 0
    min_overlap = 0
    try:
        opts, args = getopt.getopt(argv,"hi:o:x:y:m:",["input=","output=","xsize=","ysize=","minoverlap="])
    except getopt.GetoptError:
        print('VIImageTile.py -i <input> -o <output> -x <x size> -y <y size> -m <min overlap>')
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
        elif opt in ("-m", "--maxoverlap"):
            try:
                min_overlap = int(arg)
            except ValueError:
                print('-m <min overlap> option requires an integer value')
                sys.exit(2)

    doTileImage(input, output, xsize, ysize, min_overlap)

if __name__ == "__main__":
    main(sys.argv[1:])
