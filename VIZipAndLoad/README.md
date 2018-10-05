# VIZipAndLoad script

This utility script creates a set of image groups in Visual Insights from a directory containing sub-directories of images.

The script iterates through the sub-directories of the target directory (passed on the command line) and automatically zips up the images (files with extension ".jpg") into a zip file for that sub-directory.  It then creates an image group in VI for each sub-directory (using the sub-directory name as the image name) if that image group doesn't already exist.  It then adds the associated zip file to the image group.

## Set-up

Set up the environment and common libraries as per the general README.md

## Usage

Run from python, e.g.

`python VIZipAndLoad.py -d <target directory>`

Arguments:

-d, --directory - sets the directory to process  
--defect, --no-defect - set whether to classify categories as defects  
-s, --split - sets the train/test split, e.g. 0.75 = 75% images in training set  
-p, --prefix - sets a prefix to add to the names of the image groups

where:

<--directory> is the directory containing the image sub-directories
<--defect/--no-defect> is a flag to indicate whether new groups should have the defect flag or not.  Optional parameter with default value True.

Note that the <--defect> option will apply to all image groups so if you want to create both 'defect' and 'no defect' image groups then it is recommended you organize your image directories into 'defect' and 'no defect' folders and run the script twice with different target folders and <is defect> settings.  

The training <--split> parameter allows you to automatically split the data into training and testing partitions based on a random (probabilistic) split.  Train and test zips will be prefixed by "trn" and "tst" prefixes.  

The <--prefix> parameter allows a prefix to be added to the name of the image group.  It can be useful to have a common prefix to aid in searching for groups.  
