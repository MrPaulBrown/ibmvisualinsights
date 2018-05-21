# VIZipAndLoad script

This utility script creates a set of image groups in Visual Insights from a directory containing sub-directories of images.

The script iterates through the sub-directories of the target directory (passed on the command line) and automatically zips up the images (files with extension ".jpg") into a zip file for that sub-directory.  It then creates an image group in VI for each sub-directory (using the sub-directory name as the image name) if that image group doesn't already exist.  It then adds the associated zip file to the image group.

## Set-up

Set up the environment and common libraries as per the general README.md

## Usage

Run from python, e.g.

`python VIWatcherCloud.py <target directory> [<is defect>]`

where:

<target directory> is the directory containing the image sub-directories
<is defect> is a flag to indicate whether new groups should have the defect flag or not.  Optional parameter with default value True.

Note that the <is defect> option will apply to all image groups so if you want to create both 'defect' and 'no defect' image groups then it is recommended you organize your image directories into 'defect' and 'no defect' folders and run the script twice with different target folders and <is defect> settings.
