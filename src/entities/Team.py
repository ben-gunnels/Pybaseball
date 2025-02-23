from .Batter import Batter
from .Pitcher import Pitcher
from typing import List
class Team:
    def __init__(self, **kwargs):
        self._city = kwargs.get("city", "City")
        self._name = kwargs.get("name", "Name")
        self._ballpark = kwargs.get("ballpark", "Ballpark")
        self._lineup = kwargs.get("lineup", [])
        self._starting_pitchers = kwargs.get("starting_pitchers", [])
        self._bullpen = kwargs.get("bullpen", [])
        self._bench = kwargs.get("bench", [])
        self._defense = kwargs.get("defense", {})

        # Management operations
        self._set_lineup()
        self._set_rotation()

    @property
    def city(self):
        return self._city
    
    @property
    def name(self):
        return self._name
    
    @property 
    def ballpark(self):
        return self._ballpark
    
    @property
    def lineup(self):
        return self._lineup
    
    @property
    def starting_pitchers(self):
        return self._starting_pitchers
    
    @property
    def bullpen(self):
        return self._bullpen
    
    @property
    def bench(self):
        return self._bench

    @property
    def defense(self):
        return self._defense

    def _fill_position(self, player) -> None: # Assign the players to the field by positional key value
        self._defense[player.position] = player
    
    def _set_lineup(self):
        self._lineup = sorted(self._lineup + self._bench, reverse=True, key=lambda x: x.overall) # Best player in leadoff spot

        self._bench = [] # Reset the bench and fill it with the lowest overall players with redundant spots
        tmp_lineup = []
        for player in self._lineup:
            if player.position in self._defense:            
                self._bench.append(player) # Add player to the bench
            else:
                self._fill_position(player)
                tmp_lineup.append(player)
        self._lineup = tmp_lineup
        
    def _set_rotation(self):
        self._starting_pitchers = sorted(self._starting_pitchers + self._bullpen, reverse=True, key=lambda x: x.overall + x.stamina) # Best pitcher in Ace spot
        self._bullpen = self._starting_pitchers[5:] # Send every pitcher after 5 to the bullpen
        self._starting_pitchers = self._starting_pitchers[:5]
    
    def display(self, ballpark = False):
        team_attributes = self.team_attributes()

        if ballpark:
            print(f"\nWelcome to {self._ballpark} Home of")
        print(f"The {self._city} {self._name}")
        print(f"Team Attributes")
        print(f"OVR:{team_attributes['overall']} HIT:{team_attributes['hitting']} PTCH:{team_attributes['pitching']} SPD:{team_attributes['speed']}")
        
    def team_attributes(self):
        """
            Provides the overall attribute, hit attribute, pitch attribute, and speed attribute for a team based on the average of its players.
        """
        players = 0
        overall_sum = 0
        hit_sum = 0
        hit_cats = 0
        pitch_sum = 0
        pitch_cats = 0
        speed_sum = 0
        speed_cats = 0

        for batter in (self.lineup + self.bench):
            # Add to overall attribute
            overall_sum += batter.calc_overall()
            players += 1
            # Add to the hitting attribute
            hit_sum += batter.contact_r + batter.contact_l + batter.power_r + batter.power_l + batter.zone_awareness
            hit_cats += 5
            # Add to the speed attribute
            speed_sum += batter.speed
            speed_cats += 1

        for pitcher in (self.starting_pitchers + self.bullpen):
            # Add to the overall
            overall_sum += pitcher.calc_overall()
            players += 1
            # add to just the pitchers
            pitch_sum += pitcher.calc_overall()
            pitch_cats += 1
        
        return { "overall": int((overall_sum / players) * 100), 
                "hitting": int((hit_sum / hit_cats) * 100), 
                "pitching": int((pitch_sum / pitch_cats) * 100),
                "speed": int((speed_sum / speed_cats) * 100)
                }
