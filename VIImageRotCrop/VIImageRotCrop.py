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

def rotcropImage(filename, outputdir, xsize, ysize, rotations):

    # print("Tiling: {}".format(filename))
    # print("Output dir: {}".format(outputdir))

    img = cv2.imread(filename)

    if img is not None:

        basename, fname = os.path.split(filename)
        rootname, file_extension = os.path.splitext(fname)

        # Perform Rotations
        for r in range(rotations):

            angle = 360 * (r / rotations)

            rot_img = rotate_image(img, angle)

            # get image height, width
            (h, w) = rot_img.shape[:2]
            xmin = int(w/2 - xsize/2)
            xmax = int(w/2 + xsize/2)
            ymin = int(h/2 - ysize/2)
            ymax = int(h/2 + ysize/2)

            crop = rot_img[ymin:ymax, xmin:xmax]

            cropfn = "{}_{}{}".format(rootname, r, file_extension)
            crop_filename = os.path.join(outputdir, cropfn)

            cv2.imwrite(crop_filename, crop)

    else:
        # Problem reading file
        print("Failed to read file: {}".format(filename))


def main(argv):
    input = ''
    output = ''
    xsize = 0
    ysize = 0
    rotations = 4
    try:
        opts, args = getopt.getopt(argv,"hi:o:x:y:r:",["input=","output=","xsize=","ysize=","minoverlap="])
    except getopt.GetoptError:
        print('VIRotCrop.py -i <input> -o <output> -x <x size> -y <y size> -r <# rotations>')
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
        elif opt in ("-r", "--rotations"):
            try:
                rotations = int(arg)
            except ValueError:
                print('-r <rotations> option requires an integer value')
                sys.exit(2)

    print('Input is {}'.format(input))
    print('Output is {}'.format(output))
    print('x, y is {}, {}'.format(xsize, ysize))
    print('Rotations is {}'.format(rotations))

    if xsize < 100 or ysize < 100:
        print('Image size too small')
        sys.exit(2)

    if rotations > 360:
        print('Too many rotations')
        sys.exit(2)

    if rotations < 1:
        print('Too few rotations')
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
            rotcropImage(filename, output, xsize, ysize, rotations)
    else:
        rotcropImage(input, output, xsize, ysize, rotations)

if __name__ == "__main__":
    main(sys.argv[1:])
