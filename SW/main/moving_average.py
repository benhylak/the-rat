class MovingAverage:
    def __init__(self, window_size):
        self.window_size = window_size
        self.values = []

    def process(self, value):
        self.values.append(value)
        if len(self.values) > self.window_size:
            self.values.pop(0)
        return self.values
