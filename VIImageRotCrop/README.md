# VIImageRotCrop.py script

This script rotates an image (around its centre) a desired number of times and then crops the specified size area from the centre of that image.  

## Usage

`python VIImageRotCrop.py -i <input> -o <output> -x <xsize> -y <ysize> -r <rotations> -d <degrees>`  

Where:  
`<input>` is the source file or Directory  
`<output>` is the target Directory  
`<xsize>` is the size of the cropped image horizontally  
`<ysize>` is the size of the cropped image vertically  
`<rotations>` is the numbr of rotations to perform  
`<degrees>` is the maximum number of degrees to rotate through

Note that the <degrees> setting will set rotation angle from + (<degrees> / 2) to ( - <degrees> / 2).  For example, setting a max rotation of 90 degrees will rotation from -45 degrees to +45 degress.

If <input> is a file it will process the image, if it is a directory it will iterate through the files in the directory, processing each in turn  
