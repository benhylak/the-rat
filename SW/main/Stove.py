class Stove:
    def __init__(self):
        self.upper_right = Burner("upper_right")
        self.upper_left = Burner("upper_left")
        self.lower_left = Burner("lower_left")
        self.lower_right = Burner("lower_right")

    def get_burners(self):
        """
        Returns a list of the Burners in the Stove object
        :return: List of the burners
        """
        burners = []
        burners.append(self.upper_left)
        burners.append(self.upper_right)
        burners.append(self.lower_left)
        burners.append(self.lower_right)
        return burners

class Burner:
    def __init__(self, name):
        self.name = name
        self.on = False
        self.pot_detected = False
        self.boiling = False
        self.temp = 0.0
    
