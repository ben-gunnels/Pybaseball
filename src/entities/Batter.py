from .Player import Player

# globals
from .config import DEFAULT_ATTRIBUTE, BATTER_NUMERICAL_ATTRIBUTES

class Batter(Player):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.power_l = kwargs.get("power_l", DEFAULT_ATTRIBUTE)
        self.contact_l = kwargs.get("contact_l", DEFAULT_ATTRIBUTE)
        self.power_r = kwargs.get("power_r", DEFAULT_ATTRIBUTE)
        self.contact_r = kwargs.get("contact_r", DEFAULT_ATTRIBUTE)
        self.zone_awareness = kwargs.get("zone_awareness", DEFAULT_ATTRIBUTE)
        self.patience = kwargs.get("patience", DEFAULT_ATTRIBUTE)
        self.speed = kwargs.get("speed", DEFAULT_ATTRIBUTE)
        self.fielding = kwargs.get("fielding", DEFAULT_ATTRIBUTE)
    
    def _get_overall(self):
        return round(sum([getattr(self, attr) for attr in BATTER_NUMERICAL_ATTRIBUTES]) / len(BATTER_NUMERICAL_ATTRIBUTES), 2)
    
    def _get_mean(self, *args):
        total = 0
        for arg in args:
            total += arg
        return round(total / len(args), 2)

    def display(self):
        print(f"{self.handedness} {self._translatePosition()} {self.first_name} {self.last_name} {self.number}")
        print(f"Attributes: {self._get_overall()}ovr {self._get_mean(self.power_l, self.power_r)}pwr {self._get_mean(self.contact_l, self.contact_r)}cnt {self.zone_awareness}zna")
        print(f"{self.patience}ptn {self.speed}spd\n")


