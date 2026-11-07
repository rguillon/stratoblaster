# Copyright (c) 2026 Renaud Guillon
"""The Windmill Ram, the Lab's L-14 mini boss (specs/bosses/lab/L-14-windmill-ram.md).

Lab boss: in the dev viewer only, no level brings it in. A wedge-shaped flying siege engine: an
armoured battering-ram prow at the front (two halves meeting on its centre line), a timber-and-iron
hull with a siege belfry amidships, and a huge four-sailed windmill rotor at its stern that drives
it. Once both cheek guns on its prow are gone the prow splits open: its two halves swing apart
sideways like doors (it changes shape, BOSS-45), baring the iron-headed ram inside, and a lance
rides in on each half's inner face.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import move_point, moving_region, swing
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


RED = bullet("red", 185)
ORANGE = bullet("orange", 175)

# MB-WINDMILL-RAM-01: the hull, a wedge from the prow's back edge to its stern: its half width at
# the front and at the back, and its deck's height.
HULL_FRONT = -24
HULL_BACK = 60
HULL_HALF = [21, 33]
DECK = 10

# MB-WINDMILL-RAM-05: the right half of its ram prow as drawn, shut (its left half is its mirror
# image); the two halves meet on the centre line. Each swings open about its hinge (`[x, y,
# height]`, the half's back outer corner) by `OPEN` degrees about the vertical, like a door.
PROW = [[0, -68], [5, -66], [21, -30], [21, HULL_FRONT], [0, HULL_FRONT]]
PROW_HINGE = [21.0, float(HULL_FRONT), 2.0]
OPEN = 55
PROW_SWING = swing(PROW_HINGE, "up", [0, OPEN])
# The heights the prow is drawn between: its keel, and its armoured top (over the deck).
PROW_Y = [2, 13]

# The cheek guns stand on the shut prow (MB-WINDMILL-RAM-03); the lances' pods on its halves' inner
# faces, where they end up once the prow has swung open.
CHEEK = [9, -42]
CHEEK_HEIGHT = PROW_Y[1] + 1
LANCE_SPOT = [9, -33]


def _tenth(value: float) -> float:
    """`value` rounded to a tenth."""
    return math.floor(value * 10 + 0.5) / 10


def opened(spot: list[Any]) -> list[float]:
    """Where `spot` of the right prow half as drawn lies once the prow has swung open."""
    q = move_point(PROW_SWING, OPEN, [spot[0], spot[1], 0])
    return [_tenth(q[0]), _tenth(q[1])]


LANCE_AT = opened(LANCE_SPOT)

# The belfry amidships (MB-WINDMILL-RAM-03): its centre, its top, and its gun's height.
BELFRY_AT = [0, 6]
BELFRY_TOP = 24
# The windmill (MB-WINDMILL-RAM-04): its tower's centre and top, the hub of its sails in front of
# its cap (`[x, y, height]`), the sails' reach, and how far their disc leans forward from flat
# (degrees: it faces the player's way, up the screen).
TOWER_AT = [0, 52]
TOWER_TOP = 40
HUB = [0.0, 47.0, 48.0]
SAIL_REACH = 38
SAIL_TILT = 25

# The guns: twin barrels on each cheek, three on the belfry's turret, the core's ram gun on the fore
# deck (its aimed shots and bursts) and its rotor under a hatch amidships (its last ring).
CHEEK_GUN = {"size": 4.5, "barrels": 2, "gap": 2.8, "bore": 1.1, "length": 7}
BELFRY_GUN = {"size": 5, "barrels": 3, "gap": 1.2, "bore": 1.1, "length": 7}
RAM_GUN = {"size": 5, "barrels": 2, "gap": 2.8, "bore": 1.2, "length": 8}
ROTOR = {"size": 4.5, "barrels": 12, "layout": "ring", "bore": 0.8, "length": 3.2}
RAM_GUN_AT = [0, -16]
ROTOR_AT = [0, 24]

_WINDMILL_RAM = record({
    "id": "windmill-ram",
    # Its points and its parts' drops (MB-WINDMILL-RAM-11).
    "stats": stats({
        "id": "windmill-ram",
        "name": "Windmill Ram",
        "size": 4.4,
        "coreRadius": 16,
        "coreHealth": 1300,
        "points": 4400,
        "groundSpeed": 0.5,
        "parts": [
            part("cheek-left", [-CHEEK[0], CHEEK[1]], 9, 700),
            part("cheek-right", CHEEK, 9, 700),
            part("belfry", BELFRY_AT, 12, 820),
        ],
    }),
    # Where it stops and how it moves in place (MB-WINDMILL-RAM-06): wide sways and a lunging bob,
    # as if it charged.
    "stopFraction": 0.73,
    "sway": {"amplitude": 62, "period": 7.5},
    "bob": {"amplitude": 13, "period": 2.4},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-WINDMILL-RAM-03).
    "mounts": [
        gun_mount("cheek-left", "cheek-left", [-CHEEK[0], CHEEK[1]], CHEEK_HEIGHT, CHEEK_GUN),
        gun_mount("cheek-right", "cheek-right", CHEEK, CHEEK_HEIGHT, CHEEK_GUN),
        gun_mount("belfry", "belfry", BELFRY_AT, BELFRY_TOP + 1, BELFRY_GUN),
        gun_mount("ram-gun", "core", RAM_GUN_AT, DECK + 1, RAM_GUN),
        gun_mount("deck-rotor", "core", ROTOR_AT, DECK + 1.5, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-WINDMILL-RAM-08): while shut, the
    # cheeks' aimed bursts as it lunges, the belfry's fans swept down; the core's aimed shots, then
    # spreads, then bursts, then the rotor's ring.
    "stages": stages(
        [
            volley.burst("cheek-left", 2.4, 3, 0.15, RED, 1.0),
            volley.burst("cheek-right", 2.4, 3, 0.15, RED, 2.2),
            volley.fan("belfry", 3.0, 5, 12, ORANGE, 1.6),
        ],
        [
            [volley.aimed("core", 2.8, 1, 0, RED, 1.4)],
            [volley.aimed("core", 2.4, 3, 10, RED, 0.8)],
            [volley.burst("core", 2.0, 4, 0.14, ORANGE, 0.6)],
            [
                volley.ring("core", 1.6, 12, 8, ORANGE, 0.4),
                volley.aimed("core", 2.4, 1, 0, RED, 1),
            ],
        ],
    ),
})

# Its transformation (BOSS-45, MB-WINDMILL-RAM-10): once both cheek guns are gone its prow splits
# open, its halves swinging apart like doors, and a lance rides in on each half's inner face. The
# hatch over its deck rotor bursts as the rotor comes into use, in its last stage (BOSS-58).
WINDMILL_RAM = with_weapons(
    merge(_WINDMILL_RAM, {"transformParts": [["cheek-left", "cheek-right"]]}),
    [
        hidden_weapon(
            "lance-left",
            "lance",
            [-LANCE_AT[0], LANCE_AT[1]],
            7,
            660,
            1,
            "red",
            1.2,
            [PROW_Y[1], PROW_Y[1] + 3],
        ),
        hidden_weapon(
            "lance-right",
            "lance",
            LANCE_AT,
            7,
            660,
            1,
            "red",
            2.0,
            [PROW_Y[1], PROW_Y[1] + 3],
        ),
    ],
    concat(
        moving_region("prow", 1, PROW, PROW_SWING, None, [PROW_Y[0], 1000]),
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
                "deck-rotor",
            ),
        ],
    ),
)
