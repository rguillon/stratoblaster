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
    "1-1": 1.14,
    "1-2": 1.4,
    "1-3": 1.61,
    "1-4": 1.73,
    "1-5": 1.73,
    "2-1": 2.91,
    "2-2": 2.55,
    "2-3": 2.15,
    "2-4": 1.96,
    "2-5": 2.25,
    "3-1": 3.29,
    "3-2": 2.35,
    "3-3": 1.96,
    "3-4": 2.31,
    "3-5": 2.43,
    "4-1": 3.06,
    "4-2": 3.84,
    "4-3": 10.54,
    "4-4": 28.92,
    "4-5": 28.92,
})
