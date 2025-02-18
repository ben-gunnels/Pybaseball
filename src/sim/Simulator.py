import random
import time
from ..entities.Batter import Batter
from ..entities.Pitcher import Pitcher
from ..entities.Pitch import Pitch
from ..prob.NDist import NDist
from .config import GAME_SLIDERS

# [0.1, 0.3]
def decideOutcome(buckets):
    r = random.random()
    for i in range(len(buckets)):
        if (r < buckets[i]):
            return i
    return len(buckets)

def main():
    # Independent pitcher event
    strike_prob_dist = NDist(GAME_SLIDERS.pitcher_events.strike_prob, 0.1)
    # Dependent batter event strike is thrown
    swing_strike_prob_dist = NDist(GAME_SLIDERS.batter_events.swing_strike_prob, 0.1)
    swing_miss_strike_prob_dist = NDist(GAME_SLIDERS.batter_events.swing_miss_strike_prob, 0.1)
    swing_foul_strike_prob_dist = NDist(GAME_SLIDERS.batter_events.swing_foul_strike_prob, 0.1)
    # Dependent batter event ball is thrown
    swing_ball_prob_dist = NDist(GAME_SLIDERS.batter_events.swing_ball_prob, 0.1)
    swing_miss_ball_prob_dist = NDist(GAME_SLIDERS.batter_events.swing_miss_ball_prob, 0.1)
    swing_foul_ball_prob_dist = NDist(GAME_SLIDERS.batter_events.swing_foul_ball_prob, 0.1)
    # Dependent event on ball in play
    hit_in_play_prob_dist = NDist(GAME_SLIDERS.in_play_events.hit_in_play_prob, 0.1)

    pitches = {"4SFB": Pitch(pitch_name="4SFB", velocity=0.6, stuff=0.8, control=0.3), "CUR": Pitch(pitch_name="CUR", velocity=0.4, stuff=0.9, control=0.4)}

    mark_marsden = Pitcher(first_name="Mark", 
                        last_name="Marsden",
                        position="SP",
                        number=44,
                        pitches=pitches,
                        stamina=0.5,
                        deception=0.7,
    )


    jeff_brightbridge = Batter(first_name="Jeff",
                            last_name="Brightbridge",
                            position="1B",
                            number=12,
                            contact=0.6,
                            power=0.82,
                            zone_awareness=0.74,
                            patience=0.52,
                            speed=0.54
    )

    at_bats = { 'strike_outs': 0, 'hits': 0, 'walks': 0, 'in_play_out': 0 }

    for i in range(250):
        balls = 0
        strikes = 0
        while (True):
            if (strikes >=3):
                print("Strike 3! You're Out!")
                at_bats["strike_outs"] = at_bats.get('strike_outs', 0) + 1
                break
            if (balls >= 4):
                print("Ball 4! Take your base!")
                at_bats["walks"] = at_bats.get('walks', 0) + 1
                break

            print(f"{balls}-{strikes}")
            print("And the pitch")
            # time.sleep(1)
            pitch = mark_marsden.pitches["4SFB"]

            strike_prob = strike_prob_dist.calculate_x(pitch.control)
            swing = False
            if (random.random() < strike_prob):
                # print("Strike!")
                swing_prob = swing_strike_prob_dist.calculate_x((jeff_brightbridge.zone_awareness + (1-jeff_brightbridge.patience)) / 2) # Swing rate should be high for high zone awareness
                if (random.random() < swing_prob):
                    swing = True
                if (swing):
                    swing_miss_prob = swing_miss_strike_prob_dist.calculate_x(1-jeff_brightbridge.contact) # High contact should 
                    swing_foul_prob = swing_foul_strike_prob_dist.calculate_x(1-jeff_brightbridge.contact) # Reduce these probabilites
                    outcome = decideOutcome([swing_miss_prob, swing_foul_prob])
                    outcomes = { 0: "Swing and Miss!", 1: "Foul Ball!", 2: "Base Hit"}
                    print(outcomes[outcome])
                else:
                    print("Strike taken.")
                    outcome = 0
            else:
                # print("Ball.")
                swing_prob = swing_ball_prob_dist.calculate_x((1-jeff_brightbridge.zone_awareness) + (1-jeff_brightbridge.patience) / 2) # Swing rate should be low for low zone awareness
                if (random.random() < swing_prob):
                    swing = True
                if (swing):
                    swing_miss_prob = swing_miss_ball_prob_dist.calculate_x(1-jeff_brightbridge.contact) # High contact should 
                    swing_foul_prob = swing_foul_ball_prob_dist.calculate_x(1-jeff_brightbridge.contact) # Reduce these probabilites
                    outcome = decideOutcome([swing_miss_prob, swing_foul_prob])
                    outcomes = { 0: "Swing and Miss!", 1: "Foul Ball!", 2: "Base Hit"}
                    print(outcomes[outcome])
                else:
                    print("Ball taken.")
                    outcome = 3
            if (outcome == 0):
                strikes += 1
            elif (outcome == 1):
                strikes += 1 if strikes < 2 else 0
            elif (outcome == 2):
                hit_in_play_prob = hit_in_play_prob_dist.calculate_x(jeff_brightbridge.power)
                if (hit_in_play_prob > random.random()):
                    at_bats["hits"] = at_bats.get("hits", 0) + 1
                else:
                    at_bats["in_play_out"] = at_bats.get("in_play_out", 0) + 1
                break
            elif (outcome == 3):
                balls += 1
            # time.sleep(2)
    print(f"K%: {100*at_bats['strike_outs']/250}, BB%: {100*at_bats['walks']/250}, BA: {100*at_bats['hits']/250}")
    
        

if __name__ == "__main__":
    main()