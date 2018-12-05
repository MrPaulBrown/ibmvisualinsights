# VIImagePadSquare.py script

This script pads an image, or set of images in a directory, into a  into a square region the size of the longest side of the base image

## Usage

`python VIImagePadSquare.py -i <input> -o <output>`  

Where:  
`<input>` is the source file or Directory  
`<output>` is the target Directory   

If <input> is a file it will process the image, if it is a directory it will iterate through the files in the directory, processing each in turn  
