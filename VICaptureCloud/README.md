# VICaptureCloud script

This script uses an attached webcam to capture images for scoring against an IBM Visual Insights deployed model

## Set-up

Set up the environment and common libraries as per the general README.md

### Models deployed in IBM Visual Insights

These scripts require at least one model to be deployed in IBM Visual Insights and accessible via the uploadScoreImage API

### Config file

Modify the config file (VICaptureCloud.config) to set the following options:

[Record]  
OutputDirectory: **Set to the local path to store images**  

[Crop]  
crop: **Set to _True_ to crop the frame or _False_ otherwise**  
xmin: **X min of crop window**  
ymin: **Y min of crop window**  
xmax: **X max of crop window**  
ymax: **Y max of crop window**  

[Cloud]  
URL: **Set to Visual Insights uploadScoreImage URL**  
Tenant: **Set to desired tenant ID**  
CLSCell: **Set to scoring cell for classification model**  
CLSProduct: **Set to product type code for classification model**  
ODCell: **Set to scoring cell for object detection model**  
ODProduct: **Set to product type code for object detection model**  

## Usage

Run from python, e.g.

`python VICaptureCloud.py`

The script will create a window showing the current capture.  The following keyboard command can be used:

Commands:  
Esc: Quit  
Space: Action (save image or score image)  
S: Toggle scoring (default: off)  
C: Switch to classification mode (default: on)  
O: Switch to Object Detection mode  
L: Toggle object detection confidence labels  
(0-9): Switch to camera ID #0-9 (default 0)  

In scoring mode, the space bar can be used to send the current frame to IBM Visual Insights.

In non-scoring mode, the frame will be saved to the local filesystem (useful for creating a training set)

### Explanation of output

Duration of cycle (capture, scoring and display of images) is shown as the number of ms in the bottom corner of the capture window and the calculated frame rate

Classification results are displayed in the scoring window as the top class and confidence scores

Object detection results are displayed as a set of boxes on the image.  The width of the box represents the confidence level.  The color shows the object detected (reflected by the displayed key)
