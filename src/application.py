from PyQt6.QtCore import QTimer
import PyQt6.QtWidgets as qt
import cv2 as cv

from sys import exit
from os import getcwd

class Window(qt.QWidget):

    def __init__(self, size=(400, 200)):
        # Basic window setup
        super().__init__()
        self.setWindowTitle('Image Capture Tool')
        self.setFixedSize(size[0], size[1])

        # Create the window and its contents
        self.create_widgets()
        self.position_widgets()
        self.connect_widgets()

        # Create a variable to track how many images have been taken so far
        self.images_taken = 0

    def create_widgets(self):
        # Create the form elements
        self.images = qt.QSpinBox(parent=self)
        self.images.setRange(1, 500)
        self.images.setSingleStep(10)

        self.refresh = qt.QSpinBox(parent=self)
        self.refresh.setRange(1, 100)

        self.activeDirectory = qt.QLineEdit(parent=self)
        self.activeDirectory.setText(getcwd())
        self.activeDirectory.setDisabled(True)

        self.selectDirectory = qt.QPushButton(parent=self)
        self.selectDirectory.setText('Select Directory')

        self.submit = qt.QPushButton(parent=self)
        self.submit.setText('Submit')

        self.progress = qt.QProgressBar(parent=self)
        self.progress.setRange(0, 100)

        self.timer = QTimer(parent=self)

    def position_widgets(self):
        layout = qt.QHBoxLayout()
        control = qt.QVBoxLayout()
        form = qt.QFormLayout()

        form.addRow('Images (#)', self.images)
        form.addRow('Refresh Rate (#/s)', self.refresh)
        form.addRow('Active Directory', self.activeDirectory)
        form.addRow(self.selectDirectory)
        form.addRow(self.submit)

        control.addLayout(form)
        control.addWidget(self.progress)
        layout.addLayout(control)
        self.setLayout(layout)

    def connect_widgets(self):
        self.selectDirectory.clicked.connect(self.select_directory)
        self.submit.clicked.connect(self.run)
        self.timer.timeout.connect(self.take_image)

    def run(self):
        self.images_taken = 0
        self.timer.setInterval(int(1000/self.refresh.value()))
        self.progress.setValue(0)
        self.timer.start()

    def take_image(self):
        if self.images_taken < self.images.value():
            print(f'Image {self.images_taken}')
            self.images_taken += 1
        else:
            self.timer.stop()

        int_images_taken = int(self.images_taken / self.images.value() * 100)
        if int_images_taken > 100: int_images_taken = 100
        self.progress.setValue(int_images_taken)
        
    def select_directory(self):
        dir = qt.QFileDialog.getExistingDirectoryUrl(parent=self).toLocalFile()
        print(dir)
        if len(dir) > 0:
            self.activeDirectory.setText(dir)


if __name__ == '__main__':
    app = qt.QApplication([])
    window = Window()
    window.show()
    exit(app.exec())
