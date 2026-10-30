"""Cars on the streets and main roads (phase 4 review), ported from `config/cars.ts`."""

from game.config.record import record
from game.config.tile_buildings import TILE

CAR_IDS = record(
    {
        "red": "car-red",
        "blue": "car-blue",
        "white": "car-white",
        "grey": "car-grey",
        "van": "van",
        "truck": "truck",
    }
)

# Cars stand in the middle of a lane, on the road surface (`roads.lift`).
CAR_RULES = record(
    {
        "kinds": ["car-red", "car-blue", "car-white", "car-grey", "van", "truck"],
        "density": 0.3,
        "lift": 0.6,
        "scale": 0.6,
        "length": 4,
        # Phase 15 (P15-R11): cars keep off the sidewalks of the streets.
        "sidewalk": TILE.sidewalk,
        "speed": [12, 30],
    }
)
