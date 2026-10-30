"""Per-level factors on the phase 5 enemy values in World 2 (P08-R09, tunable values), ported from
`config/world-2/difficulty.ts`.

They go on from World 1: 2-1 as hard as 1-3 and 2-5 harder than 1-5. Neither ever goes down.
"""

from game.config.record import record

WORLD_2_DIFFICULTY = record(
    {
        "2-1": {"bulletSpeed": 0.9, "fireRate": 0.9},
        "2-2": {"bulletSpeed": 0.95, "fireRate": 0.95},
        "2-3": {"bulletSpeed": 1, "fireRate": 1},
        "2-4": {"bulletSpeed": 1.1, "fireRate": 1.1},
        "2-5": {"bulletSpeed": 1.15, "fireRate": 1.15},
    }
)
