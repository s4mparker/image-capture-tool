import PyQt6.QtWidgets as qt
import cv2 as cv

from sys import exit

class Window(qt.QWidget):

    def __init__(self, size=(300, 200)):
        # Basic window setup
        super().__init__()
        self.setWindowTitle('Image Capture Tool')
        self.setFixedSize(size[0], size[1])

        # Create the window and its contents
        self.create_widgets()
        self.position_widgets()
        self.connect_widgets()

    def create_widgets(self):
        # Create the form elements
        self.imageCount = qt.QSpinBox(parent=self)
        self.imageCount.setRange(1, 250)

    def position_widgets(self):
        # Create the main window layout
        layout = qt.QHBoxLayout()

        # Create the form layout
        form = qt.QFormLayout()

        # Insert here
        form.addRow('Images (#)', self.imageCount)

        layout.addLayout(form)
        self.setLayout(layout)

    def connect_widgets(self):
        pass












if __name__ == '__main__':
    app = qt.QApplication([])
    window = Window()
    window.show()
    exit(app.exec())
