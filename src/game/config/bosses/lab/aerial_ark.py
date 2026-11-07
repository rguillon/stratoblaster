# Copyright (c) 2026 Renaud Guillon
"""The Lab's L-20 final boss, the Aerial Ark (specs/bosses/lab/L-20-aerial-ark.md).

Lab boss: in the dev viewer only (no level brings it in). The climax: a gigantic six-engine
flying-wing mothership seen from above, about 5.3 L across, a long command fuselage down its
middle under a raised bridge, a swept wing with a sawtooth trailing edge, six podded engines along
it. Its wing is built in three segments: the centre section round the fuselage and an outer segment
each side, plated in four tiles. At its first transformation the wing splits at its joints: the
outer segments spread apart like a squadron breaking formation, held by telescoping struts and
cables (its view rig), and an orb rises at each split joint. At its second the outer segments break
into their tiles, which swing round and re-join into a ring round the centre section: the airplane
becomes a halo, and a pair of gatlings and a lance in its nose come out. Its outer engines leave
with their segments (they retire, BOSS-46); the rest of it stays put, so its hit circles and
muzzles never move.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount, laser_mount, missile_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# FB-AERIAL-ARK-01: the fuselage's nose and tail, its back's top, and the raised bridge on it
# (`[y0, y1]`, its half width and its top).
NOSE = -74
TAIL = 56
FUSE_TOP = 15
BRIDGE = [-30, -10]  # type: list[float]
BRIDGE_HALF = 7
BRIDGE_TOP = 20
# The centre section of the wing (the right half; mirrored), from its leading root to the joint,
# back along its sawtooth trailing edge to its trailing root, and its heights (bottom, waist, top).
CENTRE_WING = [
    [11, -38],
    [44, -20],
    [44, 8],
    [30, 24],
    [24, 20],
    [11, 40],
]  # type: list[list[float]]
WING_Y = [3, 6.6, 8]  # type: list[float]
# The joint's X, and the outer segment beyond it (FB-AERIAL-ARK-05): its leading edge at the joint
# and its slope, its chord (its trailing edge parallel), its tip's X, its heights; plated in
# `TILES` tiles across its span.
JOINT_X = 44
LEAD_Y = -20
LEAD_SLOPE = 0.565
CHORD = 28
TIP_X = 90
TILE_Y = [3.5, 6.2, 7.5]  # type: list[float]
TILES = 4
# The engines (FB-AERIAL-ARK-02): podded nacelles on the wing, their X and their span along Y,
# their radius and their axis' height; their tops carry the guns.
NACELLE_R = 4.6
NACELLE_AXIS = 12
NACELLE_TOP = 16.6
INNER_ENGINE = [20, 4, 32]  # type: list[float]
MID_ENGINE = [32, -3, 20]  # type: list[float]
OUTER_ENGINE = [72.75, 0, 26]  # type: list[float]
# The strut at each joint (FB-AERIAL-ARK-05): its fixed sleeve out from the centre section along
# `STRUT_Y`, from `STRUT_X[0]` to `STRUT_X[1]`, its half width and its top (the orb stands on it).
STRUT_Y = -2
STRUT_X = [38, 50]  # type: list[float]
STRUT_HALF = 4.5
STRUT_TOP = 9
# The halo (FB-AERIAL-ARK-11): its centre's Y and its radius, where the tiles come round to.
HALO_Y = -2
HALO_R = 50

GOLD = bullet("orange", 185)
RED = bullet("red", 200)
MAGENTA = bullet("magenta", 180)
PURPLE = bullet("purple", 190)


def lead(x: float) -> float:
    """Return the Y of the outer segment's leading edge at `x` (at rest)."""
    return LEAD_Y + (x - JOINT_X) * LEAD_SLOPE


def fpart(part_id: str, at: list[Any], radius: float, health: float, more: Any = None) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    options: Any = {"drop": 0.6}
    if more != None:
        options = merge(options, more)
    return part(part_id, at, radius, health, options)


def _mirror(at: list[Any]) -> list[Any]:
    return [-at[0], at[1]]


# The engines' guns (BOSS-58, FB-AERIAL-ARK-03): a twin-barrelled turret on each outer engine,
# a laser turret on each inner engine and a block of four missile ports on each middle engine, on
# their nacelles' backs; the core's: a three-barrelled turret on the bridge and the tail rotor,
# under a hatch until its last stage.
OUTER_AT = [OUTER_ENGINE[0], 10]
OUTER_GUN_AT = [OUTER_ENGINE[0], 6]
OUTER_GUN = {"size": 4.4, "barrels": 2, "gap": 1.4, "bore": 1.1, "length": 7.5}
INNER_AT = [INNER_ENGINE[0], 14]
INNER_LASER_AT = [INNER_ENGINE[0], 10]
INNER_LASER = {"size": 4.4, "bore": 1.9, "length": 9, "turret": True}
MID_AT = [MID_ENGINE[0], 4]
MID_BLOCK_AT = [MID_ENGINE[0], 3]
BRIDGE_GUN_AT = [0, -20]
BRIDGE_GUN = {"size": 5.6, "barrels": 3, "gap": 1.2, "bore": 1.1, "length": 8.5}
ROTOR_AT = [0, 36]
ROTOR = {"size": 5.4, "barrels": 16, "layout": "ring", "bore": 0.7, "length": 3.4}

_AERIAL_ARK = record({
    "id": "aerial-ark",
    # Its points, its core's drop and its parts' drops (FB-AERIAL-ARK-13).
    "stats": stats({
        "id": "aerial-ark",
        "name": "Aerial Ark",
        "size": 5.5,
        "coreRadius": 22,
        "coreHealth": 5400,
        "points": 16500,
        "groundSpeed": 0.3,
        "coreDrop": 1,
        "parts": [
            # D-228: they leave with their outer segments as these break formation.
            fpart("engine-outer-left", _mirror(OUTER_AT), 10, 1500, {"retire": 1}),
            fpart("engine-outer-right", OUTER_AT, 10, 1500, {"retire": 1}),
            fpart("engine-inner-left", _mirror(INNER_AT), 10, 1700),
            fpart("engine-inner-right", INNER_AT, 10, 1700),
            fpart("engine-mid-left", _mirror(MID_AT), 9, 1600),
            fpart("engine-mid-right", MID_AT, 9, 1600),
        ],
    }),
    # Where it stops and how it moves in place (FB-AERIAL-ARK-06): the biggest of them, slow sways.
    "stopFraction": 0.72,
    "sway": {"amplitude": 22, "period": 12},
    "bob": {"amplitude": 5, "period": 6},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-AERIAL-ARK-03).
    "mounts": [
        gun_mount(
            "engine-outer-left",
            "engine-outer-left",
            _mirror(OUTER_GUN_AT),
            NACELLE_TOP,
            OUTER_GUN,
        ),
        gun_mount("engine-outer-right", "engine-outer-right", OUTER_GUN_AT, NACELLE_TOP, OUTER_GUN),
        laser_mount(
            "engine-inner-left",
            "engine-inner-left",
            _mirror(INNER_LASER_AT),
            NACELLE_TOP,
            INNER_LASER,
        ),
        laser_mount(
            "engine-inner-right", "engine-inner-right", INNER_LASER_AT, NACELLE_TOP, INNER_LASER
        ),
        missile_mount(
            "engine-mid-left", "engine-mid-left", _mirror(MID_BLOCK_AT), NACELLE_TOP + 3, 4
        ),
        missile_mount("engine-mid-right", "engine-mid-right", MID_BLOCK_AT, NACELLE_TOP + 3, 4),
        gun_mount("bridge-gun", "core", BRIDGE_GUN_AT, BRIDGE_TOP, BRIDGE_GUN),
        gun_mount("tail-rotor", "core", ROTOR_AT, FUSE_TOP, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-AERIAL-ARK-08). As a flying wing:
    # the outer turrets' fans crossing under it, the inner engines' tracking lasers, the middle
    # engines' homing pairs, the bridge's aimed shots. Split, the orbs' turning rings fill the
    # sky between ever wider fans from the bridge; as a halo, gatling streams and the lance's
    # straight beam with wide fans and spreads, ending in the tail rotor's spiral.
    "stages": stages(
        [
            volley.fan("engine-outer-left", 2.8, 5, 12, RED, 1, -14),
            volley.fan("engine-outer-right", 2.8, 5, 12, RED, 2.4, 14),
            volley.laser("engine-inner-left", 7, 1.4, 3),
            volley.laser("engine-inner-right", 7, 1.4, 6.5),
            volley.missiles("engine-mid-left", 6, 2, 24, 2),
            volley.missiles("engine-mid-right", 6, 2, 24, 5),
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
                volley.fan("core", 2.3, 11, 10, PURPLE, 0.6),
                volley.burst("core", 2.4, 4, 0.12, RED, 1.4),
            ],
            [
                volley.ring("core", 1.2, 16, 8, MAGENTA, 0.4),
                volley.fan("core", 2.4, 7, 12, PURPLE, 1.2),
            ],
        ],
    ),
})

# Where the hidden weapons stand: the orbs on the struts at the split joints (FB-AERIAL-ARK-10);
# the gatlings on the centre section's wing roots and the lance in the nose (FB-AERIAL-ARK-11).
ORB_AT = [JOINT_X, STRUT_Y]
ORB_POD = [STRUT_TOP, STRUT_TOP + 3.5]
GATLING_AT = [21, -16]
GATLING_POD = [WING_Y[2], WING_Y[2] + 3.5]
LANCE_AT = [0, -52]
LANCE_POD = [11, 15]
# The armour over them: the fairing over each joint (the right one; mirrored), the plating of the
# wing roots (the right one; mirrored) and of the nose (whole), with their heights.
JOINT_FAIRING = [[37, -11], [51, -11], [51, 7], [37, 7]]  # type: list[list[float]]
FAIRING_Y = [WING_Y[2] - 0.5, 13]
ROOT_PLATING = [[12, -28], [31, -22], [31, -6], [12, -6]]  # type: list[list[float]]
PLATING_Y = [WING_Y[2] - 0.5, WING_Y[2] + 3]
NOSE_PLATING = [
    [0, -66],
    [7, -62],
    [10, -50],
    [10, -40],
    [-10, -40],
    [-10, -50],
    [-7, -62],
]  # type: list[list[float]]
NOSE_Y = [10, 15.5]  # type: list[float]

# Its transformations: once both outer engines are gone its wing splits at its joints and the
# outer segments spread apart (its rig), an orb rising at each joint; once both inner engines are
# gone its outer segments' tiles come round into a halo (its rig), the plating of its wing roots
# and of its nose bursts off on a pair of gatlings and a lance. The hatch over the tail rotor
# bursts as the rotor comes into use, in its last stage (BOSS-58).
AERIAL_ARK = with_weapons(
    merge(
        _AERIAL_ARK,
        {
            "transformParts": [
                ["engine-outer-left", "engine-outer-right"],
                ["engine-inner-left", "engine-inner-right"],
            ]
        },
    ),
    [
        hidden_weapon("orb-left", "orb", _mirror(ORB_AT), 7, 1360, 1, "magenta", 1.2, ORB_POD),
        hidden_weapon("orb-right", "orb", ORB_AT, 7, 1360, 1, "magenta", 2.5, ORB_POD),
        hidden_weapon(
            "gatling-left", "gatling", _mirror(GATLING_AT), 7, 1700, 2, "red", 1.2, GATLING_POD
        ),
        hidden_weapon("gatling-right", "gatling", GATLING_AT, 7, 1700, 2, "red", 2.2, GATLING_POD),
        hidden_weapon("lance", "lance", LANCE_AT, 8, 1700, 2, "magenta", 1.6, LANCE_POD),
    ],
    [
        armour_region("joint", 1, JOINT_FAIRING, "shell", FAIRING_Y),
        armour_region("root-plating", 2, ROOT_PLATING, "wing", PLATING_Y),
        armour_region("nose-plating", 2, NOSE_PLATING, "shell", NOSE_Y, False),
        armour_region(
            "rotor-hatch",
            None,
            [
                [
                    ROTOR_AT[0] + 6.4 * math.cos(k * math.pi / 4 + math.pi / 8),
                    ROTOR_AT[1] + 6.4 * math.sin(k * math.pi / 4 + math.pi / 8),
                ]
                for k in range(8)
            ],
            "ring",
            None,
            False,
            "tail-rotor",
        ),
    ],
)
