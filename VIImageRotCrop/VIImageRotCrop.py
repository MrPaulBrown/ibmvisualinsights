import math
import sys
import os
import getopt
import cv2

def rotate_image(mat, angle):
    height, width = mat.shape[:2]
    image_center = (width / 2, height / 2)

    rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1)

    radians = math.radians(angle)
    sin = math.sin(radians)
    cos = math.cos(radians)
    bound_w = int((height * abs(sin)) + (width * abs(cos)))
    bound_h = int((height * abs(cos)) + (width * abs(sin)))

    rotation_mat[0, 2] += ((bound_w / 2) - image_center[0])
    rotation_mat[1, 2] += ((bound_h / 2) - image_center[1])

    rotated_mat = cv2.warpAffine(mat, rotation_mat, (bound_w, bound_h))
    return rotated_mat

def rotcropImage(filename, outputdir, rotations, degs):

    # print("Tiling: {}".format(filename))
    # print("Output dir: {}".format(outputdir))

    img = cv2.imread(filename)

    if img is not None:

        basename, fname = os.path.split(filename)
        rootname, file_extension = os.path.splitext(fname)

        (h, w) = img.shape[:2]
        size = min(h, w)

        # Perform Rotations
        for r in range(rotations):

            angle = (degs * (r / rotations)) - (degs / 2.0)

            rot_img = rotate_image(img, angle)

            # get image height, width
            (h, w) = rot_img.shape[:2]
            xmin = int(w/2 - size/2)
            xmax = int(w/2 + size/2)
            ymin = int(h/2 - size/2)
            ymax = int(h/2 + size/2)

            crop = rot_img[ymin:ymax, xmin:xmax]

            cropfn = "{}_{}{}".format(rootname, r, file_extension)
            crop_filename = os.path.join(outputdir, cropfn)

            cv2.imwrite(crop_filename, crop)

    else:
        # Problem reading file
        print("Failed to read file: {}".format(filename))

def doRotCrop(input, output, rotations, degrees):

    print('Input is {}'.format(input))
    print('Output is {}'.format(output))
    print('Rotations is {}'.format(rotations))
    print('Degrees is {}'.format(degrees))

    if rotations > 360:
        print('Too many rotations')
        sys.exit(2)

    if rotations < 1:
        print('Too few rotations')
        sys.exit(2)

    if degrees > 360 or degrees < 0:
        print('Degrees should be in range 0-360')
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
            rotcropImage(filename, output, rotations, degrees)
    else:
        rotcropImage(input, output, rotations, degrees)

def main(argv):
    input = ''
    output = ''
    xsize = 0
    ysize = 0
    rotations = 4
    try:
        opts, args = getopt.getopt(argv,"hi:o:r:d:",["input=","output=","rotations=","degrees="])
    except getopt.GetoptError:
        print('VIImageRotCrop.py -i <input> -o <output> -r <# rotations> -d <degrees>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('VIImageRotCrop.py -i <input> -o <output> -r <# rotations> -d <degrees>')
            sys.exit()
        elif opt in ("-i", "--input"):
            input = arg
            if not os.path.exists(input):
                print('-i <input> path does not exist')
                sys.exit(2)
        elif opt in ("-o", "--output"):
            output = arg
        elif opt in ("-r", "--rotations"):
            try:
                rotations = int(arg)
            except ValueError:
                print('-r <rotations> option requires an integer value')
                sys.exit(2)
        elif opt in ("-d", "--degrees"):
            try:
                degrees = int(arg)
            except ValueError:
                print('-d <degrees> option requires an integer value')
                sys.exit(2)

    doRotCrop(input, output, rotations, degrees)

if __name__ == "__main__":
    main(sys.argv[1:])
