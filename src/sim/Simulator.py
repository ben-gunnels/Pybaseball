import random
import time
from ..entities.Batter import Batter
from ..entities.Pitcher import Pitcher
from ..entities.Pitch import Pitch
from ..prob.NDist import NDist
from ..entities.TeamGenerator import TeamGenerator
from .GameState import GameState
from .config import GAME_SLIDERS, NUMBER_STRIKES, NUMBER_BALLS
from .Event import Event
from .EventRegister import EventRegister

class Simulator:
    # Independent pitcher event
    strike_prob_dist = NDist(GAME_SLIDERS.pitcher_events.strike_prob, 0.1)
    hbp_prob_dist = NDist(GAME_SLIDERS.pitcher_events.hbp_prob, 0.1)
    # Dependent batter event strike is thrown
    swing_strike_prob_dist = NDist(GAME_SLIDERS.batter_events.swing_strike_prob, 0.1)
    swing_miss_strike_prob_dist = NDist(GAME_SLIDERS.batter_events.swing_miss_strike_prob, 0.1)
    swing_foul_strike_prob_dist = NDist(GAME_SLIDERS.batter_events.swing_foul_strike_prob, 0.1)
    # Dependent batter event ball is thrown
    swing_ball_prob_dist = NDist(GAME_SLIDERS.batter_events.swing_ball_prob, 0.1)
    swing_miss_ball_prob_dist = NDist(GAME_SLIDERS.batter_events.swing_miss_ball_prob, 0.1)
    swing_foul_ball_prob_dist = NDist(GAME_SLIDERS.batter_events.swing_foul_ball_prob, 0.1)

    def __init__(self, team_a, team_b, game_state, event_register, **kwargs):
        assert(NUMBER_STRIKES > 0)
        assert(NUMBER_BALLS > 0)
        self.team_a = team_a
        self.team_b = team_b
        self.game_state = game_state
        self.event_register = event_register
        self.between_pitch_delay = kwargs.get("between_pitch_delay", 2)
        self.pitch_speed_delay = kwargs.get("pitch_speed_delay", 1)
        
    def decide_outcome(self, buckets):
        r = random.random()
        for i in range(len(buckets)):
            if (r < buckets[i]):
                return i
        return len(buckets)

    def display_intro(self, team, ballpark=False):
        team.display(ballpark)
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

    def at_bat(self, pitcher, batter):
        """
            Handles the course of a single at bat between a pitcher and a hitter.
            It manages the scenarios that could occur in a probabilistic manner. 
        """
        while (self.game_state.balls < NUMBER_BALLS and self.game_state.strikes < NUMBER_STRIKES):
            time.sleep(self.between_pitch_delay)
            pitch = random.choice(pitcher.pitches)
            pitch_outcome = self._pitch(pitch)
            self.game_state.current_state = self.event_register.pitcher_event[pitch_outcome]

            # Pitch -> Make Swing Decision
            if (self.game_state.current_state == "strike"): # Ball is in the zone
                swing_decision = self._batter_swing_decision(batter, pitcher, pitch, True)
                self.game_state.current_state = self.event_register.swing_decision_event[swing_decision] + " " + "strike" # Swing, In-Zone
                
            elif (self.game_state.current_state == "ball"):
                swing_decision = self._batter_swing_decision(batter, pitcher, pitch, True)
                self.game_state.current_state = self.event_register.swing_decision_event[swing_decision] + " " + "ball" # Swing, Not In-Zone
                
            elif (self.game_state.current_state == "hbp"):
                self.game_state.current_state = "hbp"
                hbp = Event("hbp", [], disp=f"Batter {batter.first_name} {batter.last_name} hit by pitch! Ouch! That's gotta hurt!")
                hbp.display()
                self.game_state.balls += NUMBER_BALLS
                break
            
            # Swing Decision -> Swing Outcome
            if (self.game_state.current_state == "swing strike"):
                swing_outcome = self._batter_swing(batter, pitcher, pitch, True)
                self.game_state.current_state = self.event_register.swing_outcome_event[swing_outcome]
                
            elif (self.game_state.current_state == "swing ball"):
                swing_outcome = self._batter_swing(batter, pitcher, pitch, False)
                self.game_state.current_state = self.event_register.swing_outcome_event[swing_outcome]
            
            elif (self.game_state.current_state == "take strike"):
                self.game_state.strikes += 1
                print("Strike!")
                if (self._check_strikeout()):
                    break
            
            elif (self.game_state.current_state == "take ball"):
                self.game_state.balls += 1
                print("Ball.")
                if (self._check_walk()):
                    break
            
            # Swing Outcome -> result
            if (self.game_state.current_state == "miss"):
                self.game_state.strikes += 1
                print("Strike! Swing and a Miss.")
                if (self._check_strikeout()):
                    break
            
            elif (self.game_state.current_state == "foul"):
                self.game_state.strikes = min(1 + self.game_state.strikes, NUMBER_STRIKES - 1) # Foul balls only increment below NUMBER_STRIKES - 1
                foul = Event("foul", [], f"Fouled off.")
                foul.display()
            
            elif (self.game_state.current_state == "in-play"):
                in_play = Event("in-play", [], f"{batter.first_name} {batter.last_name} puts that ball in play!")
                in_play.display()
                break
            
    def _pitch(self, pitch):
        strike_prob = self.strike_prob_dist.calculate_x(pitch.control)
        hbp_prob = self.hbp_prob_dist.calculate_x(1-pitch.control) # Invert the probability
        pitch_event = Event("pitch", [strike_prob.mu, strike_prob.mu + hbp_prob.mu],  f"And the {self.game_state.balls}-{self.game_state.strikes} pitch")
        pitch_event.display()
        time.sleep(self.pitch_speed_delay)
        return pitch_event.generate_outcome()
    
    def _batter_swing_decision(self, batter, pitcher, pitch, pitch_in_zone):
        # Sprinkle some stuff and deception on the pitch
        if pitch_in_zone:
            swing_prob = self.swing_strike_prob_dist.calculate_x(batter.zone_awareness) # Swing rate should be high for high zone awareness
            swing_prob = swing_prob.calculate_x(1-pitcher.deception) # Less likely to swing at strike with high deception and stuff
            swing_prob = swing_prob.calculate_x(1-pitch.stuff)
        else:
            swing_prob = self.swing_strike_prob_dist.calculate_x(((1-batter.zone_awareness) + (1-batter.patience)) / 2) # Batter patience improves likelihood of not swinging at a ball
            swing_prob = swing_prob.calculate_x(pitcher.deception) # More likely to swing at ball with high deception and stuff
            swing_prob = swing_prob.calculate_x(pitch.stuff)
        
        swing_decision_event = Event("swing-decision", [swing_prob.mu])
        return swing_decision_event.generate_outcome()

    def _batter_swing(self, batter, pitcher, pitch, pitch_in_zone):
        contact_trait = batter.contact_r if pitcher.handedness == "RH" else batter.contact_l
        if pitch_in_zone:
            swing_miss_prob = self.swing_miss_strike_prob_dist.calculate_x(1-contact_trait) 
            swing_miss_prob = swing_miss_prob.calculate_x((pitch.stuff + pitch.velocity) / 2) # High contact should 
            swing_foul_prob = self.swing_foul_strike_prob_dist.calculate_x(1-contact_trait) # reduce these probabilites
        else:
            swing_miss_prob = self.swing_miss_ball_prob_dist.calculate_x(1-contact_trait) 
            swing_miss_prob = swing_miss_prob.calculate_x((pitch.stuff + pitch.velocity) / 2) # High contact should 
            swing_foul_prob = self.swing_foul_ball_prob_dist.calculate_x(1-contact_trait) # Reduce these probabilites
        
        swing_event = Event("swing", [swing_miss_prob.mu, swing_miss_prob.mu + swing_foul_prob.mu], "Swung on...")
        swing_event.display()
        return swing_event.generate_outcome()
    
    def _check_walk(self):
        """
            Checks the current state of the balls in the count. If it is NUMBER_BALLS then it prints a walk and returns True.
        """
        if (self.game_state.balls >= NUMBER_BALLS):
            print(f"Ball 4. Take your base.")
            return True
        return False

    def _check_strikeout(self):
        """
            Checks the current state of the strikes in the count. If it is NUMBER_STRIKES then it prints a strikeout and returns True.
        """
        if (self.game_state.strikes >= NUMBER_STRIKES):
            print(f"Strike 3! You're Out!")
            return True
        return False

def main():
    # Dependent event on ball in play
    team_a = TeamGenerator().generate_team()
    team_b = TeamGenerator().generate_team()
    game_state = GameState(team_a, team_b, starting_pitcher_A=0, starting_pitcher_B=0)
    event_register = EventRegister()
    delay_timers = { "between_pitch_delay": 2, "pitch_speed_delay": 1}
    simulator = Simulator(team_a, team_b, game_state, event_register, **delay_timers)


    simulator.display_intro(team_a, True)
    simulator.display_intro(team_b)
    pitcher = simulator.game_state.field.starting_pitchers[game_state.pitcher_A]
    batter = simulator.game_state.batting.lineup[0]
    simulator.at_bat(pitcher, batter)



    # pitches = {"4SFB": Pitch(pitch_name="4SFB", velocity=0.7, stuff=0.7, control=0.5), "CUR": Pitch(pitch_name="CUR", velocity=0.4, stuff=0.9, control=0.4)}

    # mark_marsden = Pitcher(first_name="Mark", 
    #                     last_name="Marsden",
    #                     position="SP",
    #                     number=44,
    #                     pitches=pitches,
    #                     stamina=0.5,
    #                     deception=0.7,
    # )


    # jeff_brightbridge = Batter(first_name="Jeff",
    #                         last_name="Brightbridge",
    #                         position="1B",
    #                         number=12,
    #                         contact=0.88,
    #                         power=0.82,
    #                         zone_awareness=0.74,
    #                         patience=0.52,
    #                         speed=0.54
    # )

    # at_bats = { 'strike_outs': 0, 'hits': 0, 'walks': 0, 'in_play_out': 0 }

    # for i in range(1):
    #     balls = 0
    #     strikes = 0
    #     while (True):
    #         if (strikes >=3):
    #             print("Strike 3! You're Out!")
    #             at_bats["strike_outs"] = at_bats.get('strike_outs', 0) + 1
    #             break
    #         if (balls >= 4):
    #             print("Ball 4! Take your base!")
    #             at_bats["walks"] = at_bats.get('walks', 0) + 1
    #             break

    #         print(f"{balls}-{strikes}")
    #         print("And the pitch")
    #         time.sleep(1)
    #         pitch = mark_marsden.pitches["4SFB"]

    #         strike_prob = strike_prob_dist.calculate_x(pitch.control)
    #         swing = False
    #         if (random.random() < strike_prob.mu):
    #             swing_prob = swing_strike_prob_dist.calculate_x((jeff_brightbridge.zone_awareness + (1-jeff_brightbridge.patience)) / 2) # Swing rate should be high for high zone awareness
    #             if (random.random() < swing_prob.mu):
    #                 swing = True
    #             if (swing):
    #                 swing_miss_prob = swing_miss_strike_prob_dist.calculate_x(1-jeff_brightbridge.contact) # High contact should 
    #                 swing_miss_prob = swing_miss_prob.calculate_x((pitch.stuff + pitch.velocity) / 2)
    #                 swing_foul_prob = swing_foul_strike_prob_dist.calculate_x(1-jeff_brightbridge.contact) # Reduce these probabilites
    #                 outcome = decideOutcome([swing_miss_prob.mu, swing_foul_prob.mu])
    #                 outcomes = { 0: "Swing and Miss!", 1: "Foul Ball!", 2: "Base Hit"}
    #                 print(outcomes[outcome])
    #             else:
    #                 print("Strike! taken.")
    #                 outcome = 0
    #         else:
    #             swing_prob = swing_ball_prob_dist.calculate_x((1-jeff_brightbridge.zone_awareness) + (1-jeff_brightbridge.patience) / 2) # Swing rate should be low for low zone awareness
    #             if (random.random() < swing_prob.mu):
    #                 swing = True
    #             if (swing):
    #                 swing_miss_prob = swing_miss_ball_prob_dist.calculate_x(1-jeff_brightbridge.contact) # High contact should 
    #                 swing_miss_prob = swing_miss_prob.calculate_x((pitch.stuff + pitch.velocity) / 2)
    #                 swing_foul_prob = swing_foul_ball_prob_dist.calculate_x(1-jeff_brightbridge.contact) # Reduce these probabilites
    #                 outcome = decideOutcome([swing_miss_prob.mu, swing_foul_prob.mu])
    #                 outcomes = { 0: "Swing and Miss!", 1: "Foul Ball!", 2: "Base Hit"}
    #                 print(outcomes[outcome])
    #             else:
    #                 print("Ball taken.")
    #                 outcome = 3
    #         if (outcome == 0):
    #             strikes += 1
    #         elif (outcome == 1):
    #             strikes += 1 if strikes < 2 else 0
    #         elif (outcome == 2):
    #             hit_in_play_prob = hit_in_play_prob_dist.calculate_x(jeff_brightbridge.power)
    #             if (hit_in_play_prob.mu > random.random()):
    #                 at_bats["hits"] = at_bats.get("hits", 0) + 1
    #             else:
    #                 at_bats["in_play_out"] = at_bats.get("in_play_out", 0) + 1
    #             break
    #         elif (outcome == 3):
    #             balls += 1
    #         time.sleep(2)
    # print(f"K%: {100*at_bats['strike_outs']/250}, BB%: {100*at_bats['walks']/250}, BA: {100*at_bats['hits']/250}")
    
        

if __name__ == "__main__":
    main()