# Copyright (c) 2026 Renaud Guillon
"""The Glacier Colossus (2-4's final boss, specs/bosses/final/2-4-glacier-colossus.md).

The final boss of 2-4. Offsets in px from the boss's centre, X right and Y up (its nose
points down, at -Y). Six parts: two cutter lasers out on its beam, two ore cannons and a heat sink
at its bow (these three shield the core), and a missile pod on its stern.
"""

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
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


def fpart(part_id: str, at: list[Any], radius: float, health: float, options: Any = None) -> Any:
    """Return a final boss's part.

    Drops a bonus 60 % of the time (FB-GLACIER-COLOSSUS-17, `part_drop_chance`).
    """
    extra = {} if options == None else options
    return part(part_id, at, radius, health, merge({"drop": 0.6}, extra))


RED = bullet("red", 190)
MAGENTA = bullet("magenta", 185)
# The ore cannons' shells: big, a little slower than the stage bullets (FB-GLACIER-COLOSSUS-10).
ORE = bullet("orange", 160, 6)

# Where the left (-X) cutter and ore cannon sit (mirrored on the right).
COLOSSUS_CUTTER = [-80, -10]
COLOSSUS_ORE = [-44, -28]
# The heat sink at the bow (FB-GLACIER-COLOSSUS-11) and the missile pod on the stern
# (FB-GLACIER-COLOSSUS-12).
COLOSSUS_HEAT_SINK = [0, -48]
COLOSSUS_POD = [0, 46]

# The guns' muzzles (FB-GLACIER-COLOSSUS-03): the tips of the barrels its model draws, from the
# boss's centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).

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

# 2-4: a giant mining ship with glowing heat vents; cutter lasers on turrets aim from its beam
# (FB-GLACIER-COLOSSUS-09), ore cannons fire fans of big shells, a missile pod covers its stern, and
# a heat sink at its bow (no weapon) shields the core with the ore cannons. The ground slows to
# x0.3.
_GLACIER_COLOSSUS = record({
    "id": "glacier-colossus",
    # Angry after each destroyed part (phase 7 review, D-063, FB-GLACIER-COLOSSUS-14).
    "rage": rage.flower(6, "red", "magenta"),
    # Its core, six parts and points (FB-GLACIER-COLOSSUS-17).
    "stats": stats({
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
    }),
    # Where it stops and how it moves in place (FB-GLACIER-COLOSSUS-08).
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
    # The parts' volleys, then the core's pattern per stage (FB-GLACIER-COLOSSUS-13).
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
})

# Its hidden weapons (boss transformations, D-224): at transformation 1 its flank armour bursts off,
# baring a dark metal frame, and a pair of ring emitters unfold (FB-GLACIER-COLOSSUS-15); at
# transformation 2 its shell bursts off, baring a dark metal frame, and a pair of sweeping lasers
# unfold (FB-GLACIER-COLOSSUS-16). The regions it sheds: FB-GLACIER-COLOSSUS-07.
GLACIER_COLOSSUS = with_weapons(
    _GLACIER_COLOSSUS,
    [
        hidden_weapon("orb-left", "orb", [-36, 53], 12, 1520, 1, "orange", 1.2, 23.8),
        hidden_weapon("orb-right", "orb", [36, 53], 12, 1520, 1, "orange", 2.0, 23.8),
        hidden_weapon("sweeper-left", "sweeper", [-25, 29], 9, 1900, 2, "orange", 1.2, 23.1),
        hidden_weapon("sweeper-right", "sweeper", [25, 29], 9, 1900, 2, "orange", 2.0, 23.1),
    ],
    [
        # FB-GLACIER-COLOSSUS-07 (D-254): the plating of the stern deck either side of the upper
        # deck (its plan from the upper deck's edge to the rim; the ring emitters under it), and the
        # ridged shell along the upper deck (its plan, a little wider than the shell at the
        # sweepers).
        armour_region(
            "flanks",
            1,
            [[31, 34], [58, 34], [44, 66], [21, 77], [10, 77], [10, 61], [24, 57]],
            "wing",
        ),
        armour_region(
            "wings",
            2,
            [
                [0, -6],
                [15, 0],
                [23, 13],
                [28, 26],
                [23, 39],
                [15, 52],
                [0, 58],
                [-15, 52],
                [-23, 39],
                [-28, 26],
                [-23, 13],
                [-15, 0],
            ],
            "wing",
            None,
            False,
        ),
    ],
)
