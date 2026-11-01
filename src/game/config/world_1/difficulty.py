# Copyright (c) 2026 Renaud Guillon
"""Per-level factors on the phase 5 enemy values (WLD-1-23, tunable values).

Enemy bullets fly faster and enemies attack more often from 1-1 to 1-5. Neither ever goes down.
"""

from game.config.record import record

WORLD_1_DIFFICULTY = record({
    "1-1": {"bulletSpeed": 0.8, "fireRate": 0.8},  # LVL-1-1-11, WLD-1-25: the lowest
    "1-2": {"bulletSpeed": 0.85, "fireRate": 0.85},  # LVL-1-2-11
    "1-3": {"bulletSpeed": 0.9, "fireRate": 0.9},  # LVL-1-3-11
    "1-4": {"bulletSpeed": 1, "fireRate": 1},  # LVL-1-4-11
    "1-5": {"bulletSpeed": 1.1, "fireRate": 1.1},  # LVL-1-5-11
})
