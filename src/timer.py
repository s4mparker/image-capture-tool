from PyQt6.QtCore import QTimer, pyqtSignal

class Timer(QTimer):

    step    = pyqtSignal(float)
    end     = pyqtSignal()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.counter = 0
        self.target  = 0
        self.timeout.connect(self.iterate)

    def begin(self, n, rate=1):
        self.counter    = 0
        self.target     = n
        self.setInterval(int(1000 / rate))
        self.start()

    def iterate(self):
        if self.counter < self.target:
            self.counter +=1
            self.step.emit(float(self.counter / self.target))
        else:
            self.stop()
            self.end.emit()
