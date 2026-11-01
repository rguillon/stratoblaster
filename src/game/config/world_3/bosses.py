# Copyright (c) 2026 Renaud Guillon
"""The bosses of each World 3 level (WLD-3-19).

Each level has a mini boss at the middle of the level and a final boss at its end, by boss kind id,
and the seconds of ground drawn past the level's end for the fights (see `WORLD_1_BOSSES`). One
fight stops the ground, the Stone Idol's (MB-STONE-IDOL-06), and one is a chase, the Mangrove
Croc's (MB-MANGROVE-CROC-07).
"""

from game.config.record import record

WORLD_3_BOSSES = record({
    # Each level's mini boss, final boss and runout: LVL-3-1-06, LVL-3-1-07, LVL-3-1-08.
    "3-1": {"mini": "mangrove-croc", "final": "river-leviathan", "runout": 140},
    # LVL-3-2-06, LVL-3-2-07, LVL-3-2-08.
    "3-2": {"mini": "toucan", "final": "canopy-spider", "runout": 100},
    # LVL-3-3-06, LVL-3-3-07, LVL-3-3-08.
    "3-3": {"mini": "stone-idol", "final": "sky-temple", "runout": 70},
    # LVL-3-4-06, LVL-3-4-07, LVL-3-4-08.
    "3-4": {"mini": "mosquito", "final": "dam-breaker", "runout": 100},
    # LVL-3-5-06, LVL-3-5-07, LVL-3-5-08.
    "3-5": {"mini": "jaguar", "final": "verdant-crown", "runout": 100},
})
