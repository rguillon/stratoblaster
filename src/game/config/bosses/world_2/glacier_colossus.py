"""The Glacier Colossus (P08-R10, 2-4)

The Glacier level's final boss. Offsets in px from the boss's centre, X right and Y up (its nose
points down, at -Y). Six parts: two cutter lasers out on its beam, two ore cannons and a heat sink
at its bow (these three shield the core), and a missile pod on its stern.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import (
    bullet,
    cells,
    mirror,
    part,
    stages,
    stats,
    twin,
    volley,
)
from game.config.bosses.boss_rage import rage
from game.config.record import merge, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


def fpart(part_id: str, at: list[Any], radius: float, health: float, options: Any = None) -> Any:
    """A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`)."""
    extra = {} if options == None else options  # noqa: E711
    return part(part_id, at, radius, health, merge({"drop": 0.6}, extra))


RED = bullet("red", 190)
MAGENTA = bullet("magenta", 185)
# The ore cannons' shells: big, a little slower than the stage bullets.
ORE = bullet("orange", 160, 6)

# Where the left (-X) cutter and ore cannon sit (mirrored on the right).
COLOSSUS_CUTTER = [-80, -10]
COLOSSUS_ORE = [-44, -28]
# The heat sink at the bow and the missile pod on the stern.
COLOSSUS_HEAT_SINK = [0, -48]
COLOSSUS_POD = [0, 46]

# The guns' muzzles: the tips of the barrels its model draws, from the boss's centre, X right,
# Y up, and height above the playfield (see `BossDesign.guns`).

# The left cutter's laser emitter (mirrored on the right).
COLOSSUS_CUTTER_LASER = [[-80, -42, 6]]
# The left ore cannon's two fat barrels (mirrored on the right).
COLOSSUS_ORE_GUNS = twin(-44, -50, 12, 3.5)
# The core's twin guns on the bridge's front, over the heat sink.
COLOSSUS_CORE_GUNS = twin(9, -30, 22)
# The core's rings leave from the top of its heat stack.
COLOSSUS_STACK = [[0, 6, 32]]
# The missile pod's four cells.
COLOSSUS_CELLS = cells([-5.5, 5.5], [41, 51], 24)

# P08-R10, 2-4: a giant mining ship with glowing heat vents; cutter lasers on turrets aim from its
# beam, ore cannons fire fans of big shells, a missile pod covers its stern, and a heat sink at its
# bow (no weapon) shields the core with the ore cannons. The ground slows to ×0.3.
GLACIER_COLOSSUS = record(
    {
        "id": "glacier-colossus",
        # Angry after each destroyed part (phase 7 review, D-063).
        "rage": rage.flower(6, "red", "magenta"),
        "stats": stats(
            {
                "id": "glacier-colossus",
                "name": "Glacier Colossus",
                "size": 5.5,
                "coreRadius": 22,
                "coreHealth": 4400,
                "points": 14000,
                "groundSpeed": 0.3,
                "coreDrop": 1,
                "parts": [
                    fpart("cutter-left", list(COLOSSUS_CUTTER), 15, 1200, {"shields": False}),
                    fpart(
                        "cutter-right",
                        [-COLOSSUS_CUTTER[0], COLOSSUS_CUTTER[1]],
                        15,
                        1200,
                        {"shields": False},
                    ),
                    fpart("ore-left", list(COLOSSUS_ORE), 15, 1700),
                    fpart("ore-right", [-COLOSSUS_ORE[0], COLOSSUS_ORE[1]], 15, 1700),
                    fpart("heat-sink", list(COLOSSUS_HEAT_SINK), 16, 1900),
                    fpart("missile-pod", list(COLOSSUS_POD), 14, 900, {"shields": False}),
                ],
            }
        ),
        "stopFraction": 0.75,
        "sway": {"amplitude": 30, "period": 10},
        "bob": {"amplitude": 6, "period": 5},
        "guns": {
            "core": {"gun": COLOSSUS_CORE_GUNS, "ring": COLOSSUS_STACK},
            "cutter-left": {
                "laser": COLOSSUS_CUTTER_LASER,
                "turret": list(COLOSSUS_CUTTER),
                "turretLaser": True,
            },
            "cutter-right": {
                "laser": mirror(COLOSSUS_CUTTER_LASER),
                "turret": [-COLOSSUS_CUTTER[0], COLOSSUS_CUTTER[1]],
                "turretLaser": True,
            },
            "ore-left": {"gun": COLOSSUS_ORE_GUNS},
            "ore-right": {"gun": mirror(COLOSSUS_ORE_GUNS)},
            "missile-pod": {"missile": COLOSSUS_CELLS},
        },
        "stages": stages(
            [
                volley.laser("cutter-left", 6.5, 1.4, 2),
                volley.laser("cutter-right", 6.5, 1.4, 5.25),
                volley.fan("ore-left", 2.6, 3, 18, ORE, 0.9),
                volley.fan("ore-right", 2.6, 3, 18, ORE, 2.2),
                volley.missiles("missile-pod", 5.5, 2, 30, 3),
            ],
            [
                [volley.aimed("core", 2.8, 1, 0, RED, 1.4)],
                [volley.aimed("core", 2.4, 3, 12, RED, 0.8)],
                [volley.burst("core", 2.4, 4, 0.13, RED, 0.6)],
                [volley.ring("core", 2.2, 8, 0, MAGENTA, 0.6)],
                [
                    volley.fan("core", 2.4, 7, 12, RED, 0.6),
                    volley.burst("core", 2.8, 3, 0.13, RED, 1.2),
                ],
                [
                    volley.ring("core", 1.8, 10, 7, MAGENTA, 0.5),
                    volley.aimed("core", 2.6, 1, 0, RED, 1.2),
                ],
                [
                    volley.ring("core", 1.3, 14, 9, MAGENTA, 0.4),
                    volley.ring("core", 1.3, 14, -11, RED, 1.05),
                ],
            ],
        ),
    }
)
