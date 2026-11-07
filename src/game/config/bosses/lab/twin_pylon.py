# Copyright (c) 2026 Renaud Guillon
"""The Twin Pylon, the Lab's L-7 final boss (specs/bosses/lab/L-7-twin-pylon.md).

Lab boss: in the dev viewer only, no level brings it in. Two tall lattice transmission pylons
standing side by side on a long base platform, a sagging energy conduit hung between their tops,
the core a capacitor block in the middle under it. It fights with electricity: lasers down from the
insulator stacks at the platform's ends and from the capacitor between the pylons, fast aimed
bursts from the coil heads on the pylons' tops, the two pylons firing in turn. Its first
transformation bares an orb at each end of the platform; its second a mortar either side of the
capacitor and a lance on the centre line, at its prow.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount, laser_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


BLUE = bullet("blue", 200)
PURPLE = bullet("purple", 185)
MAGENTA = bullet("magenta", 190)

# FB-TWIN-PYLON-01: the platform: its half length, its half depth, its deck's height; a prow on
# the centre line out to `PROW` (the lance's), and a rear annex back to `ANNEX` (the transformer's).
DECK_HALF = [80, 18]
DECK_TOP = 7
PROW = [12, -32]
ANNEX = [17, 38]
# A pylon (FB-TWIN-PYLON-02): its centre's X, its lattice's half width at its foot and at its top,
# its top's height; its cross-arm's height and how far out from the pylon it reaches either side.
PYLON_X = 40
PYLON_FOOT = 11
PYLON_HEAD = 4.5
PYLON_TOP = 36
ARM_HEIGHT = 29
ARM_REACH = 17
# The coil heads on the pylons' tops (the parts): their turrets' height.
COIL_TOP = 38.5
# The insulator stacks at the platform's ends (the parts): where they stand, their top.
INSULATOR_AT = [66, -6]
INSULATOR_TOP = 22
# The capacitor (the core): its half width, its front and back, its step's and its top's height.
CAP_HALF = 12
CAP_Y = [-20, 15]
CAP_STEP = 13
CAP_TOP = 21
# The conduit sags from the pylons' heads (`PYLON_TOP`) to `SAG` over the capacitor.
SAG = 27

# The coil heads' turrets: two barrels side by side, their fast aimed bursts (FB-TWIN-PYLON-03).
COIL_GUN = {"size": 4.6, "barrels": 2, "gap": 1.3, "bore": 1, "length": 7.5}
# The insulator stacks' laser emitters, firing straight down the screen.
INSULATOR_LASER = {"size": 4.5, "bore": 2.2, "length": 9}
# The transformer's rotor: eight barrels round its hub (its rings of sparks).
TRANSFORMER_ROTOR = {"size": 5, "barrels": 8, "layout": "ring", "bore": 0.9, "length": 4}
# The core's: the arc laser on the capacitor's top, between the pylons, on a turret following the
# player; the front turret on the capacitor's step (its aimed shots, fans and bursts); the
# capacitor's rotor (its last rings), under a hatch until then.
ARC_LASER_AT = [0, -4]
ARC_LASER = {"size": 5, "bore": 2.4, "length": 10, "turret": True}
FRONT_GUN_AT = [0, -15]
FRONT_GUN = {"size": 5, "barrels": 3, "gap": 1.2, "bore": 1.1, "length": 7}
CAP_ROTOR_AT = [0, 8]
CAP_ROTOR = {"size": 4.6, "barrels": 12, "layout": "ring", "bore": 0.85, "length": 3.6}
TRANSFORMER_AT = [0, 27]
TRANSFORMER_TOP = 14


def fpart(part_id: str, at: list[Any], radius: float, health: float) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    return part(part_id, at, radius, health, {"drop": 0.6})


# FB-TWIN-PYLON-07: five parts, all shielding the core.
_TWIN_PYLON = record({
    "id": "twin-pylon",
    # Its points, its core's drop and its parts' drops (FB-TWIN-PYLON-13).
    "stats": stats({
        "id": "twin-pylon",
        "name": "Twin Pylon",
        "size": 5,
        "coreRadius": 18,
        "coreHealth": 2200,
        "points": 9000,
        "groundSpeed": 0.6,
        "coreDrop": 1,
        "parts": [
            fpart("insulator-left", [-INSULATOR_AT[0], INSULATOR_AT[1]], 11, 800),
            fpart("insulator-right", [INSULATOR_AT[0], INSULATOR_AT[1]], 11, 800),
            fpart("coil-left", [-PYLON_X, 0], 12, 900),
            fpart("coil-right", [PYLON_X, 0], 12, 900),
            fpart("transformer", TRANSFORMER_AT, 13, 1000),
        ],
    }),
    # Where it stops and how it moves in place (FB-TWIN-PYLON-06): a wide, slow sway.
    "stopFraction": 0.74,
    "sway": {"amplitude": 35, "period": 10},
    "bob": {"amplitude": 5, "period": 4.5},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-TWIN-PYLON-03): a laser emitter on each insulator stack, a
    # twin-barrelled turret on each coil head, the transformer's rotor, and the core's: the arc
    # laser and the front turret on the capacitor, the capacitor's rotor behind them.
    "mounts": [
        laser_mount(
            "insulator-left",
            "insulator-left",
            [-INSULATOR_AT[0], INSULATOR_AT[1]],
            INSULATOR_TOP,
            INSULATOR_LASER,
        ),
        laser_mount(
            "insulator-right",
            "insulator-right",
            [INSULATOR_AT[0], INSULATOR_AT[1]],
            INSULATOR_TOP,
            INSULATOR_LASER,
        ),
        gun_mount("coil-left", "coil-left", [-PYLON_X, 0], COIL_TOP, COIL_GUN),
        gun_mount("coil-right", "coil-right", [PYLON_X, 0], COIL_TOP, COIL_GUN),
        gun_mount("transformer", "transformer", TRANSFORMER_AT, TRANSFORMER_TOP, TRANSFORMER_ROTOR),
        laser_mount("arc-laser", "core", ARC_LASER_AT, CAP_TOP, ARC_LASER),
        gun_mount("front-gun", "core", FRONT_GUN_AT, CAP_STEP, FRONT_GUN),
        gun_mount("cap-rotor", "core", CAP_ROTOR_AT, CAP_TOP, CAP_ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-TWIN-PYLON-08): the insulators'
    # lasers come down the screen from either end in turn, the coil heads' fast bursts of 4 at the
    # player in turn, the transformer's rings of 8 turning a little each time; the core's arc laser
    # from between the pylons, faster at every stage, and from its front turret aimed shots, fans
    # 12° apart and bursts, then the capacitor's rotor's rings of 12.
    "stages": stages(
        [
            volley.laser("insulator-left", 6, 1.4, 2),
            volley.laser("insulator-right", 6, 1.4, 5),
            volley.burst("coil-left", 2.4, 4, 0.08, BLUE, 1),
            volley.burst("coil-right", 2.4, 4, 0.08, BLUE, 2.2),
            volley.ring("transformer", 2.8, 8, 11.25, PURPLE, 1.6),
        ],
        [
            [volley.laser("core", 7, 1.5, 4)],
            [volley.laser("core", 6.5, 1.5, 3), volley.aimed("core", 2.6, 1, 0, MAGENTA, 1)],
            [volley.laser("core", 6, 1.5, 2.5), volley.fan("core", 2.6, 5, 12, MAGENTA, 1)],
            [volley.laser("core", 5.5, 1.5, 2), volley.burst("core", 2.2, 4, 0.1, MAGENTA, 0.8)],
            [volley.laser("core", 5, 1.6, 2), volley.ring("core", 2.2, 12, 7.5, BLUE, 0.6)],
            [
                volley.laser("core", 4.6, 1.6, 1.5),
                volley.ring("core", 1.8, 12, -9, BLUE, 0.5),
                volley.aimed("core", 2.4, 3, 12, MAGENTA, 1),
            ],
        ],
    ),
})

# Where the hidden weapons come out (FB-TWIN-PYLON-10, FB-TWIN-PYLON-11): the orbs at the
# platform's ends, behind the insulators, under their end cowlings; the mortars either side of the
# capacitor's front, under the bus covers; the lance at the prow, under its plate.
ORB_AT = [70, 10]
MORTAR_AT = [21, -10]
LANCE_AT = [0, -27]

# Its transformations (FB-TWIN-PYLON-10, FB-TWIN-PYLON-11): once both insulator stacks are gone the
# cowlings at the platform's ends burst off for a pair of orbs; once both coil heads are gone the
# bus covers either side of the capacitor and the prow plate burst off for a pair of mortars and a
# lance on the centre line. The capacitor's hatch bursts as its rotor comes into use (BOSS-58).
TWIN_PYLON = with_weapons(
    merge(
        _TWIN_PYLON,
        {"transformParts": [["insulator-left", "insulator-right"], ["coil-left", "coil-right"]]},
    ),
    [
        hidden_weapon("orb-left", "orb", [-ORB_AT[0], ORB_AT[1]], 9, 600, 1, "blue", 1.2, 8.5),
        hidden_weapon("orb-right", "orb", [ORB_AT[0], ORB_AT[1]], 9, 600, 1, "blue", 2.4, 8.5),
        hidden_weapon(
            "mortar-left", "mortar", [-MORTAR_AT[0], MORTAR_AT[1]], 8.5, 640, 2, "purple", 1.2, 9
        ),
        hidden_weapon(
            "mortar-right", "mortar", [MORTAR_AT[0], MORTAR_AT[1]], 8.5, 640, 2, "purple", 2.6, 9
        ),
        hidden_weapon("lance", "lance", LANCE_AT, 8, 650, 2, "blue", 1.8, 9),
    ],
    [
        armour_region(
            "end-cowls", 1, [[60, 1], [80, 1], [80, 18], [60, 18]], "shell", [DECK_TOP - 1, 12]
        ),
        armour_region(
            "bus-covers", 2, [[13, -19], [30, -19], [30, -1], [13, -1]], "shell", [DECK_TOP - 1, 11]
        ),
        armour_region(
            "prow-plate",
            2,
            [[-PROW[0], PROW[1]], [PROW[0], PROW[1]], [PROW[0], -19], [-PROW[0], -19]],
            "shell",
            [DECK_TOP - 1, 11],
            False,
        ),
        armour_region(
            "rotor-hatch",
            None,
            [
                [
                    CAP_ROTOR_AT[0] + 6 * math.cos(k * math.pi / 4 + math.pi / 8),
                    CAP_ROTOR_AT[1] + 6 * math.sin(k * math.pi / 4 + math.pi / 8),
                ]
                for k in range(8)
            ],
            "ring",
            None,
            False,
            "cap-rotor",
        ),
    ],
)
