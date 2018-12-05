# VIImageRescale.py script

This script re-scales an image, or set of images, to a desired size.  

## Usage

`python VIImageRescale.py -i <input> -o <output> -x <xsize> -y <ysize>`  

Where:  
`<input>` is the source file or Directory  
`<output>` is the target Directory  
`<xsize>` is the size of the target image horizontally  
`<ysize>` is the size of the target image vertically  

If <input> is a file it will process the image, if it is a directory it will iterate through the files in the directory, processing each in turn  
