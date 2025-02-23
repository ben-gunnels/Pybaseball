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
        self.overall = self.calc_overall()
    
    def calc_overall(self):
        return round(sum([getattr(self, attr) for attr in BATTER_NUMERICAL_ATTRIBUTES]) / len(BATTER_NUMERICAL_ATTRIBUTES), 2)
    
    def _get_mean(self, *args):
        total = 0
        for arg in args:
            total += arg
        return round(total / len(args), 2)

    def display(self):
        print(f"{self.handedness} {self.translate_position()} {self.first_name} {self.last_name} {self.number}")
        print(f"Attributes: {int(self.overall * 100)}ovr {int(self._get_mean(self.power_l, self.power_r)*100)}pwr {int(self._get_mean(self.contact_l, self.contact_r)*100)}cnt {int(self.zone_awareness*100)}zna")
        print(f"{int(self.patience*100)}ptn {int(self.speed*100)}spd\n")


