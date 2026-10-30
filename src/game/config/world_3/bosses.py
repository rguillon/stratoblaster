"""The bosses of each World 3 level (P09-R09), ported from `config/world-3/bosses.ts`.

Each level has a mini boss at the middle of the level and a final boss at its end, by boss kind id,
and the seconds of ground drawn past the level's end for the fights (see `WORLD_1_BOSSES`).
"""

from game.config.record import record

WORLD_3_BOSSES = record(
    {
        "3-1": {"mini": "mangrove-croc", "final": "river-leviathan", "runout": 140},
        "3-2": {"mini": "toucan", "final": "canopy-spider", "runout": 100},
        "3-3": {"mini": "stone-idol", "final": "sky-temple", "runout": 70},
        "3-4": {"mini": "mosquito", "final": "dam-breaker", "runout": 100},
        "3-5": {"mini": "jaguar", "final": "verdant-crown", "runout": 100},
    }
)
