

"""
Global constants
"""
DEFAULT_ATTRIBUTE = 0.5
DEFAULT_VAR = 0.5
DEFAULT_NUMBER = 20
RIGHT_HANDED_PROB = 0.6
MAX_ITER = 5
MAX_PITCHES = 5
MAX_PLAYERS = 1000
MIN_ATTRIBUTE = 0.2
MAX_ATTRIBUTE = 0.99
MIN_NUMBER = 0
MAX_NUMBER = 99

"""
Attribute list
"""
PLAYER_ATTRIBUTES = ["player_id", "last_name", "first_name", "position", "number", "handedness"]
BATTER_NUMERICAL_ATTRIBUTES = ["contact_l", "power_l", "contact_r", "power_r", "zone_awareness", "patience", "speed", "fielding"]
PITCHER_NUMERICAL_ATTRIBUTES = ["stamina", "deception"]
PITCH_NUMERICAL_ATTRIBUTES = ["velocity", "control", "stuff"]