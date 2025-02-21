from .config import PITCHER_EVENT_REGISTER, SWING_DECISION_EVENT_REGISTER, SWING_OUTCOME_EVENT_REGISTER, IN_PLAY_EVENT_REGISTER, OUT_EVENT_REGISTER

class EventRegister:
    def __init__(self):
        self.pitcher_event = PITCHER_EVENT_REGISTER
        self.swing_decision_event = SWING_DECISION_EVENT_REGISTER
        self.swing_outcome_event = SWING_OUTCOME_EVENT_REGISTER
        self.in_play_event = IN_PLAY_EVENT_REGISTER
        self.out_event = OUT_EVENT_REGISTER