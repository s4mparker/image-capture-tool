from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QImage, QPixmap, QColor

import cv2

class CameraView(QLabel):

    def __init__(self, **kwargs):
        # Parse the provided keyword arguments
        self.updateRate = kwargs.pop('updateRate', 1)
        self.imageSize  = kwargs.pop('imageSize', None)
        self.imageScale = kwargs.pop('imageScale', 1)

        # Call the super constructor
        super().__init__(**kwargs)

        # Create a variable to hold a blank frame
        blank = QImage(100, 100, QImage.Format.Format_RGB888)
        blank.fill(QColor('red'))
        self.blankImage = QPixmap(blank)

        # Create a variable to hold the current camera frame
        self.image = None

        # Create the video capture object used to get the camera feed
        self.feed = cv2.VideoCapture(-1)
        self.feed.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # Create the timer to refresh the label's image
        self.timer = QTimer(parent=self)
        self.timer.setInterval(self.updateRate)
        self.timer.timeout.connect(self.slot_update)

        # Start the timer and manually refresh the image
        self.slot_update()
        self.timer.start()

    def slot_update(self):
        # Get the latest frame
        response = self.feed.read()

        # If no response - simply use a blank frame instead
        if not response[0]:
            self.image = self.blankImage
        # Otherwise - use the camera feed's image
        else:
            raw_image = cv2.flip(cv2.cvtColor(response[1], cv2.COLOR_RGB2BGR), 1)
            self.image = QPixmap(QImage(raw_image, raw_image.shape[1], raw_image.shape[0], raw_image.shape[1]*3, QImage.Format.Format_RGB888))
        
        # Scale the image if required
        if self.imageSize:
            self.image = self.image.scaled(self.imageSize[0], self.imageSize[1])
        if self.imageScale:
            self.image = self.image.scaled(int(self.image.width()*self.imageScale), int(self.image.height()*self.imageScale))

        # Set the label's pixmap to the desired image
        self.setPixmap(self.image)

    def get_image(self):
        # Return the current image
        return self.image