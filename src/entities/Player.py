class Player:
    # Name, Position, Number
    def __init__(self, **kwargs):
        self.last_name = kwargs.get("last_name", "Last")
        self.first_name = kwargs.get("first_name", "First")
        self.position = kwargs.get("position", "Unknown")
        self.number = kwargs.get("number", 99)