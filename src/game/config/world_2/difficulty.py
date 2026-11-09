# Copyright (c) 2026 Renaud Guillon
"""Per-level factors on the phase 5 enemy values in World 2 (WLD-2-21, tunable values).

They go on from World 1 (WLD-2-23): 2-1 as hard as 1-3 and 2-5 harder than 1-5. Neither ever goes
down.
"""

from game.config.record import record

WORLD_2_DIFFICULTY = record({
    "2-1": {"bulletSpeed": 0.9, "fireRate": 0.9, "bossHealth": 1},  # LVL-2-1-10
    "2-2": {"bulletSpeed": 0.95, "fireRate": 0.95, "bossHealth": 1},  # LVL-2-2-10
    "2-3": {"bulletSpeed": 1, "fireRate": 1, "bossHealth": 1},  # LVL-2-3-10
    "2-4": {"bulletSpeed": 1.1, "fireRate": 1.1, "bossHealth": 1},  # LVL-2-4-10
    "2-5": {"bulletSpeed": 1.15, "fireRate": 1.15, "bossHealth": 1},  # LVL-2-5-10
})
