import random
import time
from ..entities.Batter import Batter
from ..entities.Pitcher import Pitcher
from ..entities.Pitch import Pitch
from ..entities.TeamGenerator import TeamGenerator
from ..utils.utils import get_suffix
from ..utils.UserInterface import input_with_verification
from .GameState import GameState
from .Event import Event
from .EventRegister import EventRegister
from .Distributions import Distributions
from .config import (NUMBER_STRIKES, NUMBER_BALLS, MAX_HBP, MAX_HR, MAX_GROUNDBALL_HR, 
                     MAX_SWING_MISS, PITCHER_NERF, NUMBER_INNINGS, PACE_SETTINGS)

class Simulator:
    """
        Simulates over the course of a game for two teams.
    
    """
    def __init__(self, game_state, event_register, data_table, number_innings=NUMBER_INNINGS, verbose=True, **kwargs):
        assert(NUMBER_STRIKES > 0)
        assert(NUMBER_BALLS > 0)
        self.number_innings = number_innings
        self.verbose = verbose
        self.game_state = game_state
        self.event_register = event_register
        self.data = data_table
        self.between_pitch_delay = kwargs.get("between_pitch_delay", 0)
        self.pitch_speed_delay = kwargs.get("pitch_speed_delay", 0)
        self.intro_delay = kwargs.get("intro_delay", 0)
        self.team_intro_delay = kwargs.get("team_intro_delay", 0)
        self.between_batter_delay = kwargs.get("between_batter_delay", 0)
        self.dist = Distributions()
    
    def sim_game(self, intro=True):
        """
            Facilitates the logic for simulating the course of a game. Checks the end game condition in the loop to see if a game should terminate.
            A game terminates if the home team is leading going into the bottom of the last inning, if the home team takes the lead in the bottom of the last inning, 
            or if the game is in a tie at the end of the last inning. 
        """
        if (intro):
            time.sleep(self.intro_delay)
            self._display_intro(self.game_state.A, True)
            time.sleep(self.intro_delay)
            self._display_intro(self.game_state.B)

        while (not self._check_game_end_condition()):
            self.game_state.current_state = "start-inning"
            if (self.game_state.inning[0] == 1 and self.game_state.inning[1]):
                Event(self.game_state.current_state, [], [self.data], verbose=self.verbose, disp=f"{self.game_state.batting_team[1]} ready to get us started!\n").display()
            else:
                Event(self.game_state.current_state, [], [self.data], verbose=self.verbose, disp=f"END OF INNING! {self.game_state.batting_team[1]} coming up to the plate!\n").display()
            while (self.game_state.current_state != "switch-sides" and not self._check_game_end_condition()):
                time.sleep(self.between_batter_delay)
                self.at_bat(self.game_state.pitcher, self.game_state.batter)

        winner_display = self._handle_end_game()

        Event("end-game", [], 
              [self.data], 
              verbose=True,  # Always display the end game results
              disp=f"\nEND OF GAME!\n{winner_display}\nFinal Score:\n{self.game_state.team_B} {self.game_state.score[1]}\n{self.game_state.team_A} {self.game_state.score[0]}\n").display()

                
    def at_bat(self, pitcher: Pitcher, batter: Batter):
        """
            Handles the course of a single at bat between a pitcher and a hitter.
            It manages the scenarios that could occur in a probabilistic manner. 
            Params: pitcher (Pitcher), batter (batter)
            Returns: None
        """
        break_condition = False
        self.game_state.balls = 0
        self.game_state.strikes = 0
        batter_data = self.data.get(f"{batter.first_name}_{batter.last_name}_{batter.player_id}", {})
        pitcher_data = self.data.get(f"{pitcher.first_name}_{pitcher.last_name}_{pitcher.player_id}", {})

        at_bat_message = (
                f"\n"
                f"{'Top' if self.game_state.inning[1] else 'Bottom'} of the {self.game_state.inning[0]}{get_suffix(self.game_state.inning[0])} inning.\n"
                f"{self.game_state.team_B} {self.game_state.score[1]}\n{self.game_state.team_A} {self.game_state.score[0]}\n"
                f"{pitcher.first_name} {pitcher.last_name} toes the rubber to face {batter.first_name} {batter.last_name} with {self.game_state.out} outs.\n"
        )

        runners_on = self.game_state.baserunning.runners_on()
        if len(runners_on) > 0:
            runners_on_message = "Runners on " if len(runners_on) > 1 else "Runner on "
            for base in runners_on:
                runners_on_message += f"{base} "
            at_bat_message += runners_on_message
            at_bat_message += "\n"

        Event("at-bat", [], [batter_data, pitcher_data], verbose=self.verbose, disp=at_bat_message).display()

        while (True):
            if (break_condition):
                self.data[f"{batter.first_name}_{batter.last_name}_{batter.player_id}"] = batter_data
                self.data[f"{pitcher.first_name}_{pitcher.last_name}_{pitcher.player_id}"] = pitcher_data
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
                Event("batter-hbp", [], [batter_data, pitcher_data], verbose=self.verbose, disp=f"Batter {batter.first_name} {batter.last_name} HIT BY PITCH! Ouch! That's gotta hurt!").display()
                self.game_state.current_state = "batter-hbp"
                break_condition = True
            
            # Swing Decision -> Swing Outcome
            if (self.game_state.current_state == "swing strike"):
                swing_outcome = self._batter_swing(batter, pitcher, pitch, True, [batter_data, pitcher_data])
                Event("swinging-strike", [], [batter_data, pitcher_data])
                self.game_state.current_state = self.event_register.swing_outcome_event[swing_outcome]
                
            elif (self.game_state.current_state == "swing ball"):
                swing_outcome = self._batter_swing(batter, pitcher, pitch, False, [batter_data, pitcher_data])
                Event("swinging-ball", [], [batter_data, pitcher_data], verbose=self.verbose, disp=f"{batter.last_name} went fishing for that one!").display()
                self.game_state.current_state = self.event_register.swing_outcome_event[swing_outcome]
            
            elif (self.game_state.current_state == "take strike"):
                self.game_state.strikes += 1
                Event("strike", [], [batter_data, pitcher_data], verbose=self.verbose, disp="Taken\nStrike!").display()
                if (self._check_strikeout()):
                    Event(self.game_state.current_state, [], [batter_data, pitcher_data], verbose=self.verbose, disp=f"Strike {NUMBER_STRIKES}! YOU'RE OUT!").display()
                    self.game_state.current_state = "strikeout"
                    break_condition = True
            
            elif (self.game_state.current_state == "take ball"):
                self.game_state.balls += 1
                Event("ball", [], [batter_data, pitcher_data], verbose=self.verbose, disp="Taken\nBall.").display()
                if (self._check_walk()):
                    Event(self.game_state.current_state, [], [batter_data, pitcher_data], verbose=self.verbose, disp=f"Ball {NUMBER_BALLS}. Take your base. WALK").display()
                    self.game_state.current_state = "walk"
                    break_condition = True
            
            # Swing Outcome -> result
            if (self.game_state.current_state == "miss"):
                self.game_state.strikes += 1
                Event("swing-miss", [], [batter_data, pitcher_data], verbose=self.verbose, disp="Strike! Swing and a miss!").display()
                if (self._check_strikeout()):
                    Event(self.game_state.current_state, [], [batter_data, pitcher_data], verbose=self.verbose, disp=f"Strike {NUMBER_STRIKES}! YOU'RE OUT!").display()
                    self.game_state.current_state = "strikeout"
                    break_condition = True
            
            elif (self.game_state.current_state == "foul"):
                self.game_state.strikes = min(1 + self.game_state.strikes, NUMBER_STRIKES - 1) # Foul balls only increment below NUMBER_STRIKES - 1
                foul = Event("foul", [], [batter_data, pitcher_data], verbose=self.verbose, disp=f"Fouled off.")
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
        in_play = Event("in-play", [groundball_prob.mu, linedrive_prob.mu], [batter_data, pitcher_data], verbose=self.verbose, disp=f"{batter.first_name} {batter.last_name} puts that ball IN PLAY!")
        in_play.display()
        in_play_outcome = in_play.generate_outcome()
        self.game_state.current_state = self.event_register.in_play_event[in_play_outcome]
        hit_type = self.game_state.current_state

        # Get whether the play is a hit 
        hit_prob_dist = getattr(self.dist, f"hit_on_{self.game_state.current_state}_prob_dist")
        hit_prob = hit_prob_dist.calculate_x((contact_trait+power_trait) / 2) # Likelihood of a hit is impacted by the average of contact and power
        hit = Event("deciding-hit", [hit_prob.mu], [])
        hit_outcome = hit.generate_outcome()
        self.game_state.current_state = f"{hit_type}-hit" if hit_outcome == 0 else f"out" # Ephemeral state

        # If its a hit decide which fielder it is hit to
        if (self.game_state.current_state == f"{hit_type}-hit"):
            Event("hit", [], [batter_data, pitcher_data], verbose=self.verbose)
            homerun_prob_dist = getattr(self.dist, f"homerun_on_{hit_type}_prob_dist")
            if (hit_type == "groundball"):
                homerun_prob = homerun_prob_dist.calculate_x((power_trait + (1-pitch.control*PITCHER_NERF))/2, mx=MAX_GROUNDBALL_HR)
            else:
                homerun_prob = homerun_prob_dist.calculate_x((power_trait + (1-pitch.control*PITCHER_NERF))/2, mx=MAX_HR)
             # Pitcher control limits homeruns
            triple_prob_dist = getattr(self.dist, f"triple_on_{hit_type}_prob_dist")
            triple_prob = triple_prob_dist.calculate_x((power_trait + 0.1*batter.speed)/2)
            double_prob_dist = getattr(self.dist, f"double_on_{hit_type}_prob_dist")
            double_prob = double_prob_dist.calculate_x((power_trait + batter.speed)/2)
            single_prob = 1 - homerun_prob.mu - triple_prob.mu - double_prob.mu # Marginalize Singles, singles gets whats left
            total_bases = Event("total-bases", [single_prob, single_prob + double_prob.mu, single_prob + double_prob.mu + triple_prob.mu], [])
            total_bases_outcome = total_bases.generate_outcome()

            event_helper_table = { "groundball": 6, "linedrive": 10, "flyball": 14 } # Starting index for each hit type
            outcome = self.event_register.in_play_event[event_helper_table[hit_type] + total_bases_outcome]
            Event(outcome, [], [batter_data, pitcher_data], verbose=self.verbose, disp=f"{hit_type.capitalize()}...{['SINGLE.', 'DOUBLE!', 'TRIPLE!!', 'HOME RUN!!! See ya later!'][total_bases_outcome]}").display()
            self.game_state.current_state = outcome
        
        elif (self.game_state.current_state == f"out"):
            ### @TODO add fielder errors to this section
            Event(f"{self.game_state.current_state}", [], [batter_data, pitcher_data], verbose=self.verbose, disp=f"{hit_type.capitalize()} out!").display()
            self.game_state.current_state = f"{hit_type}-out"  

    def _display_intro(self, team, ballpark=False):
        """ 
            Provides full team introductions to use prior to the start of a game. 
        """
        team.display(ballpark)
        time.sleep(self.intro_delay)
        print(f"Starting lineup: ")
        for i, player in enumerate(team.lineup):
            print(f"{i+1}: ")
            player.display()
            time.sleep(self.team_intro_delay)
        
        print("Starting pitchers: ")
        for player in team.starting_pitchers:
            player.display()
            time.sleep(self.team_intro_delay)

        print("Bullpen: ")
        for player in team.bullpen:
            player.display()
            time.sleep(self.team_intro_delay)

        print("Bench: ")
        for player in team.bench:
            player.display()
            time.sleep(self.team_intro_delay)
        print("\n") 
            
    def _pitch(self, pitch: Pitch, data: dict):
        """
            Generates the pitcher independent outcome: whether the pitch tossed is a ball or a strike. 
            Parameters: pitch (Pitch), data (dict)
            Returns: int (0 - strike, 1 - hbp, 2 - ball)
        """
        strike_prob = self.dist.strike_prob_dist.calculate_x(pitch.control)
        hbp_prob = self.dist.hbp_prob_dist.calculate_x(1-pitch.control, mx=MAX_HBP) # Invert the probability, cap the probability at MAX_HBP
        pitch_event = Event("pitch", [strike_prob.mu, strike_prob.mu + hbp_prob.mu], data, verbose=self.verbose, disp=f"And the {self.game_state.balls}-{self.game_state.strikes} pitch")
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
        
        swing_decision_event = Event("swing-decision", [swing_prob.mu], [])
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
        
        swing_event = Event("swing", [swing_miss_prob.mu, swing_miss_prob.mu + swing_foul_prob.mu], data, verbose=self.verbose, disp="SWUNG ON...")
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
    
    def _check_game_end_condition(self):
        """
            Evaluates the game situation to see if it should terminate. Checks that the winning team is ahead in the bottom of the last inning, 
            or the max number of innings has been exceeded.
            Returns: (bool), True - Game end condition is met, False - Game end condition is not met. 
        
        """
        if self.game_state.inning[0] > self.number_innings:
            return True
        
        if self.game_state.inning[0] == self.number_innings and not self.game_state.inning[1]: # If we are in the last inning in the bottom of the inning
            if self.game_state.score[0] > self.game_state.score[1]:
                return True
        return False
    
    def _handle_end_game(self):
        """
            Handles end game logic. Adds winner/loser/tie data to teams key of data table. Returns a display for the winner/tie
            Returns: display (str). Display for game's winner or TIE-GAME if it is a tie
        
        """
        # handle winner outcome
        winner = 0 if self.game_state.score[0] > self.game_state.score[1] else 1 # 0 - Team A won, 1 - Team B won
        winner = 2 if self.game_state.score[0] == self.game_state.score[1] else winner
        winner_display = self.game_state.team_A + " WIN!" if not winner else self.game_state.team_B + " WIN!"
        winner_display = "TIE-GAME" if winner == 2 else winner_display
        return winner_display
    

    def _add_team_data_to_table(self, team: str):
        """
            Adds relevant team info to the data table following the completion of a game. Including adding to a teams register of wins/losses/ties/games.
            Parameters: team (str), the team name which comes from game_state
        """
        team_data_table_key = team.replace(" ", "_")
        default_team_table = { "games": 0, "wins": 0, "losses": 0, "ties": 0 }

        self.data[team_data_table_key] = self.data.get(team_data_table_key, default_team_table)

        self.data[team_data_table_key]["games"] = self.data[team_data_table_key].get("games", 0) + 1
        self.data[team_data_table_key]["wins"] = self.data[team_data_table_key].get("wins", 0) + 1
        self.data[team_data_table_key]["losses"] = self.data[team_data_table_key].get("losses", 0) + 1
        self.data[team_data_table_key["ties"]] = self.data[team_data_table_key].get("ties", 0) + 1


def main():
    # Dependent event on ball in play
    print(f"Setting up Pybaseball Simulator...")
    print(f"Let's set up some configurations.")
    
    # Set verbosity
    verbose = input_with_verification(f"Would you like to receive a play-by-play printout of the game? [y/n]: ", ('y', 'n'))
    verbose = True if verbose == 'y' else False
    # Set innings limit
    innings = input_with_verification(f"How many innings would you like to play? [1-9]: ", ('1', '2', '3', '4', '5', '6', '7', '8', '9'))
    innings = int(innings)
    # Set pace 
    pace = input_with_verification(f"What speed would like the game to be played at? [turtle, deer, cheetah]: ", ('turtle', 'deer', 'cheetah'))
    delay_timers = PACE_SETTINGS[pace]


    team_a = TeamGenerator().generate_team()
    team_b = TeamGenerator().generate_team()
    game_state = GameState(team_a, team_b, starting_pitcher_A=random.randrange(0, 5), starting_pitcher_B=random.randrange(0, 5), verbose=verbose)
    event_register = EventRegister()
    data = {}
    simulator = Simulator(game_state, event_register, data, number_innings=innings, verbose=verbose, **delay_timers)

    # Initialize the data
    for player in team_a.lineup + team_a.bench + team_a.starting_pitchers + team_a.bullpen:
        data[f"{player.first_name}_{player.last_name}_{player.player_id}"] = {}
    
    # Initialize the data
    for player in team_b.lineup + team_b.bench + team_b.starting_pitchers + team_b.bullpen:
        data[f"{player.first_name}_{player.last_name}_{player.player_id}"] = {}

    simulator.sim_game()

    # Define the box score setup
    stats = ["POS", "PLAYER", "AB", "H", "1B", "2B", "3B", "HR", "SO", "BB", "HBP"]
    key_words = ["at-bat-completed", "hit", "single", "double", "triple", "homerun", "strikeout", "walk", "hbp"] # Search queries for a stat in database
    # Define column widths
    col_widths = [5, 25, 3, 3, 3, 3, 3, 3, 3, 3, 3]    

    print(f"{team_a.city} {team_a.name} box score")
    print("".join(str(stats[i]).ljust(col_widths[i]) for i in range(len(stats))))
    for player in team_a.lineup:
        player_id = f"{player.first_name}_{player.last_name}_{player.player_id}"
        row = [player.translate_position(), f"{player.first_name} {player.last_name}"]
        for i, kw in enumerate(key_words):
            key_matches = [k for k in data.get(player_id, {}) if kw in k]
            accumulator = 0
            for k in key_matches:
                accumulator += data[player_id].get(k, 0) 
            row.append(accumulator)
        print("".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row))))

    print(f"\n{team_b.city} {team_b.name} box score")
    print("".join(str(stats[i]).ljust(col_widths[i]) for i in range(len(stats))))
    for player in team_b.lineup:
        player_id = f"{player.first_name}_{player.last_name}_{player.player_id}"
        row = [player.translate_position(), f"{player.first_name} {player.last_name}"]
        for i, kw in enumerate(key_words):
            key_matches = [k for k in data[player_id] if kw in k]
            accumulator = 0
            for k in key_matches:
                accumulator += data[player_id].get(k, 0) 
            row.append(accumulator)
        print("".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row))))

if __name__ == "__main__":
    main()