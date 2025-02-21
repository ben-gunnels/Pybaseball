from .Player import Player
# globals
from .config import DEFAULT_ATTRIBUTE

class Pitcher(Player):
    energy = 1 # Should decrease over the course of the game
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.pitches = kwargs.get("pitches", [])
        
        self.deception = kwargs.get("deception", DEFAULT_ATTRIBUTE)
        self.stamina = kwargs.get("stamina", DEFAULT_ATTRIBUTE)
        self._calc_overall()

    def _calc_overall(self):
        pitch_val = 0
        pitch_traits = 0
        for pitch in self.pitches:
            pitch_val += pitch.velocity + pitch.control + pitch.stuff
            pitch_traits += 3
        self.overall = round((self.deception + self.stamina + pitch_val) / (2 + pitch_traits), 2)
    
    def _get_pitch_traits(self, trait):
        total = 0
        for pitch in self.pitches:
            total += getattr(pitch, trait)
        return round(total / len(self.pitches), 2)

    def display(self):
        print(f"{self.handedness} {self._translatePosition()} {self.first_name} {self.last_name} {self.number}")
        print(f"Attributes: {self.overall}ovr {self.deception}dec {self.stamina}sta")
        print(f"{self._get_pitch_traits('velocity')}velo {self._get_pitch_traits('control')}ctrl {self._get_pitch_traits('stuff')}stf\n")
