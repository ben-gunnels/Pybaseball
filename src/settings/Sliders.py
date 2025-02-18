import json
from .BatterEvents import BatterEvents
from .PitcherEvents import PitcherEvents
from .InPlayEvents import InPlayEvents

class Sliders:
    def __init__(self):
        self.batter_events = BatterEvents()
        self.pitcher_events = PitcherEvents()
        self.in_play_events = InPlayEvents()
        
        with open("src\settings\settings.json", "r") as file:
            _slider_data = json.load(file)
        
        # Initialize setting attributes based on slider settings
        for k in _slider_data.keys():
            for p, v in _slider_data[k].items():
                if (k == "batter_events"):
                    setattr(self.batter_events, p, v)
                elif (k == "pitcher_events"):
                    setattr(self.pitcher_events, p, v)
                elif (k == "in_play_events"):
                    setattr(self.in_play_events, p, v)
            
        
