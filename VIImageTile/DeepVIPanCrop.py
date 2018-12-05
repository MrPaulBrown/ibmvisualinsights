import VIImageTile
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
        opts, args = getopt.getopt(argv,"hi:o:",["input=","output="])
    except getopt.GetoptError:
        print('DeepVIPanTile.py -i <input> -o <output>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('DeepVIPanTile.py -i <input> -o <output>')
            sys.exit()
        elif opt in ("-i", "--input"):
            input = arg
            if not os.path.exists(input):
                print('-i <input> path does not exist')
                sys.exit(2)
        elif opt in ("-o", "--output"):
            output = arg

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

            VIImageTile.doPanTileImage(indirname, outdirname)

if __name__ == "__main__":
    main(sys.argv[1:])
