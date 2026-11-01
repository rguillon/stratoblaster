"""Per-level factors on the phase 5 enemy values in World 3 (WLD-3-17, tunable values)

3-1 starts as hard as 2-3 and 3-5 is harder than 2-5 (WLD-3-18). Neither ever goes down.
"""

from game.config.record import record

WORLD_3_DIFFICULTY = record(
    {
        "3-1": {"bulletSpeed": 1, "fireRate": 1},  # LVL-3-1-05
        "3-2": {"bulletSpeed": 1.05, "fireRate": 1.05},  # LVL-3-2-05
        "3-3": {"bulletSpeed": 1.1, "fireRate": 1.1},  # LVL-3-3-05
        "3-4": {"bulletSpeed": 1.2, "fireRate": 1.2},  # LVL-3-4-05
        "3-5": {"bulletSpeed": 1.25, "fireRate": 1.25},  # LVL-3-5-05
    }
)
