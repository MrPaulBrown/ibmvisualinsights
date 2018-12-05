import VIImageRotCrop
import os
import sys
import getopt

def main(argv):
    input = ''
    output = ''
    xsize = 0
    ysize = 0
    min_overlap = 0
    try:
        opts, args = getopt.getopt(argv,"hi:o:r:d:",["input=","output=","rotations=","degrees="])
    except getopt.GetoptError:
        print('VIDeepImageRotCrop.py -i <input> -o <output> -r <# rotations> -d <degrees>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('VIDeepImageRotCrop.py -i <input> -o <output> -r <# rotations> -d <degrees>')
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

    if not os.path.isdir(input):
        print('Input is not a directory')
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

    for d in os.listdir(input):
        indirname = filename = os.path.join(input, d)
        if os.path.isdir(indirname):
            outdirname = filename = os.path.join(output, d)
            if not os.path.exists(outdirname):
                os.makedirs(outdirname)

            VIImageRotCrop.doRotCrop(indirname, outdirname, rotations, degrees)

if __name__ == "__main__":
    main(sys.argv[1:])
