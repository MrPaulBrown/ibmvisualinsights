import VIImageZoom
import os
import sys
import getopt

def main(argv):
    input = ''
    output = ''
    iter = 10
    max_pct = 20
    try:
        opts, args = getopt.getopt(argv,"hi:o:r:p:",["input=","output=","iter=","max_pct="])
    except getopt.GetoptError:
        print('DeepVIImageZoom.py -i <input> -o <output> -r <iterations> -p <max percentage>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('DeepVIImageZoom.py -i <input> -o <output> -r <iterations> -p <max percentage>')
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

            VIImageZoom.doZoom(indirname, outdirname, iter, max_pct)

if __name__ == "__main__":
    main(sys.argv[1:])
