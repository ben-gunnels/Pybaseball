
import random

class Event:
    def __init__(self, event, probabilities, disp=""):
        self.event = event
        self.disp = disp
        self.probabilities = probabilities
    
    def display(self):
        print(self.disp)

    def generate_outcome(self): # Partitions outcomes by probability
        r = random.random()
        for i in range(len(self.probabilities)):
            if (r < self.probabilities[i]):
                return i
        return len(self.probabilities)