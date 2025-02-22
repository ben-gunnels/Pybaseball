from ..settings.Sliders import Sliders

GAME_SLIDERS = Sliders()

NUMBER_STRIKES = 3
NUMBER_BALLS = 4
NUMBER_OUTS = 3
MAX_HBP = 0.08
MAX_GROUNDBALL_HR = 0.01
MAX_HR = 0.3
MAX_SWING_MISS = 0.6
PITCHER_NERF = 0.1

NUMBER_INNINGS = 3

PITCHER_EVENT_REGISTER = {0: "strike", 1: "hbp", 2: "ball"}
SWING_DECISION_EVENT_REGISTER = { 0: "swing", 1: "take" }
SWING_OUTCOME_EVENT_REGISTER = { 0: "miss", 1: "foul", 2: "in-play"}
IN_PLAY_EVENT_REGISTER = {  0: "groundball", 
                            1: "linedrive", 
                            2: "flyball",
                            3: "hit_on_groundball",
                            4: "hit_on_flyball",
                            5: "hit_on_linedrive",
                            6: "single_on_groundball",
                            7: "double_on_groundball",
                            8: "triple_on_groundball",
                            9: "homerun_on_groundball",
                            10: "single_on_linedrive",
                            11: "double_on_linedrive",
                            12: "triple_on_linedrive",
                            13: "homerun_on_linedrive",
                            14: "single_on_flyball",
                            15: "double_on_flyball",
                            16: "triple_on_flyball",
                            17: "homerun_on_flyball"
                        }

FIELDER_EVENT_REGISTER = {
                            0: "error_groundball",
                            1: "error_linedrive",
                            2: "error_flyball",
                            3: "groundball_1",
                            4: "groundball_2",
                            5: "groundball_3",
                            6: "groundball_4",
                            7: "groundball_5",
                            8: "groundball_6",
                            9: "groundball_7",
                            10: "groundball_8",
                            11: "groundball_9",
                            12: "linedrive_1",
                            13: "linedrive_2",
                            14: "linedrive_3",
                            15: "linedrive_4",
                            16: "linedrive_5",
                            17: "linedrive_6",
                            18: "linedrive_7",
                            19: "linedrive_8",
                            20: "linedrive_9",
                            21: "flyball_1",
                            22: "flyball_2",
                            23: "flyball_3",
                            24: "flyball_4",
                            25: "flyball_5",
                            26: "flyball_6",
                            27: "flyball_7",
                            28: "flyball_8",
                            29: "flyball_9"
                        }


OUT_EVENT_REGISTER = set({"strikeout", "groundball-out", "linedrive-out", "flyball-out"})

# Event followed by the standard number of bases to move runners
RUNNERS_ADVANCE_REGISTER = { 
                            "walk": [1],
                            "batter-hbp": [1],
                            "single_on_groundball": [1, 2], # First value is the likely value, the probability can be seen settings
                            "double_on_groundball": [2, 3],
                            "triple_on_groundball": [3],
                            "homerun_on_groundball": [4],
                            "single_on_linedrive": [1, 2],
                            "double_on_linedrive": [2, 3],
                            "triple_on_linedrive": [3],
                            "homerun_on_linedrive": [4],
                            "single_on_flyball": [1, 2],
                            "double_on_flyball": [2, 3],
                            "triple_on_flyball": [3],
                            "homerun_on_flyball": [4]
                        }


PACE_SETTINGS = {
                "turtle": { "intro_delay": 5, "team_intro_delay": 1, "between_pitch_delay": 4, "pitch_speed_delay": 1, "between_batter_delay": 2 },
                "deer": { "intro_delay": 2, "team_intro_delay": 0.5, "between_pitch_delay": 2, "pitch_speed_delay": 1, "between_batter_delay": 1 },
                "cheetah": { "intro_delay": 0, "team_intro_delay": 0, "between_pitch_delay": 0, "pitch_speed_delay": 0, "between_batter_delay": 0 }
                }