from .config import DEFAULT_ATTRIBUTE

class Pitch:
    def __init__(self, **kwargs):
        self.pitch_name = kwargs.get("pitch_name", DEFAULT_ATTRIBUTE)
        self.velocity = kwargs.get("velocity", DEFAULT_ATTRIBUTE)
        self.stuff = kwargs.get("stuff", DEFAULT_ATTRIBUTE)
        self.control = kwargs.get("control", DEFAULT_ATTRIBUTE)