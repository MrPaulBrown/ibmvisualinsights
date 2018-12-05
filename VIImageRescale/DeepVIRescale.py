import VIImageRescale
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
        opts, args = getopt.getopt(argv,"hi:o:x:y:",["input=","output=","xsize=","ysize="])
    except getopt.GetoptError:
        print('VIDeepImageRescale.py -i <input> -o <output> -x <x size> -y <y size>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('VIDeepImageRescale.py -i <input> -o <output> -x <x size> -y <y size>')
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

            VIImageRescale.doRescale(indirname, outdirname, xsize, ysize)

if __name__ == "__main__":
    main(sys.argv[1:])
