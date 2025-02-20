from ..settings.Sliders import Sliders

GAME_SLIDERS = Sliders()

NUMBER_STRIKES = 3
NUMBER_BALLS = 4

PITCHER_EVENT_REGISTER = {0: "strike", 1: "hbp", 2: "ball"}
SWING_DECISION_EVENT_REGISTER = { 0: "swing", 1: "take" }
SWING_OUTCOME_EVENT_REGISTER = { 0: "miss", 1: "foul", 2: "in-play"}