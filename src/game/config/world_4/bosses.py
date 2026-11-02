# Copyright (c) 2026 Renaud Guillon
"""The bosses of each World 4 level (WLD-4-21).

Each level has a mini boss at the middle of the level and a final boss at its end, by boss kind id,
and the seconds of ground drawn past the level's end for the fights (see `WORLD_1_BOSSES`).
"""

from game.config.record import record

WORLD_4_BOSSES = record({
    # Each level's mini boss, final boss and runout: LVL-4-1-06, LVL-4-1-07, LVL-4-1-08.
    "4-1": {"mini": "cinder-crab", "final": "steam-dreadnought", "runout": 120},
    # LVL-4-2-06, LVL-4-2-07, LVL-4-2-08.
    "4-2": {"mini": "ash-wraith", "final": "geyser-rig", "runout": 150},
    # LVL-4-3-06, LVL-4-3-07, LVL-4-3-08.
    "4-3": {"mini": "magma-salamander", "final": "obsidian-golem", "runout": 100},
    # LVL-4-4-06, LVL-4-4-07, LVL-4-4-08.
    "4-4": {"mini": "furnace-drake", "final": "foundry-ark", "runout": 100},
    # LVL-4-5-06, LVL-4-5-07, LVL-4-5-08.
    "4-5": {"mini": "ember-herald", "final": "caldera-throne", "runout": 130},
})
