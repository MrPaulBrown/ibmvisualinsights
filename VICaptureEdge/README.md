# VICaptureEdge script

This script uses an attached webcam to capture images for scoring against an IBM Visual Insights model deployed to an Edge system.  It is designed to be run directly on the Edge system.

## Set-up

Set up the environment and common libraries as per the general README.md

### Models deployed on IBM Visual Insights Edge

These scripts require at least one model to be deployed onto the IBM Visual Insights edge system and accessible via the local scoreimage API



### Config file

Modify the config file (VICaptureEdge.config) to set the following options:

[Record]  
OutputDirectory: **Set to the local path to store images**  

[Crop]  
crop: **Set to _True_ to crop the frame or _False_ otherwise**  
xmin: **X min of crop window**  
ymin: **Y min of crop window**  
xmax: **X max of crop window**  
ymax: **Y max of crop window**  

[Score]  
URL: **Set to the singlescore URL of the local Edge system**  
CLSModelID: **Set to the model id of the classification model**  
ODModelID: **Set to the model id of the object detection model**  

[Cloud]  
URL: **Set to Visual Insights uploadScoreImage URL**  
Tenant: **Set to desired tenant ID**  
CLSCell: **Set to scoring cell for classification model**  
CLSProduct: **Set to product type code for classification model**  
ODCell: **Set to scoring cell for object detection model**  
ODProduct: **Set to product type code for object detection model**  

## Usage

Run from python, e.g.

`python VICaptureEdge.py`

The script will create a window showing the current capture.  The following keyboard command can be used:

Commands:  
Esc: Quit  
Space: Action (score image to cloud)  
S: Toggle scoring (default: off)  
C: Switch to classification mode (default: on)  
O: Switch to Object Detection mode  
L: Toggle object detection confidence labels  
(0-9): Switch to camera ID #0-9 (default 0)  

The space bar can be used to send the current frame to IBM Visual Insights, otherwise it will be scored on the local edge.

### Explanation of output

Duration information is shown as the number of ms for the image scoring and the calculated frame rate for the full cycle (including image capture and display)

Classification results are displayed in the scoring window as the top class and confidence scores

Object detection results are displayed as a set of boxes on the image.  The width of the box represents the confidence level.  The color shows the object detected (reflected by the displayed key)
