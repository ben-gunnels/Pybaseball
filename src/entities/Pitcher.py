from .Player import Player
# globals
from .config import DEFAULT_ATTRIBUTE

class Pitcher(Player):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.pitches = kwargs.get("pitches", [])
        
        self.deception = kwargs.get("deception", DEFAULT_ATTRIBUTE)
        self.stamina = kwargs.get("stamina", DEFAULT_ATTRIBUTE)

    
    def _getOverall(self):
        pitch_val = 0
        pitch_traits = 0
        for pitch in self.pitches:
            pitch_val += pitch.velocity + pitch.control + pitch.stuff
            pitch_traits += 3
        return round((self.deception + self.stamina + pitch_val) / (2 + pitch_traits), 1)

    def display(self):
        print(f"{self.position} {self.first_name} {self.last_name} {self.number}")
        print(f"Attributes: {self._getOverall()}ovr {self.deception}dec {self.stamina}sta\n")
