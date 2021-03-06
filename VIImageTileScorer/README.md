# VIImageTileScorer script

This script watches a local directory for new or changes images and scores against an IBM Visual Insights deployed model.  Scoring is done by tiling the main image, according to the tiling setting and scoring each tile invidually.  The results are shown on the main image.

## Set-up

Set up the environment and common libraries as per the general README.md

### Models deployed in IBM Visual Insights

These scripts require at least one model to be deployed in IBM Visual Insights and accessible via the uploadScoreImage API

### Config file

Modify the config file (VIWatcherCloud.config) to set the following options:

[Images]  
SourceDirectory:  **Set to the local path to store images**  
OutputDirectory:  **Set to the local path to save the tiled images**  
WildcardPattern: **Set to match to a wildcard pattern**  
Regex: **Set to match a regular expression pattern or leave blank**  

[Tile]  
xsize:   **Set to the size of the tile width**  
ysize:   **Set to the size of the tile height**  
min_overlap:   **Set to the size of the tile overlap**  

[Score]
ModelType: **Set to 'cls' for a classification model and 'od' for an object detection model**  
ScoreMode: **Set to 'Edge' for edge scoring and 'Cloud' for cloud scoring**  

[Edge]
URL: **Set to the singlescore URL of the local Edge system**  
ModelID: **Set to the model id of the deployed model**  

[Cloud]  
URL: **Set to Visual Insights uploadScoreImage URL**  
Tenant: **Set to desired tenant ID**  
Cell: **Set to scoring cell for classification model**  
Product: **Set to product type code for classification model**  

## Usage

Run from python, e.g.

`python VIImageTileScorer.py`

The script will create a window showing the current image.  This will update when an image is dropped into the watched folder and again when the results of the model are applied.

Commands:  
Esc: Quit  

### Explanation of output

Score time is shown as the number of s in the bottom corner of the capture window

Classification results are displayed in the scoring window as the top class and confidence scores for each tile

Object detection results are displayed as a set of boxes on the image.  The width of the box represents the confidence level.  The color shows the object detected (reflected by the displayed key).  No consolidation of results is provided if the same object appears in multiple tiles  
