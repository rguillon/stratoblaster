# Copyright (c) 2026 Renaud Guillon
"""The Lab's L-15 final boss, the Throne of Storms (specs/bosses/lab/L-15-throne-of-storms.md).

The climax sky castle: a round castle on a floating disc of rock, a curtain wall with four corner
towers, a central throne keep under a lightning spire, a storm generator on a rock spur at each
side, a barbican on the rock's prow and a rocket loft at its back. Lab boss: in the dev viewer
only (no level brings it in). At its first transformation its four towers slide outward on their
rails (the castle expands, BOSS-45), a cannon riding out on each rear tower; at its second its
curtain wall and ward plating burst off (BOSS-42) and the whole castle turns 45 degrees (BOSS-46),
bringing a corner to bear, baring a pair of lances and a gatling.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount, laser_mount, missile_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, slide
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# FB-THRONE-OF-STORMS-01: the rock disc's radius and its top (the castle's ground), the curtain
# wall's inner and outer radius and its top, the ward's plating top between the keep and the wall.
ROCK_R = 60
ROCK_TOP = 4
WALL_IN = 41
WALL_OUT = 48
WALL_TOP = 16
WARD_TOP = 7
# The keep in the middle: its radius and its roof's height; the spire behind the throne.
KEEP_R = 18
KEEP_TOP = 24
SPIRE_AT = [0, 14]
SPIRE_TOP = 72
# The corner towers: their centres' distance out along each axis (on the wall), their radius, their
# top, and how far each slides out along each axis at the first transformation (on its rails).
TOWER_AT = 32
TOWER_R = 10
TOWER_TOP = 27
SLIDE_OUT = 16
# The storm generators on the rock's side spurs, the barbican on its prow and the rocket loft at
# its back (FB-THRONE-OF-STORMS-03).
GENERATOR_AT = [70, 2]
GENERATOR_TOP = 30
BARBICAN_AT = [0, -57]
BARBICAN_TOP = 14
LOFT_AT = [0, 57]
LOFT_TOP = 12

RED = bullet("red", 195)
ORANGE = bullet("orange", 180)
MAGENTA = bullet("magenta", 175)
PURPLE = bullet("purple", 185)


def fpart(part_id: str, at: list[Any], radius: float, health: float) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    return part(part_id, at, radius, health, {"drop": 0.6})


TOWER_LEFT = [-TOWER_AT, -TOWER_AT]
TOWER_RIGHT = [TOWER_AT, -TOWER_AT]

# The guns: twin barrels on the front towers' turrets, a laser turret on each generator's coil, the
# barbican's fixed wall gun (five barrels straight down), the loft's block of four rocket ports, and
# the keep's: a five-barrelled fan turret on the throne's dais and a rotor at the spire's foot,
# under a hatch until its last stage.
TOWER_GUN = {"size": 4.8, "barrels": 2, "gap": 1.4, "bore": 1.2, "length": 7.5}
GENERATOR_LASER = {"size": 5, "bore": 2.2, "length": 10, "turret": True}
WALL_GUN = {"size": 6, "barrels": 5, "gap": 4.4, "bore": 1.1, "length": 6, "turret": False}
THRONE_GUN_AT = [0, -10]
THRONE_GUN = {"size": 6, "barrels": 5, "gap": 1, "bore": 1, "length": 8}
ROTOR_AT = [0, 2]
ROTOR = {"size": 5.5, "barrels": 16, "layout": "ring", "bore": 0.7, "length": 3.4}

_THRONE_OF_STORMS = record({
    "id": "throne-of-storms",
    # Its points, its core's drop and its parts' drops (FB-THRONE-OF-STORMS-13).
    "stats": stats({
        "id": "throne-of-storms",
        "name": "Throne of Storms",
        "size": 5.5,
        "coreRadius": 22,
        "coreHealth": 5000,
        "points": 16000,
        "groundSpeed": 0,
        "coreDrop": 1,
        "parts": [
            fpart("tower-left", TOWER_LEFT, 11, 1400),
            fpart("tower-right", TOWER_RIGHT, 11, 1400),
            fpart("generator-left", [-GENERATOR_AT[0], GENERATOR_AT[1]], 12, 1800),
            fpart("generator-right", GENERATOR_AT, 12, 1800),
            fpart("barbican", BARBICAN_AT, 12, 1600),
            fpart("loft", LOFT_AT, 11, 1500),
        ],
    }),
    # Where it stops and how it moves in place (FB-THRONE-OF-STORMS-06): a mountain in the sky.
    "stopFraction": 0.74,
    "sway": {"amplitude": 24, "period": 12},
    "bob": {"amplitude": 5, "period": 6},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-THRONE-OF-STORMS-03).
    "mounts": [
        gun_mount("tower-left", "tower-left", TOWER_LEFT, TOWER_TOP, TOWER_GUN),
        gun_mount("tower-right", "tower-right", TOWER_RIGHT, TOWER_TOP, TOWER_GUN),
        laser_mount(
            "generator-left",
            "generator-left",
            [-GENERATOR_AT[0], GENERATOR_AT[1]],
            GENERATOR_TOP,
            GENERATOR_LASER,
        ),
        laser_mount(
            "generator-right", "generator-right", GENERATOR_AT, GENERATOR_TOP, GENERATOR_LASER
        ),
        gun_mount("barbican", "barbican", [0, -61], BARBICAN_TOP, WALL_GUN),
        missile_mount("loft", "loft", [0, 59], LOFT_TOP, 4),
        gun_mount("throne-gun", "core", THRONE_GUN_AT, KEEP_TOP, THRONE_GUN),
        gun_mount("spire-rotor", "core", ROTOR_AT, KEEP_TOP, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-THRONE-OF-STORMS-08). Closed, a
    # siege: the towers' aimed bursts, the barbican's straight walls of five, the generators'
    # lightning lasers and the loft's rockets, the throne's single shots. Expanded, a storm of
    # fans 12 degrees apart (BOSS-58) and bursts; turned, wide fans and aimed spreads, ending in
    # the spire rotor's spiral.
    "stages": stages(
        [
            volley.burst("tower-left", 2.6, 3, 0.14, RED, 0.8),
            volley.burst("tower-right", 2.6, 3, 0.14, RED, 2.1),
            volley.fan("barbican", 2.4, 5, 0, ORANGE, 1.6),
            volley.laser("generator-left", 7, 1.4, 2.5),
            volley.laser("generator-right", 7, 1.4, 6),
            volley.missiles("loft", 6, 2, 24, 3.5),
        ],
        [
            [volley.aimed("core", 2.6, 1, 0, MAGENTA, 1.4)],
            [volley.aimed("core", 2.4, 3, 10, MAGENTA, 1)],
            [volley.fan("core", 2.4, 7, 12, PURPLE, 0.8)],
            [
                volley.fan("core", 2.2, 5, 12, PURPLE, 0.6),
                volley.burst("core", 2.6, 4, 0.12, MAGENTA, 1.4),
            ],
            [
                volley.fan("core", 2.4, 9, 12, PURPLE, 0.6),
                volley.aimed("core", 2.8, 3, 12, MAGENTA, 1.5),
            ],
            [
                volley.fan("core", 2.4, 11, 10, PURPLE, 0.6),
                volley.burst("core", 2.4, 4, 0.12, RED, 1.4),
            ],
            [
                volley.ring("core", 1.2, 16, 8, MAGENTA, 0.4),
                volley.fan("core", 2.4, 7, 12, PURPLE, 1.2),
            ],
        ],
    ),
})

# Where the cannons ride (on the rear towers' roofs, slid out: FB-THRONE-OF-STORMS-10), and where
# the lances and the gatling stand on the ward under its plating (FB-THRONE-OF-STORMS-11).
CANNON_AT = [TOWER_AT + SLIDE_OUT, TOWER_AT + SLIDE_OUT]
LANCE_AT = [31, -6]
GATLING_AT = [0, -31]
WARD_POD = [ROCK_TOP + 1, ROCK_TOP + 5]


def _sector(start_deg: float, end_deg: float) -> list[list[float]]:
    """Return the ward and wall between two bearings (degrees from +X, counter-clockwise).

    From just out of the keep to the wall's outer face, an arc point every 15 degrees.
    """
    steps = max(2, math.ceil((end_deg - start_deg) / 15))
    outer: list[list[float]] = []
    inner: list[list[float]] = []
    for k in range(steps + 1):
        a = (start_deg + (end_deg - start_deg) * k / steps) * math.pi / 180
        outer.append([WALL_OUT * math.cos(a), WALL_OUT * math.sin(a)])
        inner.append([(KEEP_R + 1) * math.cos(a), (KEEP_R + 1) * math.sin(a)])
    outer.extend([inner[len(inner) - 1 - k] for k in range(len(inner))])
    return [[math.floor(q[0] * 10 + 0.5) / 10, math.floor(q[1] * 10 + 0.5) / 10] for q in outer]


# A tower's square plot (the right front one), what slides out with it.
_PLOT = TOWER_R + 2
TOWER_PLOT = [
    [TOWER_AT - _PLOT, -TOWER_AT - _PLOT],
    [TOWER_AT + _PLOT, -TOWER_AT - _PLOT],
    [TOWER_AT + _PLOT, -TOWER_AT + _PLOT],
    [TOWER_AT - _PLOT, -TOWER_AT + _PLOT],
]
# The ward's sectors (FB-THRONE-OF-STORMS-11): the front, the back, and the right side (mirrored).
SECTOR_FRONT = _sector(-135, -45)
SECTOR_BACK = _sector(45, 135)
SECTOR_SIDE = _sector(-45, 45)
SECTOR_HEIGHTS = [ROCK_TOP + 0.5, 1000]

# Its transformations: once both front towers are gone its four towers slide out on their rails,
# a cannon riding out on each rear tower; once both generators are gone its curtain wall and ward
# plating burst off for a pair of lances and a gatling on the centre line, and it turns 45 degrees,
# bringing its front right tower round to its nose. The hatch over the spire rotor bursts as the
# rotor comes into use, in its last stage (BOSS-58).
THRONE_OF_STORMS = with_weapons(
    merge(
        _THRONE_OF_STORMS,
        {
            "transformParts": [
                ["tower-left", "tower-right"],
                ["generator-left", "generator-right"],
            ],
            "turns": [0, math.pi / 4],
        },
    ),
    [
        hidden_weapon(
            "cannon-left",
            "cannon",
            [-CANNON_AT[0], CANNON_AT[1]],
            10,
            1440,
            1,
            "red",
            1.2,
            [TOWER_TOP, TOWER_TOP + 4],
        ),
        hidden_weapon(
            "cannon-right", "cannon", CANNON_AT, 10, 1440, 1, "red", 2.0, [TOWER_TOP, TOWER_TOP + 4]
        ),
        hidden_weapon(
            "lance-left", "lance", [-LANCE_AT[0], LANCE_AT[1]], 8, 1800, 2, "magenta", 1.2, WARD_POD
        ),
        hidden_weapon("lance-right", "lance", LANCE_AT, 8, 1800, 2, "magenta", 2.6, WARD_POD),
        hidden_weapon("gatling", "gatling", GATLING_AT, 8, 1800, 2, "purple", 1.6, WARD_POD),
    ],
    concat(
        concat(
            moving_region(
                "towers-front",
                1,
                TOWER_PLOT,
                slide([[0, 0, 0], [SLIDE_OUT, -SLIDE_OUT, 0]]),
                None,
                [ROCK_TOP, 1000],
            ),
            moving_region(
                "towers-back",
                1,
                [[q[0], -q[1]] for q in TOWER_PLOT],
                slide([[0, 0, 0], [SLIDE_OUT, SLIDE_OUT, 0]]),
                None,
                [ROCK_TOP, 1000],
            ),
        ),
        [
            armour_region("ward-front", 2, SECTOR_FRONT, "shell", SECTOR_HEIGHTS, False),
            armour_region("ward-back", 2, SECTOR_BACK, "shell", SECTOR_HEIGHTS, False),
            armour_region("ward-side", 2, SECTOR_SIDE, "shell", SECTOR_HEIGHTS),
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
                "spire-rotor",
            ),
        ],
    ),
)
