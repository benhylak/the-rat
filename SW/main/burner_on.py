import Stove
import numpy as np
import random
from moving_average import MovingAverage

class BurnerOnDetector:
    def __init__(self):
        self.i = 0  #iteration time passed
        self.sample_time = 10 #record a sample every 20 iterations
        self.max_samples = 6 #the number of samples in the array
        self.max_time = 200
        self.moving_average_ur = MovingAverage(self.max_samples)
        self.moving_average_ul = MovingAverage(self.max_samples)
        self.moving_average_ll = MovingAverage(self.max_samples)
        self.moving_average_lr = MovingAverage(self.max_samples)
        self.min_temp = 20 #minimum temperature to consider burner on
        
    def decreasing_temp(self, temp, moving_average):
        decreasing = []
        if (self.i % self.sample_time == 0):
            decreasing = moving_average.process(temp)
            if len(decreasing) == self.max_samples:
                dx = np.diff(decreasing)
                return np.all(dx <= 0)
        self.i += 1        
            
    def burner_on(self, burner, moving_average):
        if (burner.temp != 0 and burner.temp > self.min_temp):
            off = self.decreasing_temp(burner.temp, moving_average)
            print("burner", off)
            if burner.pot_detected == False:
                if off == False:
                    burner.on = True
                else:
                    burner.on = False
            else:
                burner.on = False
        else:
            burner.on = False

    def update(self, stove):
        self.burner_on(stove.upper_right, self.moving_average_ur)
        self.burner_on(stove.upper_left, self.moving_average_ul)
        self.burner_on(stove.lower_left, self.moving_average_ll)
        self.burner_on(stove.lower_right, self.moving_average_lr)
