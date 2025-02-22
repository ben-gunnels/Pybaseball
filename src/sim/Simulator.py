import random
import time
from ..entities.Batter import Batter
from ..entities.Pitcher import Pitcher
from ..entities.Pitch import Pitch
from ..entities.TeamGenerator import TeamGenerator
from ..utils.utils import get_suffix
from .GameState import GameState
from .config import (NUMBER_STRIKES, NUMBER_BALLS, MAX_HBP, MAX_HR, MAX_GROUNDBALL_HR, 
                     MAX_SWING_MISS, PITCHER_NERF, NUMBER_INNINGS)
from .Event import Event
from .EventRegister import EventRegister
from .Distributions import Distributions

class Simulator:
    def __init__(self, team_a, team_b, game_state, event_register, data_table, number_innings=NUMBER_INNINGS, **kwargs):
        assert(NUMBER_STRIKES > 0)
        assert(NUMBER_BALLS > 0)
        self.number_innings = number_innings
        self.team_a = team_a
        self.team_b = team_b
        self.game_state = game_state
        self.event_register = event_register
        self.data = data_table
        self.between_pitch_delay = kwargs.get("between_pitch_delay", 0)
        self.pitch_speed_delay = kwargs.get("pitch_speed_delay", 0)
        self.dist = Distributions()

    def display_intro(self, team, ballpark=False, delay=0):
        team.display(ballpark)
        time.sleep(delay)
        print(f"Starting lineup: ")
        for i, player in enumerate(team.lineup):
            print(f"{i+1}: ")
            player.display()
        
        print("Starting pitchers: ")
        for player in team.starting_pitchers:
            player.display()

        print("Bullpen: ")
        for player in team.bullpen:
            player.display()

        print("Bench: ")
        for player in team.bench:
            player.display()
        print("\n")
    
    def sim_game(self):
        while (True):
            if (self.game_state.inning[0] > self.number_innings):
                Event("end-game", [], [self.data], f"\nEND OF GAME!\nFinal Score: {self.game_state.team_A} {self.game_state.score[0]} to {self.game_state.team_B} {self.game_state.score[1]}").display()
                break

            self.game_state.current_state = "start-inning"
            if (self.game_state.inning[0] == 1 and self.game_state.inning[1]):
                Event(self.game_state.current_state, [], [self.data], f"{self.game_state.batting_team[1]} ready to get us started!\n").display()
            else:
                Event(self.game_state.current_state, [], [self.data], f"END OF INNING! {self.game_state.batting_team[1]} coming up to the plate!\n").display()
            
            while (self.game_state.current_state != "switch-sides"):
                self.at_bat(self.game_state.pitcher, self.game_state.batter)
                
    def at_bat(self, pitcher: Pitcher, batter: Batter):
        """
            Handles the course of a single at bat between a pitcher and a hitter.
            It manages the scenarios that could occur in a probabilistic manner. 
            Params: pitcher (Pitcher), batter (batter)
            Returns: None
        """
        self.game_state.balls = 0
        self.game_state.strikes = 0

        batter_data = self.data.get(f"{batter.first_name}_{batter.last_name}_{batter._id}", {})
        pitcher_data = self.data.get(f"{pitcher.first_name}_{pitcher.last_name}_{pitcher._id}", {})

        break_condition = False
        at_bat_message = (
                f"\n"
                f"{'Top' if self.game_state.inning[1] else 'Bottom'} of the {self.game_state.inning[0]}{get_suffix(self.game_state.inning[0])} inning.\n"
                f"The score is {self.game_state.team_A} {self.game_state.score[0]} to \n{self.game_state.team_B} {self.game_state.score[1]}.\n"
                f"{pitcher.first_name} {pitcher.last_name} toes the rubber to face {batter.first_name} {batter.last_name} with {self.game_state.out} outs.\n"
        )
    
        Event("at-bat", [], [batter_data, pitcher_data], at_bat_message).display()

        while (True):
            if (break_condition):
                self.data[f"{batter.first_name}_{batter.last_name}_{batter._id}"] = batter_data
                self.data[f"{pitcher.first_name}_{pitcher.last_name}_{pitcher._id}"] = pitcher_data
                Event("at-bat-completed", [], [batter_data, pitcher_data])
                self.game_state.current_state = "at-bat-completed"
                break
            time.sleep(self.between_pitch_delay)
            pitch = random.choice(pitcher.pitches)
            pitch_outcome = self._pitch(pitch, [batter_data, pitcher_data])
            self.game_state.current_state = self.event_register.pitcher_event[pitch_outcome]

            # Pitch -> Make Swing Decision
            if (self.game_state.current_state == "strike"): # Ball is in the zone
                swing_decision = self._batter_swing_decision(batter, pitcher, pitch, True, [batter_data, pitcher_data])
                self.game_state.current_state = self.event_register.swing_decision_event[swing_decision] + " " + "strike" # Swing, In-Zone
                
            elif (self.game_state.current_state == "ball"):
                swing_decision = self._batter_swing_decision(batter, pitcher, pitch, False, [batter_data, pitcher_data])
                self.game_state.current_state = self.event_register.swing_decision_event[swing_decision] + " " + "ball" # Swing, Not In-Zone
                
            elif (self.game_state.current_state == "hbp"):
                Event("batter-hbp", [], [batter_data, pitcher_data], disp=f"Batter {batter.first_name} {batter.last_name} HIT BY PITCH! Ouch! That's gotta hurt!").display()
                self.game_state.current_state = "batter-hbp"
                break_condition = True
            
            # Swing Decision -> Swing Outcome
            if (self.game_state.current_state == "swing strike"):
                swing_outcome = self._batter_swing(batter, pitcher, pitch, True, [batter_data, pitcher_data])
                Event("swinging-strike", [], [batter_data, pitcher_data])
                self.game_state.current_state = self.event_register.swing_outcome_event[swing_outcome]
                
            elif (self.game_state.current_state == "swing ball"):
                swing_outcome = self._batter_swing(batter, pitcher, pitch, False, [batter_data, pitcher_data])
                Event("swinging-ball", [], [batter_data, pitcher_data], f"{batter.last_name} went fishing for that one!").display()
                self.game_state.current_state = self.event_register.swing_outcome_event[swing_outcome]
            
            elif (self.game_state.current_state == "take strike"):
                self.game_state.strikes += 1
                Event("strike", [], [batter_data, pitcher_data], "Taken\nStrike!").display()
                if (self._check_strikeout()):
                    Event("strikeout", [], [batter_data, pitcher_data], f"Strike {NUMBER_STRIKES}! YOU'RE OUT!").display()
                    self.game_state.current_state = "strikeout"
                    break_condition = True
            
            elif (self.game_state.current_state == "take ball"):
                self.game_state.balls += 1
                Event("ball", [], [batter_data, pitcher_data], "Taken\nBall.").display()
                if (self._check_walk()):
                    Event("walk", [], [batter_data, pitcher_data], f"Ball {NUMBER_BALLS}. Take your base. WALK").display()
                    self.game_state.current_state = "walk"
                    break_condition = True
            
            # Swing Outcome -> result
            if (self.game_state.current_state == "miss"):
                self.game_state.strikes += 1
                Event("swing-miss", [], [batter_data, pitcher_data])
                print("Strike! Swing and a Miss.")
                if (self._check_strikeout()):
                    Event("strikeout", [], [batter_data, pitcher_data], f"Strike {NUMBER_STRIKES}! YOU'RE OUT!").display()
                    self.game_state.current_state = "strikeout"
                    break_condition = True
            
            elif (self.game_state.current_state == "foul"):
                self.game_state.strikes = min(1 + self.game_state.strikes, NUMBER_STRIKES - 1) # Foul balls only increment below NUMBER_STRIKES - 1
                foul = Event("foul", [], [batter_data, pitcher_data], f"Fouled off.")
                foul.display()
            
            elif (self.game_state.current_state == "in-play"):
                self.in_play(batter, pitcher, pitch, batter_data, pitcher_data)
                break_condition = True

    def in_play(self, batter: Batter, pitcher: Pitcher, pitch: Pitch, batter_data: dict, pitcher_data: dict):
        """
            Manages the outcomes generated for a ball that is put in play. The ball can either generate a hit or an out. 
            The type of contact is generated (groundball, linedrive, flyball).
            If the swing results in a hit then the total bases the hitter earned is computed based on the type of contact. 
            Parameters: batter (Batter), pitcher (Pitcher), pitch (Pitch), pitch_in_zone (bool), batter_data (dict), pitcher_data (dict)
            Returns: None
        
        """
        contact_trait = batter.contact_r if pitcher.handedness == "RH" else batter.contact_l
        power_trait = batter.power_r if pitcher.handedness == "LH" else batter.power_l

        # First get the type of contact that is made groundball, flyball, linedrive
        groundball_prob = self.dist.groundball_prob_dist.calculate_x(((1-power_trait) + pitch.control*0.1)/2) # Pitch control increases odds of groundball
        linedrive_prob = self.dist.linedrive_prob_dist.calculate_x((power_trait + (1-pitch.stuff*0.1))/2) # Let pitch stuff nerf the power
        in_play = Event("in-play", [groundball_prob.mu, linedrive_prob.mu], [batter_data, pitcher_data], f"{batter.first_name} {batter.last_name} puts that ball IN PLAY!")
        in_play.display()
        in_play_outcome = in_play.generate_outcome()
        self.game_state.current_state = self.event_register.in_play_event[in_play_outcome]
        hit_type = self.game_state.current_state

        # Get whether the play is a hit 
        hit_prob_dist = getattr(self.dist, f"hit_on_{self.game_state.current_state}_prob_dist")
        hit_prob = hit_prob_dist.calculate_x((contact_trait+power_trait) / 2) # Likelihood of a hit is impacted by the average of contact and power
        hit = Event("deciding-hit", [hit_prob.mu], [batter_data, pitcher_data])
        hit_outcome = hit.generate_outcome()
        self.game_state.current_state = f"{hit_type}-hit" if hit_outcome == 0 else f"out" # Ephemeral state

        # If its a hit decide which fielder it is hit to
        if (self.game_state.current_state == f"{hit_type}-hit"):
            homerun_prob_dist = getattr(self.dist, f"homerun_hit_on_{hit_type}_prob_dist")
            if (hit_type == "groundball"):
                homerun_prob = homerun_prob_dist.calculate_x((power_trait + (1-pitch.control*PITCHER_NERF))/2, mx=MAX_GROUNDBALL_HR)
            else:
                homerun_prob = homerun_prob_dist.calculate_x((power_trait + (1-pitch.control*PITCHER_NERF))/2, mx=MAX_HR)
             # Pitcher control limits homeruns
            triple_prob_dist = getattr(self.dist, f"triple_hit_on_{hit_type}_prob_dist")
            triple_prob = triple_prob_dist.calculate_x((power_trait + 0.1*batter.speed)/2)
            double_prob_dist = getattr(self.dist, f"double_hit_on_{hit_type}_prob_dist")
            double_prob = double_prob_dist.calculate_x((power_trait + batter.speed)/2)
            single_prob = 1 - homerun_prob.mu - triple_prob.mu - double_prob.mu # Marginalize Singles, singles gets whats left
            print(f"[{homerun_prob.mu}, {triple_prob.mu}, {double_prob.mu}, {single_prob}]")
            total_bases = Event("total-bases", [single_prob, single_prob + double_prob.mu, single_prob + double_prob.mu + triple_prob.mu], [batter_data, pitcher_data])
            total_bases_outcome = total_bases.generate_outcome()

            event_helper_table = { "groundball": 6, "linedrive": 10, "flyball": 14 } # Starting index for each hit type
            Event(self.game_state.current_state, [], [batter_data, pitcher_data], f"{hit_type.capitalize()}...{['SINGLE.', 'DOUBLE!', 'TRIPLE!!', 'HOME RUN!!! See ya later!'][total_bases_outcome]}").display()
            self.game_state.current_state = self.event_register.in_play_event[event_helper_table[hit_type]+total_bases_outcome]
        
        elif (self.game_state.current_state == f"out"):
            ### @TODO add fielder errors to this section
            Event(f"{self.game_state.current_state}", [], [batter_data, pitcher_data], f"{hit_type.capitalize()} out!").display()
            self.game_state.current_state = f"{hit_type}-out"
            
    def _pitch(self, pitch: Pitch, data: dict):
        """
            Generates the pitcher independent outcome: whether the pitch tossed is a ball or a strike. 
            Parameters: pitch (Pitch), data (dict)
            Returns: int (0 - strike, 1 - hbp, 2 - ball)
        """
        strike_prob = self.dist.strike_prob_dist.calculate_x(pitch.control)
        hbp_prob = self.dist.hbp_prob_dist.calculate_x(1-pitch.control, mx=MAX_HBP) # Invert the probability, cap the probability at MAX_HBP
        pitch_event = Event("pitch", [strike_prob.mu, strike_prob.mu + hbp_prob.mu], data, f"And the {self.game_state.balls}-{self.game_state.strikes} pitch")
        pitch_event.display()
        time.sleep(self.pitch_speed_delay)
        return pitch_event.generate_outcome()
    
    def _batter_swing_decision(self, batter: Batter, pitcher: Pitcher, pitch: Pitch, pitch_in_zone: bool, data: dict):
        """
            Generates the outcome of the batter deciding to either swing or take based on the pitch being in the zone or out of the zone.
            Parameters: batter (Batter), pitcher (Pitcher), pitch (Pitch), pitch_in_zone (bool), data (dict)
            Returns: int (Value of either 0 - swing, 1- no swing)
        
        """
        # Sprinkle some stuff and deception on the pitch
        # Nerf swing rate with high patience
        if pitch_in_zone:
            aggressiveness = batter.zone_awareness if self.game_state.strikes > 0 else  1 - batter.patience
            aggressiveness = aggressiveness if self.game_state.strikes < NUMBER_STRIKES - 1 else 0.8 # Higher likelihood to swing with two strikes
            swing_prob = self.dist.swing_strike_prob_dist.calculate_x((batter.zone_awareness + aggressiveness) / 2) # Swing rate should be high for high zone awareness
            swing_prob = swing_prob.calculate_x(1-pitcher.deception) # Less likely to swing at strike with high deception and stuff
            swing_prob = swing_prob.calculate_x(1-pitch.stuff)
        else:
            swing_prob = self.dist.swing_ball_prob_dist.calculate_x(((1-batter.zone_awareness) + (1-batter.patience)) / 2) # Batter patience improves likelihood of not swinging at a ball
            swing_prob = swing_prob.calculate_x(pitcher.deception) # More likely to swing at ball with high deception and stuff
            swing_prob = swing_prob.calculate_x(pitch.stuff)
        
        swing_decision_event = Event("swing-decision", [swing_prob.mu], data)
        return swing_decision_event.generate_outcome()

    def _batter_swing(self, batter: Batter, pitcher: Pitcher, pitch: Pitch, pitch_in_zone: bool, data: dict):
        """
            If a batter has swung this generates the outcome for whether the swing misses the pitch, fouls the pitch, or puts the pitch in play.
            Parameters: batter (Batter), pitcher (Pitcher), pitch (Pitch), pitch_in_zone (bool), data (dict)
            Returns: int (0 - miss, 1 - foul, 2 - in play)
        """
        contact_trait = batter.contact_r if pitcher.handedness == "RH" else batter.contact_l
        if pitch_in_zone:
            swing_miss_prob = self.dist.swing_miss_strike_prob_dist.calculate_x(1-contact_trait) 
            swing_miss_prob = swing_miss_prob.calculate_x((pitch.stuff + pitch.velocity) / 2, mx=MAX_SWING_MISS) # High contact should 
            swing_foul_prob = self.dist.swing_foul_strike_prob_dist.calculate_x(1-contact_trait) # reduce these probabilites
        else:
            swing_miss_prob = self.dist.swing_miss_ball_prob_dist.calculate_x(1-contact_trait) 
            swing_miss_prob = swing_miss_prob.calculate_x((pitch.stuff + pitch.velocity) / 2, mx=MAX_SWING_MISS) # High contact should 
            swing_foul_prob = self.dist.swing_foul_ball_prob_dist.calculate_x(1-contact_trait) # Reduce these probabilites
        
        swing_event = Event("swing", [swing_miss_prob.mu, swing_miss_prob.mu + swing_foul_prob.mu], data, disp="SWUNG ON...")
        swing_event.display()
        return swing_event.generate_outcome()
    
    def _check_walk(self):
        """
            Checks the current state of the balls in the count. If it is NUMBER_BALLS then it prints a walk and returns True.
        """
        if (self.game_state.balls >= NUMBER_BALLS):
            return True
        return False

    def _check_strikeout(self):
        """
            Checks the current state of the strikes in the count. If it is NUMBER_STRIKES then it prints a strikeout and returns True.
        """
        if (self.game_state.strikes >= NUMBER_STRIKES):
            return True
        return False

def main():
    # Dependent event on ball in play
    team_a = TeamGenerator().generate_team()
    team_b = TeamGenerator().generate_team()
    game_state = GameState(team_a, team_b, starting_pitcher_A=random.randrange(0, 5), starting_pitcher_B=random.randrange(0, 5))
    event_register = EventRegister()
    delay_timers = { "between_pitch_delay": 0, "pitch_speed_delay": 0}
    data = {}
    simulator = Simulator(team_a, team_b, game_state, event_register, data, number_innings=3, **delay_timers)


    simulator.display_intro(team_a, True, delay=0)
    time.sleep(0)
    simulator.display_intro(team_b, delay=0)
    time.sleep(0)

    simulator.sim_game()

    # print(data)

if __name__ == "__main__":
    main()