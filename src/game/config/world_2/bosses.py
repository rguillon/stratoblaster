# Copyright (c) 2026 Renaud Guillon
"""The bosses of each World 2 level (WLD-2-24).

Each level has a mini boss at the middle of the level and a final boss at its end, by boss kind id,
and the seconds of ground drawn past the level's end for the fights (see `WORLD_1_BOSSES`).
"""

from game.config.record import record

WORLD_2_BOSSES = record({
    # Each level's mini boss, final boss and runout: LVL-2-1-11, LVL-2-1-12, LVL-2-1-13.
    "2-1": {"mini": "floe-breaker", "final": "narwhal", "runout": 160},
    # LVL-2-2-11, LVL-2-2-12, LVL-2-2-13.
    "2-2": {"mini": "fjord-lynx", "final": "harbour-kraken", "runout": 50},
    # LVL-2-3-11, LVL-2-3-12, LVL-2-3-13.
    "2-3": {"mini": "snow-owl", "final": "aurora-station", "runout": 80},
    # LVL-2-4-11, LVL-2-4-12, LVL-2-4-13.
    "2-4": {"mini": "avalanche", "final": "glacier-colossus", "runout": 120},
    # LVL-2-5-11, LVL-2-5-12, LVL-2-5-13.
    "2-5": {"mini": "ice-queen", "final": "boreal-citadel", "runout": 80},
})
