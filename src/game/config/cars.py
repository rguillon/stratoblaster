"""Cars on the streets and main roads (GFX-CAR-06; phase 4 review)"""

from game.config.record import record
from game.config.tile_buildings import TILE

# The eight car kinds (GFX-CAR-01).
CAR_IDS = record(
    {
        "red": "car-red",
        "blue": "car-blue",
        "white": "car-white",
        "grey": "car-grey",
        "van": "van",
        "truck": "truck",
        "bus": "bus",
        "tanker": "tanker",
    }
)

# D-211, GFX-CAR-05: the cars drawn as imposters, baked from their detailed models (see
# `render/scenery/imposters.py`): 16 headings, 128-pixel frames 12 model units across, centred
# 1.8 up, softly shaded.
CAR_IMPOSTERS = record(
    {"headings": 16, "framePx": 128, "frameSize": 12, "centre": 1.8, "ambient": 0.75}
)

# Cars stand in the middle of a lane, on the road surface (`roads.lift`, GFX-CAR-07); in the
# streets of Worlds 3 and 4 too (WLD-3-13, WLD-4-13).
CAR_RULES = record(
    {
        "kinds": [
            "car-red",
            "car-blue",
            "car-white",
            "car-grey",
            "van",
            "truck",
            "bus",
            "tanker",
        ],
        "density": 0.3,
        "lift": 0.6,
        # Their own size, not stretched to whole tiles (GFX-CAR-04).
        "scale": 0.6,
        "length": 4,
        # Phase 15 (GFX-CAR-07): cars keep off the sidewalks of the streets.
        "sidewalk": TILE.sidewalk,
        "speed": [12, 30],
    }
)
