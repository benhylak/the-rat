import Stove
import numpy as np

class BurnerOn:
    def __init__(self):
        self.i = 0
        self.decreasing = []
        self.off = True
        
    def decreasing_temp(self, average):
        while self.i < 360:
            if (self.i % 30 == 0):
                self.decreasing.append(average)
            self.i += 1
            break

        if len(self.decreasing) == 12:
            dx = np.diff(self.decreasing)
            self.i = 0
            self.decreasing = []
            self.off = np.all(dx <= 0)
            return np.all(dx <= 0)
        else:
            return None

    def update(self, stove):
        if (stove.upper_right.temp != 0):
            self.decreasing_temp(stove.upper_right.temp)
            upper_right_on = self.off
            if stove.upper_right.pot_detected == False:
                if upper_right_on == False:
                    stove.upper_right.on = True
                else:
                    stove.upper_right.on = False
            else:
                stove.upper_right.on = False
        else:
            stove.upper_right.on = False
            
        if (stove.upper_left.temp !=0):
            self.decreasing_temp(stove.upper_left.temp)
            upper_left_on = self.off
            if stove.upper_left.pot_detected == False:
                if upper_left_on == False:
                    stove.upper_left.on = True
                else:
                    stove.upper_left.on = False
            else:
                stove.upper_left.on = False
        else:
            stove.upper_left.on = False

        if (stove.lower_left.temp != 0):
            self.decreasing_temp(stove.lower_left.temp)
            lower_left_on = self.off
            if stove.lower_left.pot_detected == False:
                if lower_left_on == False:
                    stove.lower_left.on = True
                else:
                    stove.lower_left.on = False
            else:
                stove.lower_left.on = False
        else:
            stove.lower_left.on = False
            
        if (stove.lower_right.temp !=0):
            self.decreasing_temp(stove.lower_right.temp)
            lower_right_on = self.off
            if stove.lower_right.pot_detected == False:
                if lower_right_on == False:
                    stove.lower_right.on = True
                else:
                    stove.lower_right.on = False
            else:
                stove.lower_right.on = False
        else:
            stove.lower_right.on = False
            
