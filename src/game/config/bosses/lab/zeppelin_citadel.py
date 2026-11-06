# Copyright (c) 2026 Renaud Guillon
"""The Lab's L-13 final boss, the Zeppelin Citadel (specs/bosses/lab/L-13-zeppelin-citadel.md).

Three long gas envelopes side by side carrying a fortified town slung under them: a walled gondola
deck of rooftops, towers and walkways, its bow and stern jutting out from under the envelopes.
Lab boss: in the dev viewer only (no level brings it in). It fires orderly volleys from its bow
towers, its stern silos and the turrets on its outer envelopes. At its first transformation the two
outer envelopes cast off and drift out wide on telescoping booms (it changes shape, BOSS-45), their
mooring cables stretching, baring the town's flanks and a sweeper on each; at its second the middle
envelope deflates and bursts, dropping the citadel's cover off a pair of gatlings and a mortar on
the centre line: close, desperate flak.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount, missile_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, slide
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# FB-ZEPPELIN-CITADEL-01: the town gondola's outline (its deck seen from above, bow down the
# screen), its keel's and its deck's height.
TOWN = [
    [0, -68],
    [22, -60],
    [40, -46],
    [46, -36],
    [46, 42],
    [38, 53],
    [24, 60],
    [-24, 60],
    [-38, 53],
    [-46, 42],
    [-46, -36],
    [-40, -46],
    [-22, -60],
]
DECK = 8
# The envelopes (FB-ZEPPELIN-CITADEL-05): `[x, radius, nose y, tail y, centre height]` each, the
# right outer one (its mirror on the left) and the middle one.
OUTER = [33, 12.5, -38, 42, 26]  # type: list[Any]
MIDDLE = [0, 16, -48, 46, 30]
# How far the outer envelopes drift out as they cast off: `[dx, dy, dz]` px, the right one.
DRIFT = [28.0, 2.0, 3.0]
# The telescoping booms each outer envelope rides out on: their y, their inner and outer x at rest
# (inside the gondola's hull), their low and high edge.
BOOM_YS = [-22, 26]
BOOM_X = [12, 40]
BOOM_H = [3.5, 6.5]

# The bow towers (FB-ZEPPELIN-CITADEL-03): their centre, radius and top (their crowns are parts).
BOW_TOWER = [24, -48]
BOW_RADIUS = 7
BOW_TOP = 16
# The stern silos: their centre, half width and top.
STERN_SILO = [24, 52]
STERN_HALF = 6
STERN_TOP = 13
# The keep at the bow's tip (the core's gun) and the stern hatch over the core's rotor.
KEEP_GUN_AT = [0, -57]
KEEP_TOP = 14
ROTOR_AT = [0, 54]
ROTOR_TOP = 11

# The guns: a twin turret on each outer envelope's back, three barrels on the bow towers, a missile
# block on each stern silo, and the core's: a five-barrelled turret on the bow keep and a rotor on
# the stern deck, under a hatch until its last stage.
DORSAL_AT = [OUTER[0], -8]
DORSAL_HEIGHT = OUTER[4] + OUTER[1] + 2
DORSAL_GUN = {"size": 4.8, "barrels": 2, "gap": 3.1, "bore": 1.2, "length": 8}
BOW_GUN_HEIGHT = BOW_TOP + 3
BOW_GUN = {"size": 5, "barrels": 3, "gap": 1.2, "bore": 1.1, "length": 7.5}
SILO_HEIGHT = STERN_TOP + 2.5
KEEP_GUN = {"size": 6, "barrels": 5, "gap": 1, "bore": 1, "length": 8}
KEEP_ROTOR = {"size": 5.5, "barrels": 16, "layout": "ring", "bore": 0.7, "length": 3.4}

GOLD = bullet("orange", 180)
RED = bullet("red", 190)
MAGENTA = bullet("magenta", 175)


def fpart(part_id: str, at: list[Any], radius: float, health: float) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    return part(part_id, at, radius, health, {"drop": 0.6})


def outer_outline() -> list[list[float]]:
    """Return the right outer envelope's outline as it rests (seen from above), fins included."""
    x = OUTER[0]
    r = OUTER[1]
    return [
        [x - r + 1, OUTER[2] - 2],
        [x + r - 1, OUTER[2] - 2],
        [x + r + 1, OUTER[3] - 6],
        [x + r + 1, OUTER[3] + 5],
        [x - r - 1, OUTER[3] + 5],
        [x - r - 1, OUTER[3] - 6],
    ]


def middle_outline() -> list[list[float]]:
    """Return the middle envelope's outline (seen from above), fins included."""
    r = MIDDLE[1] + 1
    return [
        [-r + 3, MIDDLE[2] - 2],
        [r - 3, MIDDLE[2] - 2],
        [r, MIDDLE[2] + 14],
        [r, MIDDLE[3] + 4],
        [-r, MIDDLE[3] + 4],
        [-r, MIDDLE[2] + 14],
    ]


_ZEPPELIN_CITADEL = record({
    "id": "zeppelin-citadel",
    # Its points, its core's drop and its parts' drops (FB-ZEPPELIN-CITADEL-13).
    "stats": stats({
        "id": "zeppelin-citadel",
        "name": "Zeppelin Citadel",
        "size": 5,
        "coreRadius": 20,
        "coreHealth": 2800,
        "points": 10500,
        "groundSpeed": 0.4,
        "coreDrop": 1,
        "parts": [
            fpart("dorsal-left", [-DORSAL_AT[0], DORSAL_AT[1]], 10, 950),
            fpart("dorsal-right", DORSAL_AT, 10, 950),
            fpart("bow-left", [-BOW_TOWER[0], BOW_TOWER[1]], 10, 1150),
            fpart("bow-right", BOW_TOWER, 10, 1150),
            fpart("stern-left", [-STERN_SILO[0], STERN_SILO[1]], 10, 1250),
            fpart("stern-right", STERN_SILO, 10, 1250),
        ],
    }),
    # Where it stops and how it moves in place (FB-ZEPPELIN-CITADEL-06): a slow, stately drift.
    "stopFraction": 0.74,
    "sway": {"amplitude": 30, "period": 12},
    "bob": {"amplitude": 6, "period": 6},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-ZEPPELIN-CITADEL-03).
    "mounts": [
        gun_mount(
            "dorsal-left", "dorsal-left", [-DORSAL_AT[0], DORSAL_AT[1]], DORSAL_HEIGHT, DORSAL_GUN
        ),
        gun_mount("dorsal-right", "dorsal-right", DORSAL_AT, DORSAL_HEIGHT, DORSAL_GUN),
        gun_mount("bow-left", "bow-left", [-BOW_TOWER[0], BOW_TOWER[1]], BOW_GUN_HEIGHT, BOW_GUN),
        gun_mount("bow-right", "bow-right", BOW_TOWER, BOW_GUN_HEIGHT, BOW_GUN),
        missile_mount("stern-left", "stern-left", [-STERN_SILO[0], STERN_SILO[1]], SILO_HEIGHT, 4),
        missile_mount("stern-right", "stern-right", STERN_SILO, SILO_HEIGHT, 4),
        gun_mount("keep-gun", "core", KEEP_GUN_AT, KEEP_TOP, KEEP_GUN),
        gun_mount("keep-rotor", "core", ROTOR_AT, ROTOR_TOP, KEEP_ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-ZEPPELIN-CITADEL-08): orderly
    # volleys (the dorsal turrets' aimed pairs, the bow towers' fans straight down, the stern
    # silos' homing pairs, the keep's single shots and spreads), ending in the stern rotor's
    # rings of 16.
    "stages": stages(
        [
            volley.aimed("dorsal-left", 2.2, 2, 6, RED, 0.9),
            volley.aimed("dorsal-right", 2.2, 2, 6, RED, 2.0),
            volley.fan("bow-left", 2.8, 5, 10, GOLD, 1.4),
            volley.fan("bow-right", 2.8, 5, 10, GOLD, 2.8),
            volley.missiles("stern-left", 7, 2, 30, 3),
            volley.missiles("stern-right", 7, 2, 30, 6.5),
        ],
        [
            [volley.aimed("core", 2.6, 1, 0, RED, 1.4)],
            [volley.fan("core", 2.6, 5, 12, GOLD, 1)],
            [volley.aimed("core", 2.4, 3, 8, RED, 1)],
            [volley.burst("core", 2.4, 4, 0.12, MAGENTA, 0.8)],
            [volley.fan("core", 2.6, 7, 10, GOLD, 0.6)],
            [
                volley.aimed("core", 2.6, 5, 9, RED, 0.6),
                volley.burst("core", 3.2, 3, 0.14, MAGENTA, 1.8),
            ],
            [
                volley.ring("core", 1.4, 16, 11.25, GOLD, 0.4),
                volley.fan("core", 2.6, 5, 12, RED, 1.2),
            ],
        ],
    ),
})

# Where the sweepers stand on the town's flanks (bared once the outer envelopes have drifted off:
# FB-ZEPPELIN-CITADEL-10), and the gatlings and the mortar on its central plaza (bared once the
# middle envelope has burst: FB-ZEPPELIN-CITADEL-11), and their pods' base and top.
SWEEPER_AT = [OUTER[0], 8]
GATLING_AT = [8, -24]
MORTAR_AT = [0, 10]
POD = [DECK, DECK + 3.5]

# Its transformations: once both dorsal turrets are gone its outer envelopes cast off and drift out
# wide, a sweeper rising on each of the town's bared flanks; once both bow towers are gone the
# middle envelope deflates and bursts, baring a pair of gatlings and a mortar on its plaza. The
# hatch over the stern rotor bursts as the rotor comes into use, in its last stage (BOSS-58).
ZEPPELIN_CITADEL = with_weapons(
    merge(
        _ZEPPELIN_CITADEL,
        {"transformParts": [["dorsal-left", "dorsal-right"], ["bow-left", "bow-right"]]},
    ),
    [
        hidden_weapon(
            "sweeper-left",
            "sweeper",
            [-SWEEPER_AT[0], SWEEPER_AT[1]],
            8,
            1000,
            1,
            "red",
            1.2,
            POD,
        ),
        hidden_weapon("sweeper-right", "sweeper", SWEEPER_AT, 8, 1000, 1, "red", 2.6, POD),
        hidden_weapon(
            "gatling-left",
            "gatling",
            [-GATLING_AT[0], GATLING_AT[1]],
            8,
            1250,
            2,
            "magenta",
            1.2,
            POD,
        ),
        hidden_weapon("gatling-right", "gatling", GATLING_AT, 8, 1250, 2, "magenta", 2.0, POD),
        hidden_weapon("mortar", "mortar", MORTAR_AT, 10, 1250, 2, "orange", 1.6, [DECK, DECK + 4]),
    ],
    concat(
        moving_region(
            "outer-envelope",
            1,
            outer_outline(),
            slide([[0, 0, 0], DRIFT]),
            None,
            [OUTER[4] - OUTER[1] - 1, 1000],
        ),
        [
            armour_region("middle-envelope", 2, middle_outline(), "shell", [14, 1000], False),
            armour_region(
                "rotor-hatch",
                None,
                [
                    [
                        ROTOR_AT[0] + 6 * math.cos(k * math.pi / 4 + math.pi / 8),
                        ROTOR_AT[1] + 6 * math.sin(k * math.pi / 4 + math.pi / 8),
                    ]
                    for k in range(8)
                ],
                "ring",
                None,
                False,
                "keep-rotor",
            ),
        ],
    ),
)
