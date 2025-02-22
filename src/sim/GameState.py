from .config import GAME_SLIDERS, NUMBER_OUTS
from ..entities.Team import Team
from typing import List
from .EventRegister import EventRegister
from .BaseRunning import BaseRunning

class GameState:
    # Track the current state of the game
    inning = [1, True] # Inning_no, Top of Inning
    out = 0
    balls = 0
    strikes = 0 
    score = [0, 0]
    bullpen = [False, False] # The team has gone to the bullpen
    spot_in_order = [0, 0] # Index of batter in lineup currently up
    event_register = EventRegister()
    
    
    _current_state = None

    def __init__(self, team_A: Team, team_B: Team, starting_pitcher_A: int, starting_pitcher_B: int, verbose: bool = True): # Team A = home team, Team B = Away Team
        self.team_A = team_A.city + " " + team_A.name
        self.team_B = team_B.city + " " + team_B.name
        self.pitcher_A = starting_pitcher_A
        self.pitcher_B = starting_pitcher_B
        self.fielding_team = [team_A, self.team_A]
        self.pitcher = self.fielding_team[0].starting_pitchers[starting_pitcher_A]
        self.batting_team = [team_B, self.team_B]
        self.batter = self.batting_team[0].lineup[self.spot_in_order[1]] # Away team start to bat first
        self.baserunning = BaseRunning(verbose)

    def start_game(self):
        print(f"The {self.team_A} at The {self.team_B}")
        print(f"{self.scores[0]}-{self.score[1]}")
        print(f"P {self.pitcher_A.first_name} {self.pitcher_B.last_name} takes the mound for the {self.team_A.name}")

    @property
    def current_state(self):
        return self._current_state
    
    @current_state.setter
    def current_state(self, new_val):
        self._current_state = new_val
        # An out has been recorded
        if (new_val in self.event_register.out_event):
            self.out += 1
        
        if (new_val in self.event_register.runners_advance_event):
            tm = 0 if self.batting_team[1] == self.team_A else 1
            self.score[tm] += self.baserunning.advance_runners(new_val, self.batter)

        # Always change to the next batter, increment the spot in lineup
        if (new_val == "at-bat-completed"):
            self._next_batter()
             # Handle logic for switching the teams
            if (self.out >= NUMBER_OUTS):
                self._switch_sides()
    
    def _next_batter(self):
        # Get the index of the team at bat
        bat = 0 if self.batting_team[1] == self.team_A else 1
        # Get the spot that the team is currently in the order
        spot = self.spot_in_order[bat] 
        # Wrap around if the 9 hitter has just finished
        self.spot_in_order[bat] = spot + 1 if spot < 8 else 0
        # Set the batter to the current spot in the lineup
        self.batter = self.batting_team[0].lineup[self.spot_in_order[bat]]
        self.current_state = "next-batter" # Temporary state to prevent loop

    
    def _switch_sides(self):
        # Reset the inning
        self.out = 0
        self.baserunning.clear_bases()
        
        # Switch offense and defense
        self.fielding_team, self.batting_team = self.batting_team, self.fielding_team
        
        # Get the index for the fielding team and the batting team
        fld = 0 if self.fielding_team[1] == self.team_A else 1
        bat = not fld

        if (not self.bullpen[fld]):
            self.pitcher = self.fielding_team[0].starting_pitchers[self.pitcher_A] if (self.fielding_team[1] == self.team_A) else self.fielding_team[0].starting_pitchers[self.pitcher_B]
        else:
            self.pitcher = self.fielding_team[0].bullpen[self.pitcher_A] if (self.fielding_team[1] == self.team_A) else self.fielding_team[0].bullpen[self.pitcher_B]
        
        # Get the batter from the remembered state
        self.batter = self.batting_team[0].lineup[self.spot_in_order[bat]]

        if (not self.inning[1]): # Bottom of the inning
            self.inning[0] += 1
            
        self.inning[1] = not self.inning[1] # Flip top to bottom, bottom to top

        self.current_state = "switch-sides"

            


      
    

