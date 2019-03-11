import Stove
import numpy as np
import random
from moving_average import MovingAverage

class BurnerOnDetector:
    def __init__(self):
        self.main_iteration = 0  #iteration in the main file
        self.SAMPLE_TIME = 10 #record a sample every 20 iterations
        self.MAX_SAMPLES = 6 #the number of samples in the array
        self.MIN_TEMP = 30 #minimum temperature to consider burner on
        
        #create a moving average list for each burner
        self.moving_average_ur = MovingAverage(self.MAX_SAMPLES)
        self.moving_average_ul = MovingAverage(self.MAX_SAMPLES)
        self.moving_average_ll = MovingAverage(self.MAX_SAMPLES)
        self.moving_average_lr = MovingAverage(self.MAX_SAMPLES)
                
    def decreasing_temp(self, temp, moving_average):
        decreasing = []
        if (self.main_iteration % self.SAMPLE_TIME == 0):
            decreasing = moving_average.process(temp)
            if len(decreasing) == self.MAX_SAMPLES:
                dx = np.diff(decreasing)
                return np.all(dx <= 0)
        self.main_iteration += 1        
            
    def burner_on(self, burner, moving_average):
        if (burner.temp != 0 and burner.temp > self.MIN_TEMP):
            off = self.decreasing_temp(burner.temp, moving_average)
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
