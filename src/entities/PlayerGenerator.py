from .Batter import Batter
from .Pitcher import Pitcher
from .Pitch import Pitch

pitches = [Pitch(pitch_name="4SFB", velocity=0.6, stuff=0.8, control=0.5), Pitch(pitch_name="CUR", velocity=0.4, stuff=0.9, control=0.4)]

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

mark_marsden.display()
print("VERSUS\n")
jeff_brightbridge.display()