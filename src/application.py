from .camera import CameraView
from .timer import Timer
from .transforms import *

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow
from os import listdir, remove, getcwd
from os.path import exists, isfile, isdir
from sys import exit

import PyQt6.QtWidgets as qt

class Interface(qt.QWidget):

    def __init__(self, app, **kwargs):
        """ 
        Create a new Interface object

        Parameters:
            app     : the application the interface lives within
            kwargs  : keyword arguments passed to the QWidget super-constructor
        """

        super().__init__(**kwargs)

        self.app = app
        self.labels_file = None

        self.createWidgets()
        self.setWidgets()
        self.positionWidgets()
        self.connectWidgets()

        self.slot_reset_clicked()

    def createWidgets(self):
        """ 
        Create the widgets required to construct the user interface
        """

        self.camera         = CameraView(parent=self)
        self.timer          = Timer(parent=self)

        self.instructions   = qt.QLabel(parent=self)

        self.images         = qt.QSpinBox(parent=self)
        self.refresh        = qt.QSpinBox(parent=self)
        self.classname      = qt.QLineEdit(parent=self)
        self.directory      = qt.QLineEdit(parent=self)
        self.labels         = qt.QLineEdit(parent=self)
        self.format         = qt.QComboBox(parent=self)
        self.filter         = qt.QComboBox(parent=self)
        self.blur           = qt.QSlider(orientation=Qt.Orientation.Horizontal, parent=self)

        self.generate       = qt.QPushButton(parent=self)
        self.progress       = qt.QProgressBar(parent=self)

    def setWidgets(self):
        """  
        Set the initial parameters of the user interface's widgets
        """

        self.instructions.setText('Add instructions here')
        self.instructions.setWordWrap(True)

        self.images.setRange(1, 500)
        self.refresh.setRange(1, 100)
        self.directory.setReadOnly(True)
        self.labels.setReadOnly(True)
        for (text, extension) in [('JPG (.jpg)', 'jpg'), ('PNG (.png)', 'png')]:
            self.format.addItem(text, extension)
        for (text, filter) in [('None', None), ('Greyscale', greyscale), ('Red', red), ('Green', green), ('Blue', blue), ('Corners (Canny)', canny)]:
            self.filter.addItem(text, filter)
        self.blur.setRange(0, 500)

        self.generate.setText('Generate Images')
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setDisabled(True)

    def positionWidgets(self):
        """ 
        Position the widgets within the user interface 
        """

        main = qt.QHBoxLayout()

        controls = qt.QVBoxLayout()
        controls.addWidget(self.instructions)

        form = qt.QFormLayout()
        form.addRow('Images (#)', self.images)
        form.addRow('Refresh Rate (#/sec)', self.refresh)
        form.addRow('Class Name', self.classname)
        form.addRow('Directory', self.directory)
        form.addRow('Labels File', self.labels)
        form.addRow('Format/Extension', self.format)
        form.addRow('Filter', self.filter)
        form.addRow('Blur', self.blur)
        form.addRow(self.generate)
        form.addRow(self.progress)

        controls.addLayout(form)
        controls.addStretch(10)

        main.addLayout(controls)
        main.addWidget(self.camera)

        self.setLayout(main)

    def connectWidgets(self):
        """  
        Connect the widgets' slots/signals together
        """

        self.filter.currentIndexChanged.connect(self.slot_filter_changed)
        self.blur.valueChanged.connect(self.slot_blur_changed)
        self.generate.clicked.connect(self.slot_generate_clicked)

        menu = self.app.menuBar()
        file = menu.addMenu('File')
        file.addAction('Clear', self.slot_clear_clicked)
        file.addAction('Reset', self.slot_reset_clicked)

        menu.addAction('Select Directory', self.slot_select_directory_clicked)
        menu.addAction('Select Labels', self.slot_select_labels_clicked)

# --- Slots -------------------------------------------------------------------------------------------------

    def slot_generate_clicked(self):
        """  
        Triggered when the generate button is clicked
        """

        self.labels_file = open(self.labels.text(), 'a')
        self.progress.setDisabled(False)
        self.progress.setValue(0)
        self.timer.run(self.slot_capture_image, self.images.value(), self.refresh.value(), end=self.slot_generate_complete)
    def slot_generate_complete(self):
        """  
        Triggered when all required images have been captured
        """

        self.labels_file.close()
        self.progress.setValue(0)
        self.progress.setDisabled(True)
    def slot_capture_image(self):
        """ 
        Triggered when a new image needs to be captured & saved 
        """

        image = self.camera.get_image()
        path = f'{self.directory.text()}/image_{self.timer.get_completed()}.{self.format.currentData()}'

        if exists(path):
            print(f'Duplicate: {path}')
        else:
            response = image.save(path)
            if response:
                self.labels_file.write(f'image_{self.timer.get_completed()}.{self.format.currentData()},{self.classname.text()}\n')
                print(f'Saved: {path}')
            else:
                print(f'Unknown: {path}')

        self.progress.setValue(self.timer.get_completion())
    def slot_filter_changed(self):
        """ 
        Triggered when the filter is changed 
        """

        self.camera.set_filter(self.filter.currentData())
    def slot_blur_changed(self):
        """  
        Triggered when the blur is changed
        """

        self.camera.set_blur(int(self.blur.value() / 100))
    def slot_clear_clicked(self):
        """  
        Triggered when the clear button (in the menu) is clicked
        """

        # root = f'{self.directory.text()}/'

        # for file in [f for f in listdir(root) if isfile(root+f)]:
        #     path = root + file
        #     if any([file.find(e) != -1 for e in self.extensions]):
        #         remove(path)
        #         print(f'Removed: {path}')

        pass
    def slot_reset_clicked(self):
        """  
        Triggered when the reset button (in the menu) is clicked
        """

        self.images.setValue(10)
        self.refresh.setValue(100)
        self.directory.setText(getcwd())
        self.labels.setText(f'{getcwd()}/labels.csv')
        self.classname.setText('')
    def slot_select_directory_clicked(self):
        """  
        Triggered when the select directory button (in the menu) is clicked
        """

        dir = qt.QFileDialog.getExistingDirectoryUrl(parent=self, options=qt.QFileDialog.Option.DontUseNativeDialog).toLocalFile()
        if len(dir) > 0:
            self.directory.setText(dir)
    def slot_select_labels_clicked(self):
        """  
        Triggered when the select labels button (in the menu) is clicked
        """
        
        file = qt.QFileDialog.getOpenFileUrl(parent=self, filter='All (*.csv)' , options=qt.QFileDialog.Option.DontUseNativeDialog)[0].toLocalFile()
        if len(file) > 0:
            self.labels.setText(file)

class Application(qt.QMainWindow):

    def __init__(self, **kwargs):
        """  
        Create a new Application object

        Parameters:
            kwargs  : keyword arguments passed to the QMainWindow super-constructor
        """

        qt_app = qt.QApplication([])
        super().__init__(**kwargs)

        self.setWindowTitle('Image Capture Tool')
        self.setFixedWidth(1200)
        interface = Interface(app=self)
        self.setCentralWidget(interface)

        self.show()
        exit(qt_app.exec())