from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QImage, QPixmap
import cv2

class CameraView(QLabel):

    blank = QPixmap(QImage('./resources/error.png'))

    def __init__(self, **kwargs):
        super().__init__(kwargs)

        self.feed   = cv2.VideoCapture(-1)
        timer       = QTimer(parent=self)

        self.feed.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        timer.setInterval(50)
        timer.timeout.connect(self.refresh)
        timer.start()

    def refresh(self):
        img_response = self.feed.read()

        image = self.blank
        if img_response[0]:
            raw = cv2.flip(cv2.cvtColor(img_response[1], cv2.COLOR_RGB2BGR), 1)
            image = QPixmap(QImage(raw, raw.shape[1], raw.shape[0], raw.shape[1]*3, QImage.Format.Format_RGB888))
        
        self.setPixmap(image)

    def get(self):
        return self.pixmap
