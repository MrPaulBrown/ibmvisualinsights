# VIImageTile.py script

This script crops an image, or set of images in a directory, into a set of overlapping tiled regions of the specified size, with a specified minimum overlap between tiles  

## Usage

`python VIImageTile.py -i <input> -o <output> -x <xsize> -y <ysize> -m <min overlap>`  

Where:
`<input>` is the source file or Directory  
`<output>` is the target Directory  
`<xsize>` is the size of the tile horizontally  
`<ysize>` is the size of the tile vertically  
`<min overlap>` is the minimum overlap area between tiles  

If <input> is a file it will process the image, if it is a directory it will iterate through the files in the directory, processing each in turn  
