from os import listdir, remove, getcwd
from os.path import exists, isfile, isdir

from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from PyQt6.QtWidgets import QMainWindow, QWidget, QPushButton, QSpinBox, QLabel, QLineEdit, QFormLayout, QFileDialog, QProgressBar, QStatusBar
from PyQt6.QtGui import QIcon, QAction

from .camera import CameraView
from .timer import Timer

class Application(QMainWindow):

    start_timer = pyqtSignal(int, int)
    end_timer = pyqtSignal()
    show_error = pyqtSignal(str)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create the central widget
        self.root = QWidget(parent=self)
        self.setCentralWidget(self.root)

        # Create the timer used to capture the images at regular intervals
        self.timer = Timer()

        # Object variables used to store the directory and classfile paths
        self.directory = None
        self.classfile = None

        # Construct the central widget's sub-components
        form = QFormLayout()
        self.root.setLayout(form)

        self.feed = CameraView()
        self.images = QSpinBox(parent=self, minimum=1, maximum=500)
        self.rate = QSpinBox(parent=self, minimum=1, maximum=100, value=50)
        self.label = QLineEdit(parent=self)
        self.generate = QPushButton(parent=self, text='Generate')
        self.error = QLabel(parent=self, text=' ')
        self.progress = QProgressBar(parent=self, minimum=0, maximum=100, enabled=False, value=0)

        form.addRow(self.feed)
        form.addRow('Images', self.images)
        form.addRow('Rate', self.rate)
        form.addRow('Label', self.label)
        form.addRow(self.generate)
        form.addRow(self.progress)
        form.addRow(self.error)

        # Connect the components together
        self.generate.clicked.connect(self._begin)
        self.start_timer.connect(self.timer._begin)
        self.end_timer.connect(self.timer._end)
        self.timer.step.connect(self._capture)
        self.timer.end.connect(self._end)
        self.show_error.connect(self._seterror)

        # Show the final application
        self.show()

    def _begin(self):
        # Perform some basic validation
        msg = None
        if self.images.value() < 1:
            msg = 'Images is expected to be greater than 1'
        elif self.rate.value() < 1:
            msg = 'Rate is expected to be greater than 1'
        elif len(self.label.text()) < 1:
            msg = 'Label is expected to be atleast one character'
        self.show_error.emit(msg)
        if msg: return

        # Request directory and classfile input from the user
        self.directory = None
        self.classfile = None

        directory = QFileDialog.getExistingDirectoryUrl(parent=self, caption='Select a directory', directory=QUrl(f'{getcwd()}/')).toLocalFile()
        if len(directory) < 1:
            self.show_error.emit('Failed to select a directory')
            return
        else:
            self.directory = directory
        
        classfile = QFileDialog.getSaveFileUrl(parent=self, caption='Select a classfile', directory=QUrl(f'{getcwd()}/'), filter='CSV (*.csv)', options=QFileDialog.Option.DontConfirmOverwrite)[0].toLocalFile()
        if len(classfile) < 1:
            self.show_error.emit('Failed to select a classfile')
            return
        else:
            self.classfile = classfile
        
        print(f'D: {self.directory}, C: {self.classfile}')
        self.progress.setEnabled(True)
        self.progress.setValue(0)
        self.start_timer.emit(self.images.value(), self.rate.value())

    def _capture(self, completion, counter):
        filename = f'{counter}.jpg'
        path = f'{self.directory}/{filename}'

        if exists(path):
            self.end_timer.emit()
            self.show_error.emit(f'Encountered a duplicate on {filename}')
            return
        else:
            response = self.feed.get().save(path)
            if not response:
                self.end_timer.emit()
                self.show_error.emit(f'Encountered an unknown error on {filename}')
                return

        with open(self.classfile, mode='a') as file:
            file.write(f'{filename},{self.label.text()}\n')

        self.progress.setValue(int(completion*100))
        print(counter)

    def _end(self):
        self.progress.setValue(0)
        self.progress.setEnabled(False)
        self.directory = None
        self.classfile = None
        
    def _seterror(self, text):
        if text:
            self.error.setText(f'Error: {text}')
        else:
            self.error.setText(f' ')

