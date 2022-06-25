import cv2
import numpy as np
from PyQt6.QtGui import QImage

__all__ = ['greyscale', 'red', 'blue', 'green', 'canny']

def greyscale(image):
    grey = np.average(image, axis=-1)
    image[:,:,0] = grey
    image[:,:,1] = grey
    image[:,:,2] = grey
    return image

def red(image):
    image[:,:,1] = 0
    image[:,:,2] = 0
    return image

def green(image):
    image[:,:,0] = 0
    image[:,:,2] = 0
    return image

def blue(image):
    image[:,:,0] = 0
    image[:,:,1] = 0
    return image

def canny(image):
    edges = cv2.Canny(image, 50, 200)
    image[:,:,0] = edges
    image[:,:,1] = edges
    image[:,:,2] = edges
    return image
