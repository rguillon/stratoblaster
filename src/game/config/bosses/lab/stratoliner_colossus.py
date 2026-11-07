# Copyright (c) 2026 Renaud Guillon
"""The Lab's L-16 final boss, the Stratoliner Colossus.

Specs: specs/bosses/lab/L-16-stratoliner-colossus.md.

Lab boss: in the dev viewer only, no level brings it in. A colossal six-engine swept-wing jet
bomber-airliner seen from above, about 5 L across: a long fuselage with a radome nose, swept wings
with three podded engines each, flaps along their trailing edges, a swept tailplane, a fin and a
tail gun. It fights as an airliner at first (aimed pairs from its wing guns, its outer engines'
gun fans, its tail gun's bursts). Its first transformation morphs its two outer engine nacelles
into gatlings: the fan discs split and fly off, the cowlings peel back in petals and the cores
telescope out into barrel clusters (the nacelles retire, BOSS-46). Its second unfolds its flaps
into a second wing tier, biplane-style, carrying a pair of missile racks, and splits its nose cone
into two halves that become the rails of a lance on the centre line.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# FB-STRATOLINER-COLOSSUS-01: the fuselage, a loft along Y at stations from its nose (-Y) to its
# tail, `[y, half width, floor, top]`; the nose cone (its radome, FB-STRATOLINER-COLOSSUS-11) is
# the part ahead of `NOSE_JOINT`.
FUSELAGE = [  # type: list[list[float]]
    [-88, 0, 8, 8],
    [-84, 4, 5, 11],
    [-76, 7.5, 3, 14],
    [-66, 9.5, 2, 16],
    [40, 9.5, 2, 16],
    [58, 6.5, 4, 15],
    [70, 4, 6, 13],
    [77, 0, 9, 9],
]
NOSE_JOINT = -66


def fuselage_at(y: float) -> list[float]:
    """Return the fuselage's `[half width, floor, top]` at `y` (zeros off its ends)."""
    for k in range(len(FUSELAGE) - 1):
        a = FUSELAGE[k]
        b = FUSELAGE[k + 1]
        if a[0] <= y <= b[0]:
            u = (y - a[0]) / (b[0] - a[0])
            return [a[i] + (b[i] - a[i]) * u for i in [1, 2, 3]]
    return [0, 0, 0]


# The swept wing (FB-STRATOLINER-COLOSSUS-02): from its root (`ROOT_X`, in the fuselage) to its tip
# (`TIP_X`), its leading and trailing edges' Y at the root and at the tip; its underside and top.
ROOT_X = 9
TIP_X = 86
ROOT_EDGES = [-24, 14]
TIP_EDGES = [30, 42]
WING_LOW = 8
WING_TOP = 10.5


def leading_edge(x: float) -> float:
    """Return the wing's leading edge's Y at `x` (out from the centre line)."""
    return ROOT_EDGES[0] + (TIP_EDGES[0] - ROOT_EDGES[0]) * (x - ROOT_X) / (TIP_X - ROOT_X)


def trailing_edge(x: float) -> float:
    """Return the wing's trailing edge's Y at `x`."""
    return ROOT_EDGES[1] + (TIP_EDGES[1] - ROOT_EDGES[1]) * (x - ROOT_X) / (TIP_X - ROOT_X)


# Its six engines, podded on pylons ahead of and under the wing: their X (inner, middle, outer), how
# far their centre is ahead of the leading edge, their half length, radius and axis height.
ENGINE_X = [26, 46, 66]
ENGINE_AHEAD = 7
ENGINE_HALF = 11
ENGINE_R = 4.6
ENGINE_H = 4.6


def engine_y(x: float) -> float:
    """Return the Y of the centre of the engine at `x`."""
    return leading_edge(x) - ENGINE_AHEAD


OUTER_Y = math.floor(engine_y(ENGINE_X[2]) + 0.5)
# The outer cowlings' petals (FB-STRATOLINER-COLOSSUS-10): they cover the nacelle from its front
# to `PETAL_HINGE` behind its centre, where they are hinged.
PETAL_HINGE = 5
# The tail (FB-STRATOLINER-COLOSSUS-02): the tailplane's root and tip chords and its tip's X; the
# fin along the centre line, its root chord, its top chord and height.
TAIL_ROOT = [48, 62]
TAIL_TIP = [62, 69]
TAIL_SPAN = 34
TAIL_H = 12
FIN_ROOT = [40, 64]
FIN_TIP = [56, 64]
FIN_TOP = 36
# The flaps along the inner trailing edges (FB-STRATOLINER-COLOSSUS-11): their span `[x0, x1]` and
# chord; the second wing tier they unfold into, its height, and how far its outer panel reaches
# past their tips.
FLAP_X = [12, 44]
FLAP_CHORD = 11
TIER_H = 24
TIER_REACH = 22

RED = bullet("red", 195)
ORANGE = bullet("orange", 180)
PURPLE = bullet("purple", 185)
MAGENTA = bullet("magenta", 175)


def fpart(part_id: str, at: list[Any], radius: float, health: float, options: Any = None) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    extra = options if options != None else {}
    return part(part_id, at, radius, health, merge({"drop": 0.6}, extra))


# Its guns (BOSS-58, FB-STRATOLINER-COLOSSUS-03): twin barrels on each wing gun's barbette, three
# barrels straight down on each outer nacelle's fixed gun, twin barrels on the tail gun's turret;
# the core's: a five-barrelled fan turret on the spine ahead of the wing, and a rotor on the spine
# behind it (its last spirals), under a hatch until then.
WING_GUN_AT = [36, 8]
WING_GUN_H = WING_TOP + 0.6
WING_GUN = {"size": 4.6, "barrels": 2, "gap": 2.8, "bore": 1.1, "length": 7.5}
NACELLE_GUN_AT = [ENGINE_X[2], OUTER_Y - 4]
NACELLE_GUN_H = ENGINE_H + ENGINE_R + 0.6
NACELLE_GUN = {"size": 4.2, "barrels": 3, "gap": 2.2, "bore": 0.9, "length": 6, "turret": False}
TAIL_GUN_AT = [0, 70]
TAIL_GUN_H = 13.5
TAIL_GUN = {"size": 4.4, "barrels": 2, "gap": 2.4, "bore": 1, "length": 7}
SPINE_GUN_AT = [0, -42]
SPINE_H = 16.5
SPINE_GUN = {"size": 6, "barrels": 5, "gap": 1, "bore": 1, "length": 8}
ROTOR_AT = [0, 26]
ROTOR = {"size": 5, "barrels": 14, "layout": "ring", "bore": 0.75, "length": 3.6}

_STRATOLINER_COLOSSUS = record({
    "id": "stratoliner-colossus",
    # Its points, its core's drop and its parts' drops (FB-STRATOLINER-COLOSSUS-13).
    "stats": stats({
        "id": "stratoliner-colossus",
        "name": "Stratoliner Colossus",
        "size": 5,
        "coreRadius": 20,
        "coreHealth": 2100,
        "points": 8500,
        "groundSpeed": 1.2,
        "coreDrop": 1,
        "parts": [
            fpart("wing-gun-left", [-WING_GUN_AT[0], WING_GUN_AT[1]], 10, 1000),
            fpart("wing-gun-right", WING_GUN_AT, 10, 1000),
            # BOSS-46: they leave the fight as they morph into the gatlings.
            fpart("nacelle-left", [-ENGINE_X[2], OUTER_Y], 10, 600, {"retire": 1}),
            fpart("nacelle-right", [ENGINE_X[2], OUTER_Y], 10, 600, {"retire": 1}),
            fpart("tail-gun", TAIL_GUN_AT, 10, 900),
        ],
    }),
    # Where it stops and how it moves in place (FB-STRATOLINER-COLOSSUS-06): a huge airliner, long
    # slow sways.
    "stopFraction": 0.7,
    "sway": {"amplitude": 34, "period": 10},
    "bob": {"amplitude": 6, "period": 5},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-STRATOLINER-COLOSSUS-03).
    "mounts": [
        gun_mount(
            "wing-gun-left",
            "wing-gun-left",
            [-WING_GUN_AT[0], WING_GUN_AT[1]],
            WING_GUN_H,
            WING_GUN,
        ),
        gun_mount("wing-gun-right", "wing-gun-right", WING_GUN_AT, WING_GUN_H, WING_GUN),
        gun_mount(
            "nacelle-left",
            "nacelle-left",
            [-NACELLE_GUN_AT[0], NACELLE_GUN_AT[1]],
            NACELLE_GUN_H,
            NACELLE_GUN,
        ),
        gun_mount("nacelle-right", "nacelle-right", NACELLE_GUN_AT, NACELLE_GUN_H, NACELLE_GUN),
        gun_mount("tail-gun", "tail-gun", TAIL_GUN_AT, TAIL_GUN_H, TAIL_GUN),
        gun_mount("spine-gun", "core", SPINE_GUN_AT, SPINE_H, SPINE_GUN),
        gun_mount("spine-rotor", "core", ROTOR_AT, SPINE_H, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-STRATOLINER-COLOSSUS-08). As an
    # airliner: the wing guns' aimed pairs, the outer nacelles' straight fans of three (two streams
    # far apart), the tail gun's bursts, the spine gun's single shots. Then fans 12 degrees apart
    # (BOSS-58) and spreads, ending in the spine rotor's spiral.
    "stages": stages(
        [
            volley.aimed("wing-gun-left", 2.2, 2, 6, RED, 0.8),
            volley.aimed("wing-gun-right", 2.2, 2, 6, RED, 1.9),
            volley.fan("nacelle-left", 2.0, 3, 0, ORANGE, 1.2),
            volley.fan("nacelle-right", 2.0, 3, 0, ORANGE, 2.2),
            volley.burst("tail-gun", 2.6, 3, 0.13, MAGENTA, 1.5),
        ],
        [
            [volley.aimed("core", 2.8, 1, 0, PURPLE, 1.4)],
            [volley.aimed("core", 2.6, 3, 9, PURPLE, 1)],
            [volley.fan("core", 2.6, 5, 12, ORANGE, 0.8)],
            [
                volley.fan("core", 2.4, 3, 12, ORANGE, 0.6),
                volley.aimed("core", 2.8, 2, 8, PURPLE, 1.5),
            ],
            [
                volley.fan("core", 2.4, 5, 12, PURPLE, 0.6),
                volley.burst("core", 2.8, 3, 0.12, RED, 1.4),
            ],
            [
                volley.ring("core", 1.3, 14, 8, MAGENTA, 0.4),
                volley.fan("core", 2.6, 5, 12, ORANGE, 1.2),
            ],
        ],
    ),
})

# Where the hidden weapons stand: a gatling where each outer nacelle was (FB-STRATOLINER-COLOSSUS-
# 10), a rack on each half of the second wing tier, over the flaps, and the lance between the
# nose cone's halves (FB-STRATOLINER-COLOSSUS-11). The racks slide out along the tier from its
# root.
GATLING_AT = [ENGINE_X[2], OUTER_Y - 1]
GATLING_POD = [4, 9]
RACK_AT = [30, math.floor(trailing_edge(30) - FLAP_CHORD / 2 + 0.5)]
RACK_FROM = [FLAP_X[0] + 2, math.floor(trailing_edge(FLAP_X[0] + 2) - FLAP_CHORD / 2 + 0.5)]
TIER_POD = [TIER_H, TIER_H + 3]
LANCE_AT = [0, -74]
LANCE_POD = [3, 8.5]


def _flap() -> list[list[float]]:
    """Return the right flap's outline (along the trailing edge)."""
    x0 = FLAP_X[0]
    x1 = FLAP_X[1]
    return [
        [x0, trailing_edge(x0) - FLAP_CHORD],
        [x1, trailing_edge(x1) - FLAP_CHORD],
        [x1, trailing_edge(x1)],
        [x0, trailing_edge(x0)],
    ]


def _fan() -> list[list[float]]:
    """Return the outline round the right outer nacelle's front half (its fan and intake)."""
    x = ENGINE_X[2]
    r = ENGINE_R + 1.2
    y0 = OUTER_Y - ENGINE_HALF - 1
    y1 = OUTER_Y + PETAL_HINGE
    return [[x - r, y0], [x + r, y0], [x + r, y1], [x - r, y1]]


def _nose() -> list[list[float]]:
    """Return the nose cone's outline, from its tip back to the joint (not mirrored)."""
    right = [[s[1] + 0.6, s[0] - (1 if s[1] == 0 else 0)] for s in FUSELAGE if s[0] <= NOSE_JOINT]
    result = list(right)
    result.extend([[-q[0], q[1]] for q in reversed(right)])
    return result


FLAP = _flap()
FAN = _fan()
NOSE = _nose()

# Its transformations: once both wing guns are gone its outer nacelles morph into gatlings (their
# fans split and fly off, their cowlings peel back, their cores telescope out: the nacelles
# retire); once its tail gun is gone its flaps unfold into a second wing tier carrying a pair of
# racks, and its nose cone splits into the rails of a lance. The hatch over the spine rotor bursts
# as the rotor comes into use, in its last stage (BOSS-58).
STRATOLINER_COLOSSUS = with_weapons(
    merge(
        _STRATOLINER_COLOSSUS,
        {"transformParts": [["wing-gun-left", "wing-gun-right"], ["tail-gun"]]},
    ),
    [
        hidden_weapon(
            "gatling-left",
            "gatling",
            [-GATLING_AT[0], GATLING_AT[1]],
            8,
            800,
            1,
            "red",
            1.0,
            GATLING_POD,
            [0, 0, 0],
        ),
        hidden_weapon(
            "gatling-right", "gatling", GATLING_AT, 8, 800, 1, "red", 1.8, GATLING_POD, [0, 0, 0]
        ),
        hidden_weapon(
            "rack-left",
            "rack",
            [-RACK_AT[0], RACK_AT[1]],
            5.5,
            1000,
            2,
            "magenta",
            1.4,
            TIER_POD,
            None,
            [-RACK_FROM[0], RACK_FROM[1]],
        ),
        hidden_weapon(
            "rack-right", "rack", RACK_AT, 5.5, 1000, 2, "magenta", 3.4, TIER_POD, None, RACK_FROM
        ),
        hidden_weapon("lance", "lance", LANCE_AT, 7, 1000, 2, "magenta", 2.2, LANCE_POD, [0, 0, 0]),
    ],
    [
        armour_region("fans", 1, FAN, "ring", [ENGINE_H - ENGINE_R - 1, ENGINE_H + ENGINE_R + 1]),
        armour_region("flaps", 2, FLAP, "wing", [WING_LOW - 0.5, WING_TOP + 1]),
        armour_region("nose", 2, NOSE, "shell", None, False),
        armour_region(
            "rotor-hatch",
            None,
            [
                [
                    ROTOR_AT[0] + 6.2 * math.cos(k * math.pi / 4 + math.pi / 8),
                    ROTOR_AT[1] + 6.2 * math.sin(k * math.pi / 4 + math.pi / 8),
                ]
                for k in range(8)
            ],
            "ring",
            None,
            False,
            "spine-rotor",
        ),
    ],
)
