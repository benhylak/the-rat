import Stove
import numpy as np

class BurnerOnDetector:
    def __init__(self):
        self.i = 0  #iteration time passed
        self.decreasing = []
        self.off = True
        self.max_time = 200 #number of iterations passed
        self.sample_time = 20 #record a sample every 20 iterations
        self.max_samples = 10 #the number of samples in the array
        self.min_temp = 35 #minimum temperature to consider burner on
        
    def decreasing_temp(self, temp):
        while self.i < self.max_time:
            if (self.i % self.sample_time == 0):
                self.decreasing.append(temp)
            self.i += 1
            break

        if len(self.decreasing) == self.max_samples:
            dx = np.diff(self.decreasing)
            self.i = 0
            self.decreasing = []
            self.off = np.all(dx <= 0)
            return np.all(dx <= 0)
        else:
            return None
            
    def burner_on(self, burner):
        if (burner.temp != 0 and burner.temp > self.min_temp):
            self.decreasing_temp(burner.temp)
            off = self.off
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
        self.burner_on(stove.upper_right)
        self.burner_on(stove.upper_left)
        self.burner_on(stove.lower_left)
        self.burner_on(stove.lower_right)
