from .EventRegister import EventRegister
from .Distributions import Distributions
from .Event import Event
from ..utils.utils import get_suffix
class BaseRunning:
    def __init__(self):
        # [First, Second, Third]
        self.bases = [0, 0, 0]
        self.event_register = EventRegister()
        self.dist = Distributions()
    
    def advance_runners(self, event, batter) -> int:
        if (event not in self.event_register.runners_advance_event):
            return 0 
        
        runs_scored = 0
        batter_advance = self.event_register.runners_advance_event[event][0] - 1

        for i in range(len(self.bases)-1, -1, -1):
            if not self._check_base_occupied(i):
                continue
            if len(self.event_register.runners_advance_event[event]) > 1: # More than 1 possible outcome
                advance_dist = getattr(self.dist, event)
                advance_prob = advance_dist.calculate_x(1-batter.speed) # High speed lowers probability of default advance
                advance_outcome = Event("runners-advance", [advance_prob], []).generate_outcome()
                # The number of bases that the runner can advance maximally
                advance_bases = self.event_register.runners_advance_event[event][advance_outcome]
            else:
                advance_bases = self.event_register.runners_advance_event[event][0]
            if self._check_scored(i+advance_bases): # runner scored
                runs_scored += 1
                self.bases[i] = 0
                continue
            if self._check_base_occupied(i+advance_bases):
                # Base is occupied and runner must stop on base before
                self.bases[i+advance_bases-1] = self.bases[i]
            else:
                # Base is open and runner can advance
                self.bases[i+advance_bases] = self.bases[i]
            # Clear the base
            self.bases[i] = 0
        if self._check_scored(batter_advance):
            runs_scored += 1 # Home run
        else:
            self.bases[batter_advance] = batter
        self.display(runs_scored)
        return runs_scored
                
    def clear_bases(self):
        self.bases = [0, 0, 0]

    def _check_scored(self, base):
        if (base >= len(self.bases)):
            return True
        return False

    def _check_base_occupied(self, base):
        if (self.bases[base] == 0):
            return False
        return True
    
    def display(self, runs_scored):
        if (runs_scored > 0):
            Event("score", [], [], f"{runs_scored} SCORED on that play!").display()
        for i, runner in enumerate(self.bases):
            if (runner != 0):
                Event("advance", [], [], f"{runner.last_name} ADVANCES to {i+1}{get_suffix(i+1)}").display() # Get the suffix for the ith + 1 base, e.g. 0 + 1 = 1st base
