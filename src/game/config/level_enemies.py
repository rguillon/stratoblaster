# Copyright (c) 2026 Renaud Guillon
"""How many enemies each level brings, as a factor on its composed waves (D-307).

Every enemy and every boss is the same in every level: its fire rate, its bullets' speed and its
health are its own, for the whole game. What makes a level harder is how many enemies it brings:
each wave's groups and each filler group between waves, `enemies` times as many as `level_plan`
composes (1: as composed), the waves coming when they would at 1. Set from a scripted player's
exposure (D-316) for a difficulty rising evenly from 10 % (1-1) to 70 % (4-5); `make adjust-level`
tunes them with the brain.
"""

from game.config.record import record

LEVEL_ENEMIES = record({
    "1-1": 1.13,
    "1-2": 1.43,
    "1-3": 1.55,
    "1-4": 1.67,
    "1-5": 2.19,
    "2-1": 2.52,
    "2-2": 2.36,
    "2-3": 1.92,
    "2-4": 2.16,
    "2-5": 2.14,
    "3-1": 2.94,
    "3-2": 2.38,
    "3-3": 2.25,
    "3-4": 2.08,
    "3-5": 2.35,
    "4-1": 3.0,
    "4-2": 3.16,
    "4-3": 2.74,
    "4-4": 2.59,
    "4-5": 2.76,
})
