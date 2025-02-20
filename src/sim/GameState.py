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
    
    current_state = None

    def __init__(self, team_A: Team, team_B: Team, starting_pitcher_A: int, starting_pitcher_B: int, max_innings=9): # Team A = home team, Team B = Away Team
        self.team_A = team_A.city + team_A.name # Provides a unique id to reference
        self.team_B = team_B.city + team_B.name
        self.pitcher_A = starting_pitcher_A
        self.pitcher_B = starting_pitcher_B
        self.max_innings = max_innings
        self.field = team_A
        self.batting = team_B
    

    def start_game(self):
        print(f"The {self.team_B.city} {self.team_B.name} at The {self.team_A.city} {self.team_B.name}")
        print(f"{self.scores[0]}-{self.score[1]}")
        print(f"P {self.pitcher_A.first_name} {self.pitcher_B.last_name} takes the mound for the {self.team_A.name}")  
    

