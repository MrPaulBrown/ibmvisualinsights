# VIImageCenterSquare.py script

This script crops a central square out of a rectangular image, or set of images in a directory.  The square will have the dimensions of the smallest side of the original rectangle, if size is not specified as a parameter  

## Usage

`python VIImageCenterSquare.py -i <input> -o <output> -s <size>

Where:  
`<input>` is the source file or Directory  
`<output>` is the target Directory  
`<size>` is the target size of the square  

If <input> is a file it will process the image, if it is a directory it will iterate through the files in the directory, processing each in turn  

If <size> is set to zero or a negative number then the square will be the size of the shortest side of the rectangle
