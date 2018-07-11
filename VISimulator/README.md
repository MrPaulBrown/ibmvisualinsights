# VISimulator script

This script simulates sending a sequence of images to Visual Insights for scoring.

## Set-up

Set up the environment and common libraries as per the general README.md

This script also requires the Kivy UI framework.  Follow these [installation instructions](https://kivy.org/docs/installation/installation.html) to install Kivy

### Models deployed in IBM Visual Insights

These scripts require at least one model to be deployed in IBM Visual Insights and accessible via the uploadScoreImage API

### Config file

Modify the config file (VISimulator.config) to set the following options:

[Images]  
Directory:  **Set to the local path location of your images**  
WildcardPattern: **Set to match to a wildcard pattern**  

[Cloud]  
URL: **Set to Visual Insights uploadScoreImage URL**  
Tenant: **Set to desired tenant ID**  
Cell: **Set to scoring cell for classification model**  
Product: **Set to product type code for classification model**  
ModelType: **Set to 'cls' for a classification model and 'od' for an object detection model**  

## Usage

Run from python, e.g.

`python VISimulator.py`

The script will launch a UI to allow the user to configure the simulation.  In addition, the setting of the "Directory" path in the configuration will govern the simulator behavior:

+ If the Directory only contains images (no sub-directories) then the simulator will pick images from random from the Directory.  
+ If the directory contains sub-directories of images then the UI will be configured to allow the user to 'balance' the images from each sub-directory.  At each iteration, the simulator will pick a sub-directory based on the relative balance of all sub-directories and then choose an image at random from that folder.  

The script will create a window showing the current scored image.  This will update as each new image is scored.

UI Controls

The user can control:

+ the request rate (in requests per minute)  
+ the duration of the simulation (in minutes)  
+ starting and stopping of the simulation  

Commands:  
Esc: Quit  

### Explanation of output

Score time is shown as the number of s in the bottom corner of the capture window

Classification results are displayed in the scoring window as the top class and confidence scores

Object detection results are displayed as a set of boxes on the image.  The width of the box represents the confidence level.  The color shows the object detected (reflected by the displayed key)

The UI also provides feedback on the image scored, the response status and response time.  
