import random
from .Batter import Batter
from .Pitcher import Pitcher
from .Pitch import Pitch
from ..prob.NDist import NDist
from .config import (DEFAULT_ATTRIBUTE, DEFAULT_VAR, MAX_PITCHES, MAX_PLAYERS, MAX_ITER, 
                     PLAYER_ATTRIBUTES, BATTER_NUMERICAL_ATTRIBUTES, PITCHER_NUMERICAL_ATTRIBUTES, 
                     PITCH_NUMERICAL_ATTRIBUTES, RIGHT_HANDED_PROB, DEFAULT_NUMBER, 
                     MAX_ATTRIBUTE, MIN_ATTRIBUTE, MIN_NUMBER, MAX_NUMBER)
from .static.Names import FIRST_NAMES, LAST_NAMES
from .static.PitchTypes import PITCH_TYPES
# Set up the distribution for attribute randomization
attribute_dist = NDist(DEFAULT_ATTRIBUTE, DEFAULT_VAR)

def generate_batter(i):
    batter = {attr: "" for attr in PLAYER_ATTRIBUTES + BATTER_NUMERICAL_ATTRIBUTES}
    batter["position"] = i  
    return batter

def generate_pitcher():
    pitcher = {attr: "" for attr in PLAYER_ATTRIBUTES + PITCHER_NUMERICAL_ATTRIBUTES}
    pitcher["pitches"] = []
    pitcher["position"] = 1
    # Randomize the pitchers pitch selection
    pitch_idxs = _generate_random_pitches()
    for idx in list(pitch_idxs):
        pitcher["pitches"].append(Pitch(**PITCH_TYPES[idx]))
    return pitcher
    
def randomize_player(player, ids_taken, numbers_taken):
    """Assigns random values to last_name, first_name, and number."""
    id_X = random.randrange(1, MAX_PLAYERS)
    while (id_X in ids_taken):
        id_X = random.randrange(1, MAX_PLAYERS)
    player["player_id"] = id_X
    # Keep track of ids taken 
    ids_taken.add(id_X)
    player["first_name"] = random.choice(FIRST_NAMES)
    player["last_name"] = random.choice(LAST_NAMES)
    player["handedness"] = "RH" if random.random() < RIGHT_HANDED_PROB else "LH"
    number_dist = NDist(DEFAULT_NUMBER, 20)
    number = int(number_dist.calculate_random_percentile(mn=MIN_NUMBER, mx=MAX_NUMBER, rnd=0, mode="skew"))
    while (number in numbers_taken):
        number = int(number_dist.calculate_random_percentile(mn=MIN_NUMBER, mx=MAX_NUMBER, rnd=0, mode="skew"))  # Assigning random jersey number
    player["number"] = number
    # Keep track of the numbers that are taken for a team
    numbers_taken.add(number)
    return player

def generate_batter_attributes(batter):
    for attr in BATTER_NUMERICAL_ATTRIBUTES:
        batter[attr] = attribute_dist.calculate_random_percentile(mn=MIN_ATTRIBUTE, mx=MAX_ATTRIBUTE)
    return batter

def generate_pitcher_attributes(pitcher):
    for attr in PITCHER_NUMERICAL_ATTRIBUTES:
        pitcher[attr] = attribute_dist.calculate_random_percentile(mn=MIN_ATTRIBUTE, mx=MAX_ATTRIBUTE)  

    for pitch in pitcher["pitches"]:
        for attr in PITCH_NUMERICAL_ATTRIBUTES:
            pitch_dist = NDist(getattr(pitch, attr), DEFAULT_VAR) # Create a new distribution from the default pitch mean
            setattr(pitch, attr, pitch_dist.calculate_random_percentile(mn=MIN_ATTRIBUTE, mx=MAX_ATTRIBUTE)) # Assign a random value to the attribute
    return pitcher

def _generate_random_pitches():
    pitch_idxs = set()
    for i in range(0, random.randrange(1, MAX_PITCHES)): # Max number of pitches a pitcher can have
        rand_idx = random.randrange(0, len(PITCH_TYPES))
        # Set up to stop early
        tries = 0
        while (rand_idx in pitch_idxs or tries < MAX_ITER):
            rand_idx = random.randrange(0, len(PITCH_TYPES))
            tries += 1
        pitch_idxs.add(rand_idx)
    return pitch_idxs