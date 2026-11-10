# Copyright (c) 2026 Renaud Guillon
"""How many enemies each level brings, as a factor on its composed waves (D-307).

Every enemy and every boss is the same in every level: its fire rate, its bullets' speed and its
health are its own, for the whole game. What makes a level harder is how many enemies it brings:
each wave's groups and each filler group between waves, `enemies` times as many as `level_plan`
composes (1: as composed), the waves coming when they would at 1. `make adjust-level` tunes these
to a target difficulty.
"""

from game.config.record import record

LEVEL_ENEMIES = record({
    "1-1": 1,
    "1-2": 1,
    "1-3": 1.4,
    "1-4": 1.59,
    "1-5": 1.57,
    "2-1": 2.28,
    "2-2": 1.96,
    "2-3": 1.66,
    "2-4": 1.45,
    "2-5": 1.6,
    "3-1": 2.33,
    "3-2": 1.71,
    "3-3": 1.4,
    "3-4": 1.55,
    "3-5": 1,
    "4-1": 1.96,
    "4-2": 1.96,
    "4-3": 2.74,
    "4-4": 10.54,
    "4-5": 28.92,
})
