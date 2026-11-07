# Copyright (c) 2026 Renaud Guillon
"""The Aegis Wing, the Lab's L-17 mini boss (specs/bosses/lab/L-17-aegis-wing.md).

Lab boss: in the dev viewer only, no level brings it in. A giant flying wing seen from above: a
tailless stealth wing, its leading edge swept straight back from a blunt nose to its tips, its
trailing edge a sawtooth, a low blended hump down its middle with its cockpit, and its engines
buried in it, their intakes on top. It picks at the player with sparse, precise shots (single
aimed shots from its intake guns, quick bursts from its nose gun). Once both intake guns are gone
it transforms: the rows of smooth skin panels on its outer wings flip over like tiles, one row
after another in a wave running in from the wingtip and from the root, each turning up a
bristling weapon face, and where the two waves meet the last panels fold open like petals on an
orb each side: from sparse precise shots to storms of rings.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import merge, record

# MB-AEGIS-WING-01: the wing's outline (its right half, from the nose round the tip to the tail on
# the centre line; mirrored): a straight swept leading edge, a sawtooth trailing edge.
WING = [  # type: list[list[float]]
    [0, -44],
    [5, -41.5],
    [60, 2],
    [61, 5],
    [59, 9],
    [44, 22],
    [32, 12],
    [20, 25],
    [10, 17],
    [0, 25],
]
# Its underside, its bevel's waist and its top.
WING_LOW = 3
WING_WAIST = 6.4
WING_TOP = 8
# The blended hump down its middle (MB-AEGIS-WING-02): `[y, half width, top]` stations from its
# nose to its tail.
HUMP = [  # type: list[list[float]]
    [-42, 3, 9],
    [-36, 8, 12.5],
    [-26, 12, 15],
    [-12, 14, 16],
    [4, 14, 15],
    [16, 11, 12.5],
    [24, 5, 9.5],
]
# The buried engines' intakes on top of the hump (their mouths' centre, `[x, y]`) and exhausts
# (slots in the trailing edge's notches, `[x, y]`).
INTAKE_AT = [11, -4]
EXHAUST_AT = [10, 17]
# The tile field (MB-AEGIS-WING-10): rows of skin panels along the chord on each outer wing,
# `ROW_COUNT` rows `ROW_PITCH` px apart round `ROW_MID` (X), each `ROW_HALF` px wide either side
# of its axis, `TILE` px long, `TILE_GAP` px apart; the panels stand `TILE_THICK` px proud of the
# wing's top. The rows run from the leading edge to the trailing edge, `MARGIN` px in.
ROW_MID = 35
ROW_PITCH = 7
ROW_COUNT = 5
ROW_HALF = 3.2
TILE = 6.4
TILE_GAP = 0.6
TILE_THICK = 0.9
MARGIN = 2
# The orb's well where the waves meet: across the three middle rows, `[y0, y1]` along them.
WELL = [-7.5, 6]

RED = bullet("red", 230)
ORANGE = bullet("orange", 200)
BLUE = bullet("blue", 175)


def leading_y(x: float) -> float:
    """Return the Y of the leading edge at `x` (0 <= x <= the tip)."""
    a = WING[1]
    b = WING[2]
    if x <= a[0]:
        return WING[0][1] + (a[1] - WING[0][1]) * x / a[0]
    return a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0])


def trailing_y(x: float) -> float:
    """Return the Y of the sawtooth trailing edge at `x` (0 <= x <= the tip)."""
    n = len(WING)
    for k in range(4, n - 1):
        a = WING[k]
        b = WING[k + 1]
        if b[0] <= x <= a[0]:
            return a[1] + (b[1] - a[1]) * (a[0] - x) / (a[0] - b[0])
    return WING[n - 1][1]


def row_x(k: int) -> float:
    """Return the X of the axis of row `k` (0 to `ROW_COUNT` - 1, from the root out)."""
    return ROW_MID + (k - (ROW_COUNT - 1) / 2) * ROW_PITCH


def row_span(k: int) -> list[float]:
    """Return `[y0, y1]` of row `k`: from its leading edge to its trailing edge, `MARGIN` in."""
    x0 = row_x(k) - ROW_HALF
    x1 = row_x(k) + ROW_HALF
    y0 = leading_y(x1) + MARGIN
    y1 = min(trailing_y(x0), trailing_y(x1))
    for q in WING:
        if x0 < q[0] < x1 and q[1] > 0:
            y1 = min(y1, q[1])
    return [y0, y1 - MARGIN]


def in_well(k: int) -> bool:
    """Whether row `k` runs through the orb's well (the three middle ones)."""
    return abs(k - (ROW_COUNT - 1) / 2) <= 1


def tile_field() -> list[list[float]]:
    """Return the outline of the tile field (the right one): a staircase round its rows."""
    top: list[list[float]] = []
    bottom: list[list[float]] = []
    for k in range(ROW_COUNT):
        span = row_span(k)
        x0 = row_x(k) - ROW_HALF - 0.3
        x1 = row_x(k) + ROW_HALF + 0.3
        top.append([x0, span[0]])
        top.append([x1, span[0]])
        bottom.append([x0, span[1]])
        bottom.append([x1, span[1]])
    outline = list(top)
    outline.extend([bottom[len(bottom) - 1 - k] for k in range(len(bottom))])
    return outline


# Its guns (BOSS-58, MB-AEGIS-WING-03): a twin-barrelled turret behind each intake (its single
# aimed shots, the barrels in turn), a long-barrelled turret on the nose (its quick bursts), and
# the core's: a twin-barrelled turret on the hump behind the cockpit and a rotor at its tail (its
# last rings), under a hatch until then.
INTAKE_GUN_AT = [11, 3]
INTAKE_GUN_H = 14.6
INTAKE_GUN = {"size": 3.6, "barrels": 2, "gap": 2.6, "bore": 0.9, "length": 7}
NOSE_GUN_AT = [0, -37]
NOSE_GUN_H = 12.4
NOSE_GUN = {"size": 3.4, "barrels": 1, "bore": 1.1, "length": 10}
DORSAL_AT = [0, -17]
DORSAL_H = 16
DORSAL_GUN = {"size": 4.2, "barrels": 2, "gap": 3, "bore": 1, "length": 7}
ROTOR_AT = [0, 14]
ROTOR_H = 13.4
ROTOR = {"size": 4.2, "barrels": 12, "layout": "ring", "bore": 0.75, "length": 3.4}

_AEGIS_WING = record({
    "id": "aegis-wing",
    # Its points and its parts' drops (MB-AEGIS-WING-12).
    "stats": stats({
        "id": "aegis-wing",
        "name": "Aegis Wing",
        "size": 3.5,
        "coreRadius": 15,
        "coreHealth": 1250,
        "points": 4200,
        "groundSpeed": 1,
        "parts": [
            part("intake-left", [-INTAKE_GUN_AT[0], INTAKE_GUN_AT[1] - 3], 8, 660),
            part("intake-right", [INTAKE_GUN_AT[0], INTAKE_GUN_AT[1] - 3], 8, 660),
            part("nose-gun", NOSE_GUN_AT, 8, 760),
        ],
    }),
    # Where it stops and how it moves in place (MB-AEGIS-WING-06): a wide wing gliding slowly.
    "stopFraction": 0.73,
    "sway": {"amplitude": 48, "period": 9},
    "bob": {"amplitude": 4, "period": 4.5},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-AEGIS-WING-03).
    "mounts": [
        gun_mount(
            "intake-left",
            "intake-left",
            [-INTAKE_GUN_AT[0], INTAKE_GUN_AT[1]],
            INTAKE_GUN_H,
            INTAKE_GUN,
        ),
        gun_mount("intake-right", "intake-right", INTAKE_GUN_AT, INTAKE_GUN_H, INTAKE_GUN),
        gun_mount("nose-gun", "nose-gun", NOSE_GUN_AT, NOSE_GUN_H, NOSE_GUN),
        gun_mount("dorsal", "core", DORSAL_AT, DORSAL_H, DORSAL_GUN),
        gun_mount("tail-rotor", "core", ROTOR_AT, ROTOR_H, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-AEGIS-WING-08): sparse, precise
    # shots (single fast aimed shots, short bursts, aimed pairs and spreads); at the end the tail
    # rotor's spiral of rings.
    "stages": stages(
        [
            volley.aimed("intake-left", 2.8, 1, 0, RED, 1.0),
            volley.aimed("intake-right", 2.8, 1, 0, RED, 2.4),
            volley.burst("nose-gun", 3.0, 3, 0.1, ORANGE, 1.6),
        ],
        [
            [volley.aimed("core", 3.4, 1, 0, BLUE, 2.0)],
            [volley.aimed("core", 2.8, 2, 4, BLUE, 1.2)],
            [volley.aimed("core", 2.6, 3, 7, BLUE, 1.0)],
            [
                volley.ring("core", 1.3, 12, 8, BLUE, 0.4),
                volley.aimed("core", 2.6, 1, 0, RED, 1.1),
            ],
        ],
    ),
})

# Where the orbs stand (MB-AEGIS-WING-10): in the well where the waves of flipping panels meet,
# on the wing's top.
ORB_AT = [ROW_MID, (WELL[0] + WELL[1]) / 2]
ORB_POD = [WING_TOP, WING_TOP + 3]


def _hatch() -> list[list[float]]:
    return [
        [
            ROTOR_AT[0] + 5.4 * math.cos(k * math.pi / 4 + math.pi / 8),
            ROTOR_AT[1] + 5.4 * math.sin(k * math.pi / 4 + math.pi / 8),
        ]
        for k in range(8)
    ]


# Its transformation (MB-AEGIS-WING-10): once both intake guns are gone, the skin panels of its
# outer wings (an armour region that leaves no pieces: its view rig flips them over) turn up their
# weapon faces and an orb rises out of each wing's well. The hatch over its tail rotor bursts as
# the rotor comes into use, in its last stage (BOSS-58).
AEGIS_WING = with_weapons(
    merge(_AEGIS_WING, {"transformParts": [["intake-left", "intake-right"]]}),
    [
        hidden_weapon("orb-left", "orb", [-ORB_AT[0], ORB_AT[1]], 7, 610, 1, "blue", 1.0, ORB_POD),
        hidden_weapon("orb-right", "orb", ORB_AT, 7, 610, 1, "blue", 1.8, ORB_POD),
    ],
    [
        armour_region(
            "skin", 1, tile_field(), "wing", [WING_TOP - 0.2, WING_TOP + TILE_THICK + 0.2]
        ),
        armour_region("rotor-hatch", None, _hatch(), "ring", None, False, "tail-rotor"),
    ],
)
