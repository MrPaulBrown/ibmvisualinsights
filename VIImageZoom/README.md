# VIImageZoom.py script

This script zooms into the center of an image through a number of iterations to the desired target zoom level.  For example, zooming to 20% over 4 iterations would produce the images at 5, 10, 15 and 20% zoom levels.  

## Usage

`python VIImageZoom.py -i <input> -o <output> -r <iterations> -p <percentage>`  

Where:  
`<input>` is the source file or Directory  
`<output>` is the target Directory  
`<iterations>` is the number of zoom iterations  
`<percentage>` is the maximum zoom percentage  

If <input> is a file it will process the image, if it is a directory it will iterate through the files in the directory, processing each in turn  
