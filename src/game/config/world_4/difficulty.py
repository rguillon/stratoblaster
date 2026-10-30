"""Per-level factors on the phase 5 enemy values in World 4 (P10-R10, tunable values), ported from
`config/world-4/difficulty.ts`.

4-1 starts at least as hard as 3-3 and 4-5 is harder than 3-5. Neither ever goes down.
"""

from game.config.record import record

WORLD_4_DIFFICULTY = record(
    {
        "4-1": {"bulletSpeed": 1.1, "fireRate": 1.1},
        "4-2": {"bulletSpeed": 1.15, "fireRate": 1.15},
        "4-3": {"bulletSpeed": 1.2, "fireRate": 1.2},
        "4-4": {"bulletSpeed": 1.3, "fireRate": 1.3},
        "4-5": {"bulletSpeed": 1.35, "fireRate": 1.35},
    }
)
