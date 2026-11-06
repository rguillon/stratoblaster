# Copyright (c) 2026 Renaud Guillon
"""The Mantis Lancer, the Lab's L-4 mini boss (specs/bosses/lab/L-4-mantis-lancer.md).

A Lab boss, in the dev viewer only: no level brings it in. Offsets in px from the boss's centre,
X right and Y up (its nose points down, at -Y). 3 destroyable parts (BOSS-13): a laser turret on
each raised scythe and the gun in its head. The two scythe lasers aim at the player through their
warning lines a little out of step, so their locked beams cross and fence the player in while the
head adds aimed bursts (MB-MANTIS-LANCER-08).
"""

import math

from game.config.bosses.boss_guns import gun_mount, laser_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import record

GREEN = bullet("green", 185)
ORANGE = bullet("orange", 175)

# A scythe's laser emitter, on a turret that follows the player through its warning line, then
# holds still while its beam fires (BOSS-30, BOSS-31; MB-MANTIS-LANCER-03).
SCYTHE_LASER = {"size": 4, "bore": 1.7, "length": 10, "turret": True}

# The head's gun: two barrels side by side in its mouth, taking turns through its bursts.
HEAD_GUN = {"size": 4.2, "barrels": 2, "gap": 2.9, "bore": 1.1, "length": 7}

# Where the rotor in its abdomen lies, under its hatch (BOSS-58).
ROTOR_AT = [0, 30]

# L-4 mini: a tall, narrow praying mantis, its triangular head at the front, its two scythes raised
# forward either side of it (MB-MANTIS-LANCER-07).
_MANTIS_LANCER = record({
    "id": "mantis-lancer",
    # Its points and its parts' drops (MB-MANTIS-LANCER-11).
    "stats": stats({
        "id": "mantis-lancer",
        "name": "Mantis Lancer",
        "size": 3.5,
        "coreRadius": 17,
        "coreHealth": 1450,
        "points": 4500,
        "groundSpeed": 0.6,
        "parts": [
            part("scythe-left", [-25, -46], 12, 740),
            part("scythe-right", [25, -46], 12, 740),
            part("head", [0, -52], 10, 700),
        ],
    }),
    # Where it stops and how it moves in place (MB-MANTIS-LANCER-06).
    "stopFraction": 0.72,
    "sway": {"amplitude": 55, "period": 7},
    "bob": {"amplitude": 9, "period": 3.3},
    "guns": {},
    # It transforms once both scythes are gone (MB-MANTIS-LANCER-10).
    "transformParts": [["scythe-left", "scythe-right"]],
    # Its gun mounts (BOSS-58, MB-MANTIS-LANCER-03): a laser turret on each scythe's blade, the twin
    # gun in the head's mouth, and the core's: a fan turret on its long neck (its aimed shots, fans
    # and bursts) and a rotor in its abdomen under a hatch (its last ring).
    "mounts": [
        laser_mount("scythe-left", "scythe-left", [-25, -48], 11, SCYTHE_LASER),
        laser_mount("scythe-right", "scythe-right", [25, -48], 11, SCYTHE_LASER),
        gun_mount("head", "head", [0, -56], 7, HEAD_GUN),
        gun_mount(
            "neck",
            "core",
            [0, -33],
            9,
            {"size": 4.4, "barrels": 3, "gap": 1, "bore": 0.9, "length": 6},
        ),
        gun_mount(
            "abdomen-rotor",
            "core",
            ROTOR_AT,
            9.6,
            {"size": 4.5, "barrels": 12, "layout": "ring", "bore": 0.8, "length": 3.2},
        ),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-MANTIS-LANCER-08). The scythes'
    # beams lock 0.6 s apart, so they cross; its fans are 12° apart, the neck turret's spacing.
    "stages": stages(
        [
            volley.laser("scythe-left", 5.5, 1.6, 2),
            volley.laser("scythe-right", 5.5, 1.6, 2.6),
            volley.burst("head", 2.4, 3, 0.16, GREEN, 1.3),
        ],
        [
            [volley.aimed("core", 3, 1, 0, ORANGE, 1.5)],
            [volley.aimed("core", 2.6, 3, 12, ORANGE, 0.8)],
            [volley.burst("core", 2.4, 4, 0.14, ORANGE, 0.6)],
            [
                volley.ring("core", 1.5, 12, 9, GREEN, 0.4),
                volley.aimed("core", 2.6, 1, 0, ORANGE, 1.1),
            ],
        ],
    ),
})

# The thorax plating's right half (MB-MANTIS-LANCER-05): from the neck's root to the wings' root,
# the orbs under it; mirrored across the centre line.
THORAX_PLATING = [
    [0, -27],
    [7, -27],
    [13, -20],
    [15.5, -10],
    [15, 0],
    [11, 7],
    [0, 9],
]

# Its transformation (D-224, MB-MANTIS-LANCER-10): once both scythes are gone its thorax plating
# bursts off, baring a dark metal frame, and a pair of orbs unfold on it.
MANTIS_LANCER = with_weapons(
    _MANTIS_LANCER,
    [
        hidden_weapon("orb-left", "orb", [-8, -9], 8, 590, 1, "green", 1.2, 7),
        hidden_weapon("orb-right", "orb", [8, -9], 8, 590, 1, "green", 2.0, 7),
    ],
    [
        armour_region("thorax", 1, THORAX_PLATING, "shell"),
        # The hatch over its abdomen rotor (BOSS-58): it bursts as the rotor comes into use, in its
        # last stage, and the rotor rises out of it.
        armour_region(
            "rotor-hatch",
            None,
            [
                [6 * math.cos(k * math.pi / 4), ROTOR_AT[1] + 6 * math.sin(k * math.pi / 4)]
                for k in range(8)
            ],
            "ring",
            None,
            False,
            "abdomen-rotor",
        ),
    ],
)
