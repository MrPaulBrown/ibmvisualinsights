# ValidateImages scripts

These utility scripts send a directory of images to the VI scoring service (or the PowerAI Vision scoring service) to be scored and collate and process the results.  There are two scripts - one for classification models and the other for object detection models

## Set-up

Set up the environment and common libraries as per the general README.md

### ValidateImages (Classification) Config file

Modify the config file (ValidateImages.config) to set the following options:

[Images]  
Directory: **Set to the local path of the images to score**  

[Results]
Scores: **Set the pathname of the results csv file**    
Confusion: **Set the pathname of the confusion matrix csv file**    

[Score]  
URL: **Set to the image scoring URL**  
Type: **Set to "VI" for Visual Insights scoring or "PAIV" for PowerAI Vision scoring**  
Cell: **Set to scoring cell for classification model**  
Product: **Set to product type code for classification model**  

### ValidateImagesOD (Object Detection) Config file

Modify the config file (ValidateImagesOD.config) to set the following options:

[Images]  
Directory: **Set to the local path of the images to score**  

[Results]
Scores: **Set the pathname of the results csv file**    
OutputDirectory: **Set the pathname of the output directory of the scored images**    

[Score]  
URL: **Set to the image scoring URL**  
Type: **Set to "VI" for Visual Insights scoring or "PAIV" for PowerAI Vision scoring (TBD)**  
Cell: **Set to scoring cell for model**  
Product: **Set to product type code for model**  

## Usage

Run from python, e.g.

`python ValidateImages.py`
`python ValidateImagesOD.py`
