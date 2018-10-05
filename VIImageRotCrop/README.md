# VIImageRotCrop.py script

This script rotates an image (around its centre) a desired number of times and then crops the specified size area from the centre of that image.  

## Usage

`python VIImageRotCrop.py -i <input> -o <output> -x <xsize> -y <ysize> -r <rotations>`  

Where:  
`<input>` is the source file or Directory  
`<output>` is the target Directory  
`<xsize>` is the size of the cropped image horizontally  
`<ysize>` is the size of the cropped image vertically  
`<rotations>` is the numbr of rotations to perform  

If <input> is a file it will process the image, if it is a directory it will iterate through the files in the directory, processing each in turn  
