import json

class Sliders:
    def __init__(self):
        with open("settings.json", "r") as file:
            _slider_data = json.load(file)
        for k in _slider_data.keys():
            for p, v in _slider_data[k].items():
                setattr(self, p, v)
        
