from .config import GAME_SLIDERS
from ..entities.Team import Team
from typing import List

class GameState:
    # Track the current state of the game
    max_innings = 9 
    inning = (0, True) # Inning_no, Top of Inning
    outs = 0
    balls = 0
    strikes = 0 
    scores = (0, 0)

    def __init__(self, team_A: Team, team_B: Team, starting_p_A: int, starting_p_B: int, max_innings=9): # Team A = home team, Team B = Away Team
        team_A = team_A
        team_B = team_B
        starting_p_A = team_A.starting_pitchers[starting_p_A]
        starting_p_B = team_B.starting_pitchers[starting_p_B]
        max_innings = max_innings
    

    def start_game(self):
        print(f"The {self.team_B.city} {self.team_B.name} at The {self.team_A.city} {self.team_B.name}")
        print(f"{self.scores[0]}-{self.score[1]}")
        print(f"P {self.starting_p_A.first_name} {self.starting_p_B.last_name} takes the mound for the {self.team_A.name}")  
    

