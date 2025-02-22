from .EventRegister import EventRegister
from .Distributions import Distributions
from .Event import Event
from ..utils.utils import get_suffix

class BaseRunning:
    def __init__(self, verbose):
        # [First, Second, Third]
        self.bases = [0, 0, 0]
        self.event_register = EventRegister()
        self.dist = Distributions()
        self.verbose = verbose
    
    def advance_runners(self, event, batter, batter_out=False, advance_bases=[2, 1, 0]) -> int:
        if (event not in self.event_register.runners_advance_event):
            return 0 
        
        runs_scored = 0
        if (not batter_out):
            batter_advance = self.event_register.runners_advance_event[event][0] - 1

        for i in advance_bases:
            if not self._check_base_occupied(i):
                continue
            if len(self.event_register.runners_advance_event[event]) > 1: # More than 1 possible outcome
                advance_dist = getattr(self.dist, f"{event}_runners_prob_dist")
                advance_prob = advance_dist.calculate_x(1-batter.speed) # High speed lowers probability of default advance
                advance_outcome = Event("runners-advance", [advance_prob.mu], []).generate_outcome()
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
        
        if (not batter_out):
            if self._check_scored(batter_advance):
                runs_scored += 1 # Home run
            else:
                self.bases[batter_advance] = batter

        self.display(runs_scored)
        return runs_scored

    def advance_runners_on_out(self, event, batter):
        fst = self._check_base_occupied(0)
        scnd = self._check_base_occupied(1)
        thrd = self._check_base_occupied(2)
        run = 0
        if (event == "groundball-out"):
            if (fst and scnd and thrd):
                self._clear_base_and_move_up(batter, 2, "Home")
            elif (fst and scnd):
                self._clear_base_and_move_up(batter, 1, "Third")
            elif (fst):
                self._clear_base_and_move_up(batter, 0, "Second")

        elif (event == "flyball-out"):
            if (thrd):
                self.advance_runners(event, batter, batter_out=True, advance_bases=[2]) # Only advance the runner from third



    def clear_bases(self):
        self.bases = [0, 0, 0]

    def runners_on(self):
        on = []
        for i in range(len(self.bases)):
            if self.bases[i] != 0:
                on.append(f"{i+1}{get_suffix(i+1)}")
        return on
    
    def _clear_base_and_move_up(self, batter, base, disp):
        Event("fielders-choice", [], [], verbose=self.verbose, disp=f"FIELDERS CHOICE! {self.bases[base].last_name} out at {disp}!")
        self.bases[base] = 0
        self.advance_runners(batter, "walk") # Call it a walk to guarantee the runners move only 1 base u

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
            Event("score", [], [], verbose=self.verbose, disp=f"{runs_scored} SCORED on that play!").display()
        for i, runner in enumerate(self.bases):
            if (runner != 0):
                Event("advance", [], [], verbose=self.verbose, disp=f"{runner.last_name} ADVANCES to {i+1}{get_suffix(i+1)}").display() # Get the suffix for the ith + 1 base, e.g. 0 + 1 = 1st base
