# Copyright (c) 2026 Renaud Guillon
"""The Leviathan Spine, the Lab's L-3 final boss (specs/bosses/lab/L-3-leviathan-spine.md).

Lab boss: in the dev viewer only, no level brings it in. A very long, narrow sea-serpent lying
along the screen (5.5 L long, its head down the screen), its segmented back armoured: a pair of
pectoral fins fire laser beams crossing under it, and three dorsal gun nodes and a tail fluke along
its spine fire walls of bullets, a tracking laser and homing missiles. It sheds the plating of its
back twice: a gatling pair first, then a cannon pair and a lance horn on its crown.

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


BLUE = bullet("blue", 190)
ORANGE = bullet("orange", 175)
RED = bullet("red", 185)


def fpart(part_id: str, at: list[Any], radius: float, health: float) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    return part(part_id, at, radius, health, {"drop": 0.6})


# FB-LEVIATHAN-SPINE-02: its body along Y, from its snout (at -Y) to its tail's tip; its back
# plating (the armour it sheds) over three lengths: its flanks behind the fins, its back behind
# its middle node, and the crown of its skull.
SNOUT = -96
TAIL = 96
FLANKS_Y = [-16, 2]
BACK_Y = [20, 38]
CROWN_Y = [-88, -70]

# The fins' laser emitters (FB-LEVIATHAN-SPINE-03): fixed, each beam slanting across under the body
# to the other side.
FIN_LASER = {"size": 3.6, "bore": 1.8, "length": 9}
FIN_SLANT = 24
# The front node's twin guns, firing its lines of aimed bursts.
FRONT_GUN = {"size": 5, "barrels": 2, "gap": 2.8, "bore": 1.1, "length": 8}
# The rear node's fan turret, sweeping its walls of bullets straight down.
REAR_GUN = {"size": 5.5, "barrels": 5, "gap": 1, "bore": 0.9, "length": 7}
# Where the core's tail rotor rises, under a hatch until its last stage.
ROTOR_AT = [0, 64]

_LEVIATHAN_SPINE = record({
    "id": "leviathan-spine",
    # Its points, its core's drop and its parts' drops (FB-LEVIATHAN-SPINE-13).
    "stats": stats({
        "id": "leviathan-spine",
        "name": "Leviathan Spine",
        "size": 5.5,
        "coreRadius": 18,
        "coreHealth": 3000,
        "points": 10000,
        "groundSpeed": 1.2,
        "coreDrop": 1,
        "parts": [
            fpart("fin-left", [-28, -24], 12, 950),
            fpart("fin-right", [28, -24], 12, 950),
            fpart("node-front", [0, -42], 11, 1100),
            fpart("node-rear", [0, 47], 11, 1100),
            fpart("node-mid", [0, 11], 11, 1200),
            fpart("tail-fluke", [0, 81], 13, 1200),
        ],
    }),
    # Where it stops and how it moves in place (FB-LEVIATHAN-SPINE-06): a long, slow weave.
    "stopFraction": 0.7,
    "sway": {"amplitude": 70, "period": 7},
    "bob": {"amplitude": 8, "period": 3.5},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-LEVIATHAN-SPINE-03): a laser at each fin's tip, the front node's
    # twin guns, the middle node's laser turret, the rear node's fan turret, the fluke's missile
    # ports, and the core's: the crest turret at the back of its skull and the tail rotor.
    "mounts": [
        laser_mount(
            "fin-left", "fin-left", [-31, -28], 6, merge(FIN_LASER, {"restDeg": -FIN_SLANT})
        ),
        laser_mount(
            "fin-right", "fin-right", [31, -28], 6, merge(FIN_LASER, {"restDeg": FIN_SLANT})
        ),
        gun_mount("node-front", "node-front", [0, -42], 17, FRONT_GUN),
        gun_mount("node-rear", "node-rear", [0, 47], 15.5, REAR_GUN),
        laser_mount(
            "node-mid",
            "node-mid",
            [0, 11],
            17.5,
            {"size": 5, "bore": 2.1, "length": 10, "turret": True},
        ),
        missile_mount("tail-fluke", "tail-fluke", [0, 81], 7, 4),
        gun_mount(
            "crest",
            "core",
            [0, -63],
            11,
            {"size": 5, "barrels": 5, "gap": 1, "bore": 0.9, "length": 7},
        ),
        gun_mount(
            "tail-rotor",
            "core",
            ROTOR_AT,
            10.6,
            {"size": 4.4, "barrels": 14, "layout": "ring", "bore": 0.7, "length": 3},
        ),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-LEVIATHAN-SPINE-08); its fans 12
    # degrees apart, the crest turret's barrels' spacing (BOSS-58).
    "stages": stages(
        [
            volley.laser("fin-left", 6, 1.5, 2),
            volley.laser("fin-right", 6, 1.5, 5),
            volley.burst("node-front", 2.6, 5, 0.1, BLUE, 1),
            volley.fan("node-rear", 2.6, 7, 9, ORANGE, 1.6),
            volley.laser("node-mid", 6.5, 1.6, 3.5),
            volley.missiles("tail-fluke", 6, 2, 30, 4),
        ],
        [
            [volley.aimed("core", 3, 1, 0, RED, 1.5)],
            [volley.aimed("core", 2.6, 3, 10, RED, 0.8)],
            [volley.burst("core", 2.4, 4, 0.14, RED, 0.6)],
            [volley.fan("core", 2.4, 5, 12, RED, 0.6)],
            [volley.fan("core", 2.2, 7, 12, RED, 0.6)],
            [
                volley.burst("core", 2.2, 6, 0.1, RED, 0.6),
                volley.aimed("core", 2.8, 3, 10, BLUE, 1.4),
            ],
            [
                volley.ring("core", 1.4, 14, 9, RED, 0.4),
                volley.fan("core", 2.6, 5, 12, BLUE, 1.2),
            ],
        ],
    ),
})


def _band(y: list[Any], half: list[Any]) -> list[list[float]]:
    """Return the outline of a length of its back from `y[0]` to `y[1]`, `half[k]` half-wide."""
    return [[-half[0], y[0]], [half[0], y[0]], [half[1], y[1]], [-half[1], y[1]]]


# Its transformations (FB-LEVIATHAN-SPINE-10, FB-LEVIATHAN-SPINE-11): once both fins are gone the
# plating of its flanks bursts off and a gatling pair unfolds; once its front and rear nodes are
# gone the plating of its back bursts off for a cannon pair, and its crown for a lance horn on its
# centre line. The tail hatch over its rotor bursts as the rotor comes into use (BOSS-58).
LEVIATHAN_SPINE = with_weapons(
    merge(
        _LEVIATHAN_SPINE,
        {"transformParts": [["fin-left", "fin-right"], ["node-front", "node-rear"]]},
    ),
    [
        hidden_weapon("gatling-left", "gatling", [-8, -7], 7, 960, 1, "blue", 1.2, 11.5),
        hidden_weapon("gatling-right", "gatling", [8, -7], 7, 960, 1, "blue", 2.0, 11.5),
        hidden_weapon("cannon-left", "cannon", [-8, 29], 7.5, 1200, 2, "orange", 1.4, 11),
        hidden_weapon("cannon-right", "cannon", [8, 29], 7.5, 1200, 2, "orange", 2.6, 11),
        hidden_weapon("lance", "lance", [0, -78], 8, 1200, 2, "red", 2.0, 9.6),
    ],
    [
        armour_region("flanks", 1, _band(FLANKS_Y, [14.4, 14.6]), "shell", None, False),
        armour_region("back", 2, _band(BACK_Y, [13.6, 12.6]), "shell", None, False),
        armour_region(
            "crown",
            2,
            [[-10, CROWN_Y[0]], [10, CROWN_Y[0]], [12, CROWN_Y[1]], [-12, CROWN_Y[1]]],
            "shell",
            None,
            False,
        ),
        armour_region(
            "rotor-hatch",
            None,
            [
                [
                    ROTOR_AT[0] + 6 * math.cos(k * math.pi / 4),
                    ROTOR_AT[1] + 6 * math.sin(k * math.pi / 4),
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
