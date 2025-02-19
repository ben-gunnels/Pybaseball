from .Batter import Batter
from .Pitcher import Pitcher
from typing import List
class Team:
    def __init__(self, **kwargs):
        self.city = kwargs.get("city", "City")
        self.name = kwargs.get("name", "Name")
        self.ballpark = kwargs.get("ballpark", "Ballpark")
        self.lineup = kwargs.get("lineup", [])
        self.starting_pitchers = kwargs.get("starting_pitchers", [])
        self.bullpen = kwargs.get("bullpen", [])
        self.bench = kwargs.get("bench", [])
        self.defense = kwargs.get("defense", {})

        # Management operations
        self._set_lineup()
        self._set_rotation()

    def _fill_position(self, player) -> None: # Assign the players to the field by positional key value
        self.defense[player.position] = player
    
    def _set_lineup(self):
        self.lineup = sorted(self.lineup + self.bench, reverse=True, key=lambda x: x._get_overall()) # Best player in leadoff spot

        self.bench = [] # Reset the bench and fill it with the lowest overall players with redundant spots
        tmp_lineup = []
        for player in self.lineup:
            if player.position in self.defense:            
                self.bench.append(player) # Add player to the bench
            else:
                self._fill_position(player)
                tmp_lineup.append(player)
        self.lineup = tmp_lineup
        


    def _set_rotation(self):
        self.starting_pitchers = sorted(self.starting_pitchers + self.bullpen, reverse=True, key=lambda x: x._get_overall() + x.stamina) # Best pitcher in Ace spot
        self.bullpen = self.starting_pitchers[5:] # Send every pitcher after 5 to the bullpen
        self.starting_pitchers = self.starting_pitchers[:5]
    
    def display(self, ballpark = False):
        if ballpark:
            print(f"Welcome to {self.ballpark} Home of")
        print(f"The {self.city} {self.name}")
        