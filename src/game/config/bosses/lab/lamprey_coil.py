# Copyright (c) 2026 Renaud Guillon
"""The Lab's L-5 mini boss, the Lamprey Coil (specs/bosses/lab/L-5-lamprey-coil.md).

A serpentine lamprey lying coiled in an S across the screen, its round sucker mouth at its front.
Lab boss: in the dev viewer only (no level brings it in). Offsets in px from the boss's centre, X
right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# MB-LAMPREY-COIL-01: the body's centre line, from the tail's tip to the head, `[x, y, radius]`
# (its girth there). An S lying across the screen: the tail at the left, a lobe dipping towards
# the player, a lobe rising behind, the neck hooking back down to the mouth.
LAMPREY_SPINE = [
    [-58, 8, 5.4],
    [-50, -2, 6.6],
    [-38, -11, 7.8],
    [-23, -14, 9],
    [-9, -9, 9.8],
    [2, 2, 10.3],
    [14, 13, 10.8],
    [29, 18, 11.2],
    [42, 12, 11.5],
    [48, -2, 11.8],
    [43, -17, 12],
    [31, -28, 12.2],
    [17, -34, 12.6],
]
# The height of the body's centre line over the playfield (its top is that plus its girth).
LAMPREY_AXIS = 7
# The sucker mouth's centre and radius (MB-LAMPREY-COIL-02), in front of the head.
LAMPREY_MOUTH = [7, -39]
LAMPREY_MOUTH_RADIUS = 12.5
# The top of the mouth's throat: the rotor stands in it.
LAMPREY_THROAT = 10.5
# The stretch of the back the dorsal armour covers (MB-LAMPREY-COIL-05): between these points of
# the centre line, `ARMOUR_HALF` px either side of it.
ARMOUR_SPAN = [3, 7]
ARMOUR_HALF = 9

RED = bullet("red", 185)
PURPLE = bullet("purple", 180)
ORANGE = bullet("orange", 175)

# The gill clusters' twin-barrelled turrets, firing their aimed bursts in turn (MB-LAMPREY-COIL-03).
GILL_GUN = {"size": 5, "barrels": 2, "gap": 2.8, "bore": 1.1, "length": 7}
# The tail stinger's rotor: four barrels, spinning its own small spiral against the mouth's.
STINGER_ROTOR = {"size": 4, "barrels": 4, "layout": "ring", "bore": 1, "length": 4.5}
# The mouth rotor: ten barrels in the sucker's throat, its spirals (the boss's signature).
MOUTH_ROTOR = {"size": 4.5, "barrels": 10, "layout": "ring", "bore": 0.8, "length": 4}
# The crown turret on the back of the head: its aimed shots and bursts.
CROWN_GUN = {"size": 4.5, "barrels": 3, "gap": 1.2, "bore": 1, "length": 6}


def _band(spine: list[Any], span: list[int], half: float) -> list[list[float]]:
    """Return the outline of the band `half` px either side of `spine` between `span`'s points.

    Its left edge from the first point to the last, then its right edge back.
    """
    left: list[list[float]] = []
    right: list[list[float]] = []
    n = len(spine)
    for i in range(span[0], span[1] + 1):
        a = spine[max(0, i - 1)]
        b = spine[min(n - 1, i + 1)]
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        d = math.hypot(dx, dy)
        nx = -dy / d
        ny = dx / d
        p = spine[i]
        left.append([p[0] + nx * half, p[1] + ny * half])
        right.append([p[0] - nx * half, p[1] - ny * half])
    result: list[list[float]] = []
    result.extend(left)
    result.extend([right[len(right) - 1 - k] for k in range(len(right))])
    return result


# MB-LAMPREY-COIL-05: the dorsal armour's outline (the region it sheds).
ARMOUR_OUTLINE = _band(LAMPREY_SPINE, ARMOUR_SPAN, ARMOUR_HALF)

# MB-LAMPREY-COIL-07: three parts, all shielding the core.
_LAMPREY_COIL = record({
    "id": "lamprey-coil",
    # Its points and its parts' drops (MB-LAMPREY-COIL-11).
    "stats": stats({
        "id": "lamprey-coil",
        "name": "Lamprey Coil",
        "size": 3.5,
        "coreRadius": 18,
        "coreHealth": 1600,
        "points": 5000,
        "groundSpeed": 0.7,
        "parts": [
            part("gill-left", [-27, -26], 12, 780),
            part("gill-right", [40, 28], 12, 780),
            part("stinger", [-64, 12], 11, 820),
        ],
    }),
    # Where it stops and how it moves in place (MB-LAMPREY-COIL-06).
    "stopFraction": 0.73,
    "sway": {"amplitude": 55, "period": 6},
    "bob": {"amplitude": 9, "period": 2.6},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-LAMPREY-COIL-03): a twin-barrelled turret on each gill cluster,
    # a four-barrelled rotor on the stinger's bulb, and the core's: the ten-barrelled rotor in its
    # sucker mouth (its spirals) and the crown turret on the back of its head (its aimed shots and
    # bursts).
    "mounts": [
        gun_mount("gill-left", "gill-left", [-27, -26], 14.6, GILL_GUN),
        gun_mount("gill-right", "gill-right", [40, 28], 14.6, GILL_GUN),
        gun_mount("stinger", "stinger", [-64, 12], 11, STINGER_ROTOR),
        gun_mount("mouth", "core", LAMPREY_MOUTH, LAMPREY_THROAT, MOUTH_ROTOR),
        gun_mount("crown", "core", [26, -30], 19, CROWN_GUN),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-LAMPREY-COIL-08): the gills weave
    # aimed bursts in turn, the stinger spins its small spiral one way, the mouth its big one, a
    # new turn and pace at every stage. BOSS-58: rings of 10 and 4, a bullet per barrel; the crown's
    # aimed fans 12° apart.
    "stages": stages(
        [
            volley.burst("gill-left", 2.6, 3, 0.16, RED, 1),
            volley.burst("gill-right", 2.6, 3, 0.16, RED, 2.3),
            volley.ring("stinger", 0.9, 4, -21, ORANGE, 0.5),
        ],
        [
            [
                volley.ring("core", 1.6, 10, 12, PURPLE, 0.8),
                volley.aimed("core", 3, 1, 0, RED, 1.6),
            ],
            [
                volley.ring("core", 1.4, 10, -15, PURPLE, 0.6),
                volley.aimed("core", 2.6, 3, 12, RED, 1.2),
            ],
            [
                volley.ring("core", 1.2, 10, 18, PURPLE, 0.5),
                volley.burst("core", 2.4, 3, 0.15, RED, 1),
            ],
            [
                volley.ring("core", 0.8, 10, 8, PURPLE, 0.4),
                volley.burst("core", 2.2, 4, 0.13, RED, 1),
            ],
        ],
    ),
})

# Where the sweepers stand: on the back's centre line, either side of the middle of the S.
SWEEPER_SPOTS = [[-9, -9], [14, 13]]

# Its transformation (MB-LAMPREY-COIL-10): once two of its parts are gone, its dorsal armour bursts
# off the middle of the S, baring a dark metal lattice, and a pair of sweepers unfold on its back.
LAMPREY_COIL = with_weapons(
    _LAMPREY_COIL,
    [
        hidden_weapon("sweeper-left", "sweeper", SWEEPER_SPOTS[0], 7, 660, 1, "purple", 1.2, 19.5),
        hidden_weapon("sweeper-right", "sweeper", SWEEPER_SPOTS[1], 7, 660, 1, "purple", 3.4, 19.5),
    ],
    [
        # MB-LAMPREY-COIL-05: the dorsal armour along the middle of the S (not mirrored: the S is
        # turned, not mirrored, about its centre).
        armour_region("back", 1, ARMOUR_OUTLINE, "shell", None, False),
    ],
)
