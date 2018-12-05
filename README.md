# ibmvisualinsights
Collection of Python scripts for IBM Visual Insights

This Git is intended as a repo for utility and demo scripts for IBM Visual Insights

## Common Set up

### Python version

The scripts were built for Python 3.x and tested on Python 3.6

### Environment

These scripts use the following environment variables for access to the VI APIs.

You will need to set these in your environment:

VIUSER:  IBM ID of the user account

VIAPIKEY: API Key for the VIUSER

### Required libraries

The scripts use the following libraries:

opencv-python  
requests  
watchdog  

Install via pip using:

`python -m pip install <library-name>`

Refer to the README.md for each script for further set-up and usage

### Summary of scripts  

**ValidateImages** - scripts for running batches of images through VI scoring  
**VIBenchmark** - script for benchmarking edge scoring performance  
**VICaptureCloud** - tool to capture webcam feed and score to VI cloud  
**VICaptureEdge** - tool to capture webcam feed and score to VI edge  
**VIImageCenterSquare** - prep script to crop a square region from the center of rectangular images  
**VIImageCropROI** - prep script to crop a region from an image based on object detection regions  
**VIImagePadSquare** - prep script to create a square image from a rectangular one by padding (letter-boxing) the short side  
**VIImageRescale** - prep script to rescale images to a desired size  
**VIImageRotCrop** - prep script to perform multiple rotations on a base image and then crop to a target size  
**VIImageTile** - prep script to crop images into a set of overlapped, smaller regions  
**VIImageZoom** - prep script to zoom into a base image at multiple levels (e.g. 5, 10, 15, 20%)  
**VISimulator** - tool to simulate a continuous stream of images into VI from a set of images in directories  
**VIWatcherCloud** - tool to watch a directory for new/changed images and score them to the cloud  
**VIZipAndLoad** - utility scripts to automate the upload of data files to VI, creating data groups as required and optionally splitting into train/test  
