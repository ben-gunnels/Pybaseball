class Player:
    # Name, Position, Number
    def __init__(self, **kwargs):
        self.player_id = kwargs.get("player_id", -1)
        self.last_name = kwargs.get("last_name", "Last")
        self.first_name = kwargs.get("first_name", "First")
        self.position = kwargs.get("position", 0)
        self.number = kwargs.get("number", 99)
        self.handedness = kwargs.get("handedness", "RH")

    def translate_position(self):
        translation_table = {
            0: "DH",
            1: "P",
            2: "C",
            3: "1B",
            4: "2B",
            5: "3B",
            6: "SS",
            7: "LF",
            8: "CF",
            9: "RF",
        }

        return translation_table[self.position]