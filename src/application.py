from os import listdir, remove, getcwd
from os.path import exists, isfile, isdir

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QWidget, QToolBar, QSpinBox, QLabel, QLineEdit, QFormLayout, QFileDialog, QProgressBar
from PyQt6.QtGui import QIcon, QAction

from .camera import CameraView
from .timer import Timer

class Application(QMainWindow):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Create components
        toolbar = ApplicationToolBar(parent=self)
        widget  = ApplicationWidget(parent=self)
        timer   = Timer(parent=self)

        # Position components
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, toolbar)
        self.setCentralWidget(widget)

        # Connect components
        widget.starttimer.connect(timer.begin)
        timer.step.connect(widget._captureImage)
        timer.end.connect(widget._endCapture)
        toolbar.generateImages.triggered.connect(widget._beginCapture)
        toolbar.selectDirectory.triggered.connect(widget._selectDirectory)
        toolbar.selectClassfile.triggered.connect(widget._selectClassfile)
        toolbar.resetApplication.triggered.connect(widget._resetApplication)

        # Show the application
        self.show()

class ApplicationToolBar(QToolBar):

    def __init__(self, **kwargs):
        super().__init__(**kwargs, floatable=False, movable=False)

        self.generateImages   = QAction(QIcon('./resources/icons/camera.png'), 'Generate', self)
        self.selectDirectory  = QAction(QIcon('./resources/icons/folder.png'), 'Select Directory', self)
        self.selectClassfile  = QAction(QIcon('./resources/icons/file.png'), 'Select Classfile', self)
        self.resetApplication = QAction(QIcon('./resources/icons/refresh.png'), 'Reset Application', self)

        self.addActions([self.generateImages, self.selectDirectory, self.selectClassfile, self.resetApplication])

class ApplicationWidget(QWidget):

    starttimer = pyqtSignal(int, int)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.feed      = CameraView(parent=self)
        self.directory = QLineEdit(parent=self, text=getcwd())
        self.directory.setReadOnly(True)
        self.classfile = QLineEdit(parent=self)
        self.classfile.setReadOnly(True)
        self.images    = QSpinBox(parent=self, minimum=1, maximum=100)
        self.rate      = QSpinBox(parent=self, minimum=1, maximum=100)
        self.label     = QLineEdit(parent=self)
        self.error     = QLabel(parent=self, text=' ')
        self.progress  = QProgressBar(parent=self, orientation=Qt.Orientation.Horizontal, enabled=False, value=0, minimum=0, maximum=100)

        form = QFormLayout()
        form.addRow(self.feed)
        form.addRow('Directory:', self.directory)
        form.addRow('Classfile:', self.classfile)
        form.addRow('Images:', self.images)
        form.addRow('Rate:', self.rate)
        form.addRow('Label:', self.label)
        form.addRow(self.error)
        form.addRow(self.progress)
        self.setLayout(form)

    # -- Slots ----------------------------------------------------------------

    def _beginCapture(self):
        dir    = self.directory.text()
        file   = self.classfile.text()
        images = self.images.value()
        rate   = self.rate.value()
        label  = self.label.text()

        error_msg = None
        if   len(dir) < 1     : error_msg = 'No directory provided'
        elif not isdir(dir)   : error_msg = 'Invalid directory provided'
        elif len(file) < 1    : error_msg = 'No classfile provided'
        elif not isfile(file) : error_msg = 'Invalid classfile provided'
        elif images < 1       : error_msg = 'Number of images must be greater than 0'
        elif rate < 1         : error_msg = 'Images per sec must be greater than 0'
        elif len(label) < 1   : error_msg = 'No label provided'

        if error_msg:
            self.error.setText(f'Error: {error_msg}')
            return
        else:
            self.error.setText(f' ')
            self.progress.setEnabled(True)
            self.progress.setValue(0)
            self.starttimer.emit(images, rate)

    def _captureImage(self, completion):
        self.progress.setValue(int(completion*100))
        print('Capture!')

    def _endCapture(self):
        print('Capture complete!')
        self.progress.setValue(0)
        self.progress.setEnabled(False)

    def _selectDirectory(self):
        dirname = QFileDialog.getExistingDirectoryUrl(parent=self).toLocalFile()
        if len(dirname) > 0: self.directory.setText(dirname)

    def _selectClassfile(self):
        filename = QFileDialog.getOpenFileUrl(parent=self, filter='CSV (*.csv)')[0].toLocalFile()
        if len(filename) > 0: self.classfile.setText(filename)

    def _resetApplication(self):
        self.directory.setText(getcwd())
        self.classfile.setText('')
        self.images.setValue(1)
        self.rate.setValue(1)
        self.label.setText('')
