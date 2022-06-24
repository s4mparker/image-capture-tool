import PyQt6.QtWidgets as qt
from camera import CameraView
from timer import Timer

from os import listdir, remove, getcwd
from os.path import exists, isfile
from sys import exit

class Window(qt.QWidget):

    extensions = {'.jpg', 'png', 'jpeg'}

    def __init__(self, **kwargs):
        """
        Create a new Window object
        
        Parameters:
            kwargs  : keyword arguments to be passed to the QWidget super-constructor        
        """

        super().__init__(**kwargs)
        self.setWindowTitle('Image Capture Tool')

        self.create_widgets()
        self.position_widgets()
        self.connect_widgets()

    def create_widgets(self):
        """ Create the induvidual widgets to be used by the Window object """

        # Camera feed used the display and access the device's webcam
        self.feed               = CameraView(parent=self, imageScale=1.5)

        # Timer used to regularly capture and save images
        self.captureTimer       = Timer(parent=self)

        # Number of images to capture
        self.imageCounter       = qt.QSpinBox(parent=self)
        self.imageCounter.setRange(1, 500)

        # Number of images to capture per second
        self.refreshRate        = qt.QSpinBox(parent=self)
        self.refreshRate.setRange(1, 100)
        self.refreshRate.setValue(100)

        # Directory to store the produced images in
        self.targetDirectory    = qt.QLineEdit(parent=self)
        self.targetDirectory.setText(getcwd())
        self.targetDirectory.setReadOnly(True)

        # CSV file to store the associated image labels in
        self.targetLabels       = qt.QLineEdit(parent=self)
        self.targetLabels.setText('Please select...')
        self.targetLabels.setReadOnly(True)

        # Submit button to begin execution
        self.submitButton       = qt.QPushButton(parent=self)
        self.submitButton.setText('Submit')

        # Clear button to remove all images from the target directory
        self.clearDirectory     = qt.QPushButton(parent=self)
        self.clearDirectory.setText('Clear Directory')

        # Set the target directory to be the current working directory
        self.setCwd             = qt.QPushButton(parent=self)
        self.setCwd.setText('Set Working Directory')

        # Change the target directory
        self.selectDirectory    = qt.QPushButton(parent=self)
        self.selectDirectory.setText('Select Directory')

        # Change the labels CSV file
        self.selectLabels       = qt.QPushButton(parent=self)
        self.selectLabels.setText('Select Labels File')

        # Progress bar to show capture progress to the user
        self.progressBar        = qt.QProgressBar(parent=self)
        self.progressBar.setRange(0, 100)
        self.progressBar.setDisabled(True)

    def position_widgets(self):
        """ Position the created widgets within the Window object """

        layout = qt.QVBoxLayout()
        controls = qt.QHBoxLayout()
        form_left = qt.QFormLayout()
        form_right = qt.QFormLayout()

        form_left.addRow('Images', self.imageCounter)
        form_left.addRow('Refresh Rate', self.refreshRate)
        form_left.addRow('Directory', self.targetDirectory)
        form_left.addRow('Label File', self.targetLabels)
        form_left.addRow(self.submitButton)

        form_right.addWidget(self.clearDirectory)
        form_right.addWidget(self.setCwd)
        form_right.addWidget(self.selectDirectory)
        form_right.addWidget(self.selectLabels)
        form_right.addWidget(self.progressBar)

        controls.addLayout(form_left)
        controls.addLayout(form_right)
        layout.addWidget(self.feed)
        layout.addLayout(controls)
        self.setLayout(layout)

    def connect_widgets(self):
        """ Connect the Window object's widgets together to produce the desired functionality """

        self.submitButton.clicked.connect(self.slot_begin)
        self.clearDirectory.clicked.connect(self.slot_clear_directory)
        self.setCwd.clicked.connect(self.slot_set_cwd)
        self.selectDirectory.clicked.connect(self.slot_select_directory)
        self.selectLabels.clicked.connect(self.slot_select_labels_file)
        
    def capture(self):
        """ Capture a single image and save it to the target directory with the associated label """

        image = self.feed.get_image()
        path = f'{self.targetDirectory.text()}/image_{self.captureTimer.get_completed()}.jpg'

        if exists(path):
            print(f'Duplicate: {path}')
        else:
            response = image.save(path)
            if response:
                print(f'Saved: {path}')
            else:
                print(f'Unknown: {path}')

        self.progressBar.setValue(self.captureTimer.get_completion())

# -- Slots --

    def slot_begin(self):
        self.progressBar.setDisabled(False)
        self.progressBar.setValue(0)
        self.captureTimer.run(self.capture, self.imageCounter.value(), self.refreshRate.value(), end=self.slot_end)

    def slot_end(self):
        self.progressBar.setValue(0)
        self.progressBar.setDisabled(True)

    def slot_clear_directory(self):
        root = f'{self.targetDirectory.text()}/'

        for file in [f for f in listdir(root) if isfile(root+f)]:
            path = root + file
            if any([file.find(e) != -1 for e in self.extensions]):
                remove(path)
                print(f'Removed: {path}')

    def slot_set_cwd(self):
        self.targetDirectory.setText(getcwd())
        
    def slot_select_directory(self):
        dir = qt.QFileDialog.getExistingDirectoryUrl(parent=self, options=qt.QFileDialog.Option.DontUseNativeDialog).toLocalFile()
        if len(dir) > 0:
            self.targetDirectory.setText(dir)

    def slot_select_labels_file(self):
        file = qt.QFileDialog.getOpenFileUrl(parent=self, options=qt.QFileDialog.Option.DontUseNativeDialog)[0].toLocalFile()
        if len(file) > 0:
            self.targetLabels.setText(file)

if __name__ == '__main__':
    app = qt.QApplication([])
    window = Window()
    window.show()
    exit(app.exec())