# VIImageCropROI.py script

This script takes an image and its object detection annotation file and, for each object detected, crops a an area of the desired size from the center of the detection.  

## Usage

`python VIImageCropROI.py -i <input> -a <annotations> -o <output> -x <xsize> -y <ysize>`  

Where:  
`<input>` is the source file or directory
`<annotations` is the annotation file or directory  
`<output>` is the target directory  
`<xsize>` is the size of the cropped image horizontally  
`<ysize>` is the size of the cropped image vertically  

If <input> is a file it will process the image, if it is a directory it will iterate through the files in the directory, processing each in turn  
