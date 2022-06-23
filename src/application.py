from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QImage, QPixmap
import PyQt6.QtWidgets as qt
import cv2 as cv

from sys import exit
from os import getcwd

class Window(qt.QWidget):

    imsize = (400, 400)

    def __init__(self):
        # Basic window setup
        super().__init__()
        self.setWindowTitle('Image Capture Tool')

        # Setup the video capture
        self.video = cv.VideoCapture(-1)
        self.video.set(cv.CAP_PROP_BUFFERSIZE, 1)

        # Create the window and its contents
        self.create_widgets()
        self.position_widgets()
        self.connect_widgets()

        # Create a variable to track how many images have been taken so far
        self.images_taken = 0

    def create_widgets(self):
        self.imageCount = qt.QSpinBox(parent=self)
        self.imageCount.setRange(1, 500)

        self.refreshRate = qt.QSpinBox(parent=self)
        self.refreshRate.setRange(1, 100)

        self.activeDirectory = qt.QLineEdit(parent=self)
        self.activeDirectory.setText('Please select...')
        self.activeDirectory.setReadOnly(True)

        self.labelsFile = qt.QLineEdit(parent=self)
        self.labelsFile.setText('Please select...')
        self.labelsFile.setReadOnly(True)

        self.submit = qt.QPushButton(parent=self)
        self.submit.setText('Submit')

        self.selectDirectory = qt.QPushButton(parent=self)
        self.selectDirectory.setText('Select Directory')

        self.selectLabelsFile = qt.QPushButton(parent=self)
        self.selectLabelsFile.setText('Select Labels File')

        self.progress = qt.QProgressBar(parent=self)
        self.progress.setRange(0, 100)

        self.image = qt.QLabel(parent=self)
        self.image.setMaximumSize(self.imsize[0], self.imsize[1])
        
        self.clock = QTimer(parent=self)
        self.clock.setInterval(50)
        self.slot_update()

        self.captureTimer = QTimer(parent=self)

    def position_widgets(self):
        layout = qt.QHBoxLayout()
        self.setLayout(layout)
        control = qt.QVBoxLayout()
        layout.addLayout(control)
        form = qt.QFormLayout()
        control.addLayout(form)

        form.addRow('Images (#)', self.imageCount)
        form.addRow('Refresh Rate (#/s)', self.refreshRate)
        form.addRow('Active Directory', self.activeDirectory)
        form.addRow('Labels File', self.labelsFile)
        form.addRow(self.submit)

        selections = qt.QHBoxLayout()
        control.addLayout(selections)

        selections.addWidget(self.selectDirectory)
        selections.addWidget(self.selectLabelsFile)

        control.addWidget(self.progress)

        layout.addWidget(self.image)

    def connect_widgets(self):
        self.selectDirectory.clicked.connect(self.slot_select_directory)
        self.selectLabelsFile.clicked.connect(self.slot_select_labels_file)
        self.submit.clicked.connect(self.slot_submit)

        self.clock.timeout.connect(self.slot_update)
        self.captureTimer.timeout.connect(self.slot_capture_image)

        self.clock.start()

    def slot_update(self):
        image = self.video.read()[1]
        image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
        image = cv.flip(image, flipCode=1)
        image = QPixmap(QImage(image, image.shape[1], image.shape[0], image.shape[1] * 3, QImage.Format.Format_RGB888))
        image = image.scaled(self.imsize[0], self.imsize[1])
        self.image.setPixmap(image)

    def slot_submit(self):
        self.images_taken = 0
        self.captureTimer.setInterval(int(1000/self.refreshRate.value()))
        self.progress.setValue(0)
        self.captureTimer.start()

    def slot_capture_image(self):
        if self.images_taken < self.imageCount.value():
            print(f'Saved to {self.activeDirectory.text()}/image_{self.images_taken}.jpg')
            image = self.image.pixmap()
            image.save(f'{self.activeDirectory.text()}/image_{self.images_taken}.jpg')
            self.images_taken += 1
        else:
            self.captureTimer.stop()

        int_images_taken = int(self.images_taken / self.imageCount.value() * 100)
        if int_images_taken > 100: int_images_taken = 100
        self.progress.setValue(int_images_taken)
        
    def slot_select_directory(self):
        dir = qt.QFileDialog.getExistingDirectoryUrl(parent=self).toLocalFile()
        if len(dir) > 0:
            self.activeDirectory.setText(dir)

    def slot_select_labels_file(self):
        file = qt.QFileDialog.getOpenFileUrl(parent=self)[0].toLocalFile()
        if len(file) > 0:
            self.labelsFile.setText(file)

if __name__ == '__main__':
    app = qt.QApplication([])
    window = Window()
    window.show()
    exit(app.exec())
