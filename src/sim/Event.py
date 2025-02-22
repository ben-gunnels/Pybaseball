import random

class Event:
    def __init__(self, event, probabilities, data_tables, verbose=True, disp=""):
        self.event = event
        self.disp = disp
        self.probabilities = probabilities
        self.verbose = verbose
        self._add_to_tables(data_tables)
    
    def display(self):
        if self.verbose:
            print(self.disp)

    def generate_outcome(self): # Partitions outcomes by probability
        r = random.random()
        for i in range(len(self.probabilities)):
            if (r < self.probabilities[i]):
                return i
        return len(self.probabilities)
    
    def _add_to_tables(self, data):
        if len(data)==0:
            return 
        for table in data:
            table[self.event] = table.get(self.event, 0) + 1