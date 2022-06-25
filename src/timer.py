from PyQt6.QtCore import QTimer

class Timer(QTimer):

    def __init__(self, **kwargs):
        # Call the super constructor
        super().__init__(**kwargs)

        # Create variables that will be used during timer execution
        self.func       = None
        self.end        = None
        self.completed  = 0
        self.target     = 0

        # Connect the timer to it's own callback
        self.timeout.connect(self.slot_timeout)

    def run(self, func, n, rate, end=None):
        # Assign parameters to variables
        self.func       = func
        self.end        = end
        self.completed  = 0
        self.target     = n

        # Set the timer's refresh rate
        self.setInterval(int(1000 / rate))

        # Begin the timer
        self.start()

    def get_completed(self):
        return self.completed

    def get_completion(self):
        # Calculate the timer completion (%)
        completion = int(self.completed / self.target * 100)

        # Bounds checking
        if completion < 0:
            completion = 0
        elif completion > 100:
            completion = 100
        
        return completion

    def slot_timeout(self):
        # Check if the function should be called again
        if self.completed < self.target:
            self.completed += 1
            if self.func:
                self.func()
        else:
            self.stop()
            if self.end:
                self.end()