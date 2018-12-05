# VILocateClassifySimEdge script

This script simulates a moving camera across an image and applying an object detection model.  When the object is detected the area around the object is cropped and classified using a classification model.  The simulator allows the user to move the focus of the object detection (denoted by a square box) and also add live effects (rotation, darken, lighten, blur) to simulate a live camera.  The user can also switch between up to 10 images.    

## Set-up

Set up the environment and common libraries as per the general README.md

### Models deployed on IBM Visual Insights Edge

These scripts require at least one OD model and one classification model to be deployed onto the IBM Visual Insights edge system and accessible via the local scoreimage API  

### Config file

Modify the config file (VILocateClassifySimEdge.config) to set the following options:

[Record]  
ImageDirectory: **Set to the local path of the base images**  
OutputDirectory: **Set to the local path to store the cropped  images**  

[CLSRegion]  
width: **width of classification area**  
height: **height of classification area**  

[ODRegion]  
width: **width of object detection area**  
height: **height of object detection area**


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

`python VILocateClassifySimEdge.py`

The script will create a window showing image and a second window showing a zoomed in view of the object detection window:

Commands:  
Esc: Quit  
WASD: Move 'camera' Up, Left, Down, Right  
(0-9): Switch image #0-9 (default 0)
R: Rotate image 10 degrees  
B: Blur image  
L: Lighten image  
K: DarKen image  
<Space>: Toggle scoring (default: off)  
L: Toggle object detection labels  

The space bar can be used to send the current frame to IBM Visual Insights, otherwise it will be scored on the local edge.

### Explanation of output

Duration information is shown as the number of ms for the image scoring and the calculated frame rate for the full cycle (including image capture and display)

Classification results are displayed in the scoring window as the top class and confidence scores

Object detection results are displayed as a set of boxes on the image.  The width of the box represents the confidence level.  The color shows the object detected (reflected by the displayed key)
