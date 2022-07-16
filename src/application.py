from os import getcwd
from os.path import exists
from enum import Enum
from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from PyQt6.QtWidgets import QMainWindow, QWidget, QPushButton, QSpinBox, QLabel, QLineEdit, QFormLayout, QFileDialog, QProgressBar, QComboBox, QCheckBox, QGridLayout

from .camera import CameraView
from .timer import Timer

class FilenameFormats(Enum):
    Label = 0
    Datetime = 1
    LabelAndDatetime = 2
    
class Application(QMainWindow):

    # File extensions - not sure jpg works
    extensions_options = [('jpg', 'jpg'), ('jpeg', 'jpeg'), ('png', 'png')]

    # Filename formats
    filename_options = [('plain', None), ('label', FilenameFormats.Label), ('datetime', FilenameFormats.Datetime), ('label & datetime', FilenameFormats.LabelAndDatetime)]

    # Directory & classfile paths
    directory    = None
    classfile    = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create central widget
        self.root = QWidget(parent=self)
        self.setCentralWidget(self.root)

        # Create capture timer
        self.timer = Timer(parent=self)

        # Create, position and connect components
        self.construct_components()
        self.position_components()
        self.connect_components()

        # Present application to user
        self.show()

    def construct_components(self):
        self.feed              = CameraView()
        self.images            = QSpinBox(parent=self, minimum=1, maximum=500)
        self.rate              = QSpinBox(parent=self, minimum=1, maximum=100, value=50)
        self.label             = QLineEdit(parent=self)
        self.generate          = QPushButton(parent=self, text='Generate')
        self.reset             = QPushButton(parent=self, text='Reset')
        self.error             = QLabel(parent=self, text=' ')
        self.progress          = QProgressBar(parent=self, minimum=0, maximum=100, enabled=False, value=0)
        self.extension         = QComboBox(parent=self)
        for (text, extension) in self.extensions_options: self.extension.addItem(text, extension)
        self.filename_format   = QComboBox(parent=self)
        for (text, format) in self.filename_options: self.filename_format.addItem(text, format)
        self.ignore_duplicates = QCheckBox(parent=self, text='Ignore filename duplication?')

    def position_components(self):
        grid = QGridLayout()
        self.root.setLayout(grid)

        grid.addWidget(self.feed, 0, 0, 1, 4)
        grid.addWidget(QLabel(parent=self, text='Label:'), 1, 0)
        grid.addWidget(self.label, 1, 1)
        grid.addWidget(QLabel(parent=self, text='Images (#):'), 1, 2)
        grid.addWidget(self.images, 1, 3)
        grid.addWidget(QLabel(parent=self, text='File Extension:'), 2, 0)
        grid.addWidget(self.extension, 2, 1)
        grid.addWidget(QLabel(parent=self, text='Rate (p/s):'), 2, 2)
        grid.addWidget(self.rate, 2, 3)
        grid.addWidget(QLabel(parent=self, text='Filename Format:'), 3, 0)
        grid.addWidget(self.filename_format, 3, 1)
        grid.addWidget(self.ignore_duplicates, 3, 2, 1, 2)
        grid.addWidget(self.generate, 4, 0, 1, 2)
        grid.addWidget(self.reset, 4, 2, 1, 2)
        grid.addWidget(self.progress, 5, 0, 1, 4)
        grid.addWidget(self.error, 6, 0, 1, 4)

        for i in range(grid.columnCount()):
            if i % 2 == 0:
                grid.setColumnStretch(i, 1)
            else:
                grid.setColumnStretch(i, 2)

    def connect_components(self):
        self.generate.clicked.connect(self.slot_begin_generation)
        self.reset.clicked.connect(self.slot_reset_components)
        self.timer.step.connect(self.slot_capture_image)
        self.timer.complete.connect(self.slot_end_generation)

    # -- Slots ------------------------------------------------------------

    def slot_begin_generation(self):
        # Basic input validation
        if len(self.label.text()) < 1:
            self.slot_render_error('No label provided')
            return
        else:
            self.slot_render_error(None)

        # Request directory & classfile
        self.directory = self.request_directory()
        if not self.directory:
            self.slot_render_error('Failed to select a directory')
            return
        self.classfile = self.request_classfile()
        if not self.classfile:
            self.slot_render_error('Failed to select a classfile')
            return

        # Begin image generation
        self.progress.setEnabled(True)
        self.progress.setValue(0)
        self.timer.begin(self.images.value(), self.rate.value())

    def slot_capture_image(self, completion, id):
        # Calculate filename & file path
        filename = f'{id}'
        selected_format = self.filename_format.currentData()
        selected_extension = self.extension.currentData()
        if selected_format == FilenameFormats.Label:
            filename += f'_{self.label.text()}'
        elif selected_format == FilenameFormats.Datetime:
            filename += f'_{datetime.now().strftime("%d:%m:%Y-%H:%M:%S:%f")}'
        elif selected_format == FilenameFormats.LabelAndDatetime:
            filename += f'_{self.label.text()}_{datetime.now().strftime("%d:%m:%Y-%H:%M:%S:%f")}'

        # Determine (if required) whether the file already exists
        if exists(f'{self.directory}/{filename}.{selected_extension}'):
            if not self.ignore_duplicates.isChecked():
                self.timer.end()
                self.slot_render_error(f'Found a duplicated filename ({filename}.{selected_extension})')        
            return

        # Otherwise save the image and update the classfile
        response = self.feed.get().save(f'{self.directory}/{filename}.{selected_extension}', selected_extension)
        if not response:
            self.timer.end()
            self.slot_render_error(f'Unknown error on ({filename}.{selected_extension})')
            return
        with open(self.classfile, mode='a') as file:
            file.write(f'{filename}.{selected_extension},{self.label.text()}\n')
        
        # Update progress bar
        self.progress.setValue(int(completion*100))

        print(f'{self.directory}/{filename}.{selected_extension}')

    def slot_end_generation(self):
        # End image generation
        self.progress.setValue(0)
        self.progress.setEnabled(False)
        self.directory = None
        self.classfile = None

    def slot_render_error(self, error):
        if error:
            self.error.setText(f'Error: {error}')
        else:
            self.error.setText(f' ')

    def slot_reset_components(self):
        self.label.setText('')
        self.images.setValue(1)
        self.rate.setValue(50)
        self.extension.setCurrentIndex(0)
        self.filename_format.setCurrentIndex(0)
        self.error.setText(f' ')
        self.timer.end()

    # -- Utility functions ------------------------------------------------

    def request_directory(self):
        selected = QFileDialog.getExistingDirectoryUrl(parent=self, caption='Select a directory', directory=QUrl(f'{getcwd()}/'))
        directory = selected.toLocalFile()
        if len(directory) < 1: return None
        else: return directory

    def request_classfile(self):
        selected = QFileDialog.getSaveFileUrl(parent=self, caption='Select a classfile', directory=QUrl(f'{getcwd()}/'), filter='CSV (*.csv)', options=QFileDialog.Option.DontConfirmOverwrite)
        classfile = selected[0].toLocalFile()
        if len(classfile) < 1: return None
        else: return classfile
