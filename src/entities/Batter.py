from .Player import Player

# globals
from .config import DEFAULT_ATTRIBUTE

class Batter(Player):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.power = kwargs.get("power", DEFAULT_ATTRIBUTE)
        self.contact = kwargs.get("contact", DEFAULT_ATTRIBUTE)
        self.zone_awareness = kwargs.get("zone_awareness", DEFAULT_ATTRIBUTE)
        self.patience = kwargs.get("patience", DEFAULT_ATTRIBUTE)
        self.speed = kwargs.get("speed", DEFAULT_ATTRIBUTE)
    
    def _getOverall(self):
        return round((self.power + self.contact + self.zone_awareness + self.patience + self.speed) / 5, 1)

    def display(self):
        print(f"{self.position} {self.first_name} {self.last_name} {self.number}")
        print(f"Attributes: {self._getOverall()}ovr {self.power}pwr {self.contact}cnt {self.zone_awareness}zna")
        print(f"{self.patience}ptn {self.speed}spd\n")


