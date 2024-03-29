from PyQt6.QtCore import QTimer, pyqtSignal

class Timer(QTimer):

    step     = pyqtSignal(float, int)
    complete = pyqtSignal()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.counter = 0
        self.target  = 0
        self.timeout.connect(self.slot_iterate)

    def begin(self, n, rate):
        self.counter    = 0
        self.target     = n
        self.setInterval(int(1000 / rate))
        self.start()

    def slot_iterate(self):
        if self.counter < self.target:
            self.counter +=1
            self.step.emit(float(self.counter / self.target), self.counter)
        else:
            self.end()

    def end(self):
        self.stop()
        self.complete.emit()
