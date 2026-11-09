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
    "1-3": 1,
    "1-4": 1,
    "1-5": 1,
    "2-1": 1,
    "2-2": 1,
    "2-3": 1,
    "2-4": 1,
    "2-5": 1,
    "3-1": 1,
    "3-2": 1,
    "3-3": 1,
    "3-4": 1,
    "3-5": 1,
    "4-1": 1,
    "4-2": 1,
    "4-3": 1,
    "4-4": 1,
    "4-5": 1,
})
