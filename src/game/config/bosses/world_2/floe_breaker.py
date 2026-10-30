"""The Floe Breaker (P08-R10, 2-1), ported from `config/bosses/world-2/floe-breaker.ts`.

The mini boss of the Ice floes level. Offsets in px from the boss's centre, X right and Y up (its
nose points down, at -Y). The stage patterns are the agent's design (P07-R04): the harpoon guns
fire the same while they stand, the core fires something new at every stage, and its last stage
(only the core left) a ring used by no earlier stage. Health values are placeholders for the
P08-R11 tuning.
"""

from game.config.bosses.boss_kit import bullet, mirror, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.record import record

RED = bullet("red", 190)
MAGENTA = bullet("magenta", 180)
BLUE = bullet("blue", 185)

# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).

# The right harpoon gun's barrel tip, as its turret rests (barrel down the screen).
FLOE_HARPOON = [[30, -23.88, 7.58]]
# The two bow chasers on the armoured bow (the core's fans and aimed shots).
FLOE_CHASERS = twin(3, -32.54, 10.4)
# The frost beacon on the bridge roof (the core's last-stage rings).
FLOE_BEACON = [[0, 18, 24.6]]

# 2-1: an icebreaker hovership with a sharp armoured bow and cyan neon; two side harpoon guns on
# sponsons fire aimed bursts and shield the core (P08-R10).
FLOE_BREAKER = record(
    {
        "id": "floe-breaker",
        # Angry after each destroyed part (phase 7 review).
        "rage": rage.curtain(2.5, "blue", "magenta"),
        "stats": stats(
            {
                "id": "floe-breaker",
                "name": "Floe Breaker",
                "size": 3,
                "coreRadius": 18,
                "coreHealth": 1420,
                "points": 5500,
                "groundSpeed": 0.5,
                "parts": [
                    part("harpoon-left", [-30, -4], 13, 650),
                    part("harpoon-right", [30, -4], 13, 650),
                ],
            }
        ),
        "stopFraction": 0.72,
        "sway": {"amplitude": 65, "period": 7},
        "bob": {"amplitude": 8, "period": 3.5},
        "guns": {
            "core": {"gun": FLOE_CHASERS, "ring": FLOE_BEACON},
            "harpoon-left": {"gun": mirror(FLOE_HARPOON), "turret": [-30, -4]},
            "harpoon-right": {"gun": FLOE_HARPOON, "turret": [30, -4]},
        },
        "stages": stages(
            [
                volley.burst("harpoon-left", 2.6, 3, 0.16, RED, 1),
                volley.burst("harpoon-right", 2.6, 3, 0.16, RED, 2.3),
            ],
            [
                [volley.fan("core", 3, 3, 18, MAGENTA, 1.8)],
                [volley.aimed("core", 2.2, 3, 12, MAGENTA, 0.6)],
                [
                    volley.ring("core", 1.7, 10, 0, BLUE, 0.4),
                    volley.fan("core", 2.6, 5, 14, MAGENTA, 1.2),
                ],
            ],
        ),
    }
)
