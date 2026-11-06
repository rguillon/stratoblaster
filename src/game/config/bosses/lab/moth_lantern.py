# Copyright (c) 2026 Renaud Guillon
"""The Moth Lantern, the Lab's L-3 mini boss (specs/bosses/lab/L-3-moth-lantern.md).

Lab boss: in the dev viewer only, no level brings it in. A huge moth: broad, soft wings folded
back at rest, an eye-spot gun on each forewing, a long glowing lantern abdomen behind that lobs big,
slow spore shells bursting into rings. Once both eye-spots are gone its wings swing open wide (it
changes shape, BOSS-45) and a lance rides in on each forewing.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, bursting, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import move_point, moving_region, swing
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


MAGENTA = bullet("magenta", 175)
PURPLE = bullet("purple", 185)
# Its spore flak (MB-MOTH-LANTERN-08): a big, slow shell bursting into a ring of 10.
SPORE = bursting("purple", 80, 8, [1.5, 10, bullet("magenta", 140)])

# MB-MOTH-LANTERN-05: its right forewing and hindwing as drawn, spread wide open (their pose once
# it has transformed); at rest each is swung back about the front of its root, the forewing over
# the hindwing. The model draws them from these outlines.
FOREWING = [
    [12, -22],
    [28, -30],
    [46, -35],
    [64, -38],
    [78, -38],
    [85, -33],
    [84, -24],
    [80, -14],
    [74, -6],
    [66, -1],
    [50, 0],
    [34, -1],
    [20, -3],
    [13, -6],
]
HINDWING = [
    [13, -6],
    [30, -3],
    [48, 0],
    [60, 4],
    [66, 12],
    [64, 24],
    [56, 34],
    [44, 40],
    [32, 40],
    [22, 34],
    [16, 22],
    [13, 10],
]
# Their hinges `[x, y, height]` and how far back they rest folded (degrees about the vertical).
FORE_PIVOT = [12.0, -22.0, 6.0]
HIND_PIVOT = [13.0, -6.0, 4.0]
FORE_REST = 50
HIND_REST = 20
FORE_SWING = swing(FORE_PIVOT, "up", [FORE_REST, 0])
HIND_SWING = swing(HIND_PIVOT, "up", [HIND_REST, 0])
# The heights the wings are drawn between (their membranes' bottom, waist and top).
FORE_Y = [6, 7, 8.2]
HIND_Y = [4.4, 5.1, 6]

# The eye-spot on the right forewing as drawn, and the lance's pod on it (open).
EYE_SPOT = [52, -20]
LANCE_SPOT = [62, -24]


def _tenth(value: float) -> float:
    """`value` rounded to a tenth."""
    return math.floor(value * 10 + 0.5) / 10


def folded(spot: list[Any]) -> list[float]:
    """Where `spot` of the right forewing as drawn lies with the wing folded back, at rest."""
    q = move_point(FORE_SWING, FORE_REST, [spot[0], spot[1], 0])
    return [_tenth(q[0]), _tenth(q[1])]


# The eye-spot guns stand on the folded forewings (MB-MOTH-LANTERN-03).
EYE = folded(EYE_SPOT)
EYE_HEIGHT = 12.4

# The eye-spot guns' turrets: three barrels side by side, sweeping their fans (MB-MOTH-LANTERN-03).
EYE_GUN = {"size": 4.5, "barrels": 3, "gap": 1.2, "bore": 1.1, "length": 7}
# The lantern's spore mortar: one fat barrel in a cradle on a turntable.
SPORE_MORTAR = {"size": 6, "barrels": 1, "bore": 3.4, "length": 4.5, "style": "mortar", "axis": 0.8}

# Where the core's rotor rises from its thorax, under a hatch until its last stage.
ROTOR_AT = [0, -12]

_MOTH_LANTERN = record({
    "id": "moth-lantern",
    # Its points and its parts' drops (MB-MOTH-LANTERN-11).
    "stats": stats({
        "id": "moth-lantern",
        "name": "Moth Lantern",
        "size": 4,
        "coreRadius": 16,
        "coreHealth": 1150,
        "points": 4000,
        "groundSpeed": 0.5,
        "parts": [
            part("eye-left", [-EYE[0], EYE[1]], 12, 650),
            part("eye-right", [EYE[0], EYE[1]], 12, 650),
            part("lantern", [0, 42], 15, 720),
        ],
    }),
    # Where it stops and how it moves in place (MB-MOTH-LANTERN-06): a slow, drifting flutter.
    "stopFraction": 0.73,
    "sway": {"amplitude": 55, "period": 9},
    "bob": {"amplitude": 10, "period": 2.6},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-MOTH-LANTERN-03): a fan turret on each eye-spot, the spore mortar
    # on the lantern's back, and the core's: the maw turret on its head (its aimed shots and
    # bursts), the rotor on its thorax (its last ring).
    "mounts": [
        gun_mount("eye-left", "eye-left", [-EYE[0], EYE[1]], EYE_HEIGHT, EYE_GUN),
        gun_mount("eye-right", "eye-right", [EYE[0], EYE[1]], EYE_HEIGHT, EYE_GUN),
        gun_mount("lantern", "lantern", [0, 34], 13.2, SPORE_MORTAR),
        gun_mount(
            "maw",
            "core",
            [0, -38],
            8.4,
            {"size": 4.5, "barrels": 3, "gap": 1.1, "bore": 1, "length": 6},
        ),
        gun_mount(
            "thorax-rotor",
            "core",
            ROTOR_AT,
            13.6,
            {"size": 4.5, "barrels": 12, "layout": "ring", "bore": 0.8, "length": 3.2},
        ),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-MOTH-LANTERN-08): the eye-spots'
    # fans cross under it, 12 degrees apart (BOSS-58); the lantern lobs its spore flak.
    "stages": stages(
        [
            volley.fan("eye-left", 3, 5, 12, MAGENTA, 1, -8),
            volley.fan("eye-right", 3, 5, 12, MAGENTA, 2.5, 8),
            volley.aimed("lantern", 2.8, 1, 0, SPORE, 1.8),
        ],
        [
            [volley.aimed("core", 3, 1, 0, PURPLE, 1.4)],
            [volley.aimed("core", 2.6, 3, 10, PURPLE, 0.8)],
            [volley.burst("core", 2, 4, 0.14, PURPLE, 0.6)],
            [
                volley.ring("core", 1.6, 12, 8, PURPLE, 0.4),
                volley.aimed("core", 2.4, 1, 0, MAGENTA, 1),
            ],
        ],
    ),
})

# Its transformation (BOSS-45, MB-MOTH-LANTERN-10): once both eye-spots are gone its wings swing
# open wide, and a lance rides in on each forewing. The thorax hatch over its rotor bursts as the
# rotor comes into use, in its last stage (BOSS-58).
MOTH_LANTERN = with_weapons(
    merge(_MOTH_LANTERN, {"transformParts": [["eye-left", "eye-right"]]}),
    [
        hidden_weapon(
            "lance-left",
            "lance",
            [-LANCE_SPOT[0], LANCE_SPOT[1]],
            8,
            580,
            1,
            "purple",
            1.2,
            [8, 11],
        ),
        hidden_weapon(
            "lance-right",
            "lance",
            [LANCE_SPOT[0], LANCE_SPOT[1]],
            8,
            580,
            1,
            "purple",
            2.0,
            [8, 11],
        ),
    ],
    concat(
        concat(
            moving_region("forewings", 1, FOREWING, FORE_SWING, None, [FORE_Y[0], 1000]),
            moving_region("hindwings", 1, HINDWING, HIND_SWING, None, [HIND_Y[0], 1000]),
        ),
        [
            armour_region(
                "rotor-hatch",
                None,
                [
                    [
                        ROTOR_AT[0] + 6.5 * math.cos(k * math.pi / 4),
                        ROTOR_AT[1] + 6.5 * math.sin(k * math.pi / 4),
                    ]
                    for k in range(8)
                ],
                "ring",
                None,
                False,
                "thorax-rotor",
            ),
        ],
    ),
)
