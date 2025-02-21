from .Team import Team
from .Batter import Batter
from .Pitcher import Pitcher
from .PlayerGenerator import randomize_player, generate_batter, generate_pitcher, generate_batter_attributes, generate_pitcher_attributes
from .static.Cities import CITIES
from .static.TeamMascots import TEAM_MASCOTS
from .static.StadiumNames import STADIUM_NAMES
import json
import random


class TeamGenerator:
    def __init__(self):
        # Load the provided JSON structure
        self.team_data = {
                          "city": random.choice(CITIES), 
                          "name": random.choice(TEAM_MASCOTS), 
                          "ballpark": random.choice(STADIUM_NAMES), 
                          "lineup": [], 
                          "starting_pitchers": [], 
                          "bullpen": [], 
                          "bench": [], 
                          "defense": {}
                          }

        # Set up object structure
        self.team_data["lineup"] = [generate_batter(i) for i in range(10) if i != 1]

        self.team_data["starting_pitchers"] = [generate_pitcher() for _ in range(5)]

        self.team_data["bullpen"] = [generate_pitcher() for _ in range(7)]

        self.team_data["bench"] = [generate_batter(random.choice([x for x in range(10) if x != 1])) for i in range(5)]

        numbers_taken = set()
        ids_taken = set()

        # Populate with random values
        for category in ["lineup", "starting_pitchers", "bullpen", "bench"]:
            if category in {"lineup", "bench"}:
                self.team_data[category] = [Batter(**generate_batter_attributes(randomize_player(player, ids_taken, numbers_taken))) for player in self.team_data[category]]
            elif category in {"starting_pitchers", "bullpen"}:
                self.team_data[category] = [Pitcher(**generate_pitcher_attributes(randomize_player(player, ids_taken, numbers_taken))) for player in self.team_data[category]]

        # Output the updated JSON
        # print(json.dumps(team_data, indent=4))

    def generate_team(self):
        return Team(**self.team_data)
        
        
