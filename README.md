# ImageCaptureTool
A simple tool that enables a large number of images to be captured from a user's webcam in a relatively short period of time. This is often useful when generating image datasets for machine learning models.

## Usage
- To run the main application, execute `python3 run.py`
- To clear all images present in a directory (this was particularly useful in testing!), execute `python3 run.py -clear <path>` where `<path>` is the directory's relative path from the current working directory

## Parameters
- `Images`: The number of images to capture
- `Rate`: The number of images to capture per second (e.g rate=5 means 5 images captured per second)
- `Label`: The images' associated label that will be stored alongside the filename in the selected class/labelling file
- `File Extension`: The file extension to be used when saving images
- `Filename Format`: The filename format to be used when saving images
- `Ignore filename duplication`: If this is checked, any duplicated filenames will be ignored and skipped. This means that less images may be captured than expected

## Dependancies
- Python 3
- PyQt6