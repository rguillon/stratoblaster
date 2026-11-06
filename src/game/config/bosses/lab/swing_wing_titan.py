# Copyright (c) 2026 Renaud Guillon
"""The Swing-Wing Titan, the Lab's L-18 final boss (specs/bosses/lab/L-18-swing-wing-titan.md).

Lab boss: in the dev viewer only, no level brings it in. A gigantic variable-geometry bomber seen
from above: a long blended fuselage, big wing gloves either side of it, its wings spread wide at
rest, four engines in two pods under its rear, a tall fin with its tailplanes set across it half
way up (a cruciform tail). Spread, it crosses the screen with fans from its wing guns. Once both
wing guns are gone its wings sweep fully back and its gloves unfold into weapons decks: their
doors open fore and aft, racks of feed tubes rise, and a battery rises from each (FB-SWING-WING-
TITAN-10). Once both rear barbettes are gone its tail section splits: its dorsal fairing opens on
two missile racks, its fin splits into two skins that fold out flat, its tailplanes swing round
under them, and the four blades spin up as a rotor round an orb rising on the centre line
(FB-SWING-WING-TITAN-11).

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount, laser_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, swing
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# FB-SWING-WING-TITAN-01: the fuselage along Y, `[y, half width, belly, top]` stations from its
# nose to its tail.
FUSELAGE = [  # type: list[list[float]]
    [-106, 0.6, 13, 14],
    [-98, 5, 10, 18],
    [-86, 9, 8, 22],
    [-66, 11, 7, 25],
    [-30, 12, 6, 26],
    [20, 12.5, 6, 26],
    [50, 11, 7, 25],
    [66, 8, 9, 23],
    [82, 4.5, 12, 20],
    [90, 0.6, 15, 16],
]


def fuselage_at(y: float, k: int) -> float:
    """Return the fuselage's value `k` (1 half width, 2 belly, 3 top) at `y` (0 off its ends)."""
    for i in range(len(FUSELAGE) - 1):
        a = FUSELAGE[i]
        b = FUSELAGE[i + 1]
        if a[0] <= y <= b[0]:
            return a[k] + (b[k] - a[k]) * (y - a[0]) / (b[0] - a[0])
    return 0


# FB-SWING-WING-TITAN-02: a wing glove (the right one; mirrored): its outline and heights. The bay
# in it (FB-SWING-WING-TITAN-10), its doors' hinges `[fore, aft]` and its floor.
GLOVE = [[10, -78], [17, -62], [34, -18], [36, 10], [11, 12]]  # type: list[list[float]]
GLOVE_Y = [13.5, 20.6, 21.6]
BAY = [[11, -44], [22.8, -44], [32.2, -16], [11, -16]]  # type: list[list[float]]
BAY_DOORS = [-44, -30, -16]
BAY_FLOOR = 19
# The swing wing (the right one as drawn, spread; mirrored): its outline, its heights, its pivot in
# the glove and its sweep (degrees about the vertical).
WING = [[22, -9], [31, -12], [97, 2], [99, 7], [97, 12], [31, 16], [22, 14]]  # type: list[list[float]]
WING_Y = [12.4, 14.4, 15.4]
PIVOT = [28.0, 2.0, 14.0]
SWEEP = 58
# The engine pods under its rear (FB-SWING-WING-TITAN-02): each pod's two engines' X, their axis
# height and radius, and `[front, back]`.
ENGINE_X = [15, 25]
ENGINE_H = 6
ENGINE_R = 4.4
ENGINES = [20, 54]
# The cruciform tail (FB-SWING-WING-TITAN-11): the fin's root chord on the tail cone, its top and
# chord there, the hub (where the tailplanes cross the fin) and the tailplanes' span and chords.
FIN = [60, 88]
FIN_TOP = 62
FIN_TIP = [72, 90]
HUB = [0.0, 74.0, 34.0]
TAILPLANE_SPAN = 32
TAILPLANE_ROOT = [66, 82]
TAILPLANE_TIP = [72, 80]
# The dorsal fairing ahead of the fin that opens on the racks: `[y0, y1]`, its half width.
FAIRING = [46, 62]
FAIRING_HALF = 13

ROSE = bullet("magenta", 175)
RED = bullet("red", 190)
ORANGE = bullet("orange", 180)
GOLD = bullet("orange", 165)


def fpart(part_id: str, at: list[Any], radius: float, health: float) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    return part(part_id, at, radius, health, {"drop": 0.6})


# Its guns (BOSS-58, FB-SWING-WING-TITAN-03): a twin-barrelled turret on each wing's barbette, a
# twin-barrelled turret on each engine pod's tail barbette, the nose radome's laser turret, and the
# core's on its spine: a three-barrelled turret and a rotor, under a hatch until its last stage.
WING_GUN_AT = [68, 4]
WING_GUN_H = 18
WING_GUN = {"size": 4.6, "barrels": 2, "gap": 3, "bore": 1.1, "length": 8}
BARBETTE_AT = [20, 46]
BARBETTE_H = 14.5
BARBETTE_GUN = {"size": 4.2, "barrels": 2, "gap": 2.8, "bore": 1, "length": 7}
NOSE_AT = [0, -80]
NOSE_H = 24.6
NOSE_LASER = {"size": 4.4, "bore": 1.8, "length": 9, "turret": True}
SPINE_AT = [0, -40]
SPINE_H = 26
SPINE_GUN = {"size": 5.4, "barrels": 3, "gap": 1.2, "bore": 1.2, "length": 8}
ROTOR_AT = [0, 24]
ROTOR_H = 26
ROTOR = {"size": 5, "barrels": 14, "layout": "ring", "bore": 0.75, "length": 3.6}

_SWING_WING_TITAN = record({
    "id": "swing-wing-titan",
    # Its points, its core's drop and its parts' drops (FB-SWING-WING-TITAN-13).
    "stats": stats({
        "id": "swing-wing-titan",
        "name": "Swing-Wing Titan",
        "size": 5.8,
        "coreRadius": 18,
        "coreHealth": 3000,
        "points": 11000,
        "groundSpeed": 0.6,
        "coreDrop": 1,
        "parts": [
            fpart("wing-left", [-WING_GUN_AT[0], WING_GUN_AT[1]], 11, 1100),
            fpart("wing-right", WING_GUN_AT, 11, 1100),
            fpart("barbette-left", [-BARBETTE_AT[0], BARBETTE_AT[1]], 9, 1050),
            fpart("barbette-right", BARBETTE_AT, 9, 1050),
            fpart("nose", NOSE_AT, 10, 1400),
        ],
    }),
    # Where it stops and how it moves in place (FB-SWING-WING-TITAN-06): a huge, heavy bomber,
    # slow wide sways.
    "stopFraction": 0.68,
    "sway": {"amplitude": 30, "period": 11},
    "bob": {"amplitude": 5, "period": 5.5},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-SWING-WING-TITAN-03).
    "mounts": [
        gun_mount(
            "wing-left", "wing-left", [-WING_GUN_AT[0], WING_GUN_AT[1]], WING_GUN_H, WING_GUN
        ),
        gun_mount("wing-right", "wing-right", WING_GUN_AT, WING_GUN_H, WING_GUN),
        gun_mount(
            "barbette-left",
            "barbette-left",
            [-BARBETTE_AT[0], BARBETTE_AT[1]],
            BARBETTE_H,
            BARBETTE_GUN,
        ),
        gun_mount("barbette-right", "barbette-right", BARBETTE_AT, BARBETTE_H, BARBETTE_GUN),
        laser_mount("nose", "nose", NOSE_AT, NOSE_H, NOSE_LASER),
        gun_mount("spine-gun", "core", SPINE_AT, SPINE_H, SPINE_GUN),
        gun_mount("spine-rotor", "core", ROTOR_AT, ROTOR_H, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-SWING-WING-TITAN-08): spread, the
    # wing guns sweep fans slanting in across the screen (a crossfire), the barbettes fire aimed
    # bursts and the nose laser tracks the player; the core's aimed shots, spreads and fans, ending
    # in the spine rotor's spiral.
    "stages": stages(
        [
            volley.fan("wing-left", 2.8, 5, 10, ORANGE, 1.0, -14),
            volley.fan("wing-right", 2.8, 5, 10, ORANGE, 2.4, 14),
            volley.burst("barbette-left", 2.6, 3, 0.14, RED, 1.6),
            volley.burst("barbette-right", 2.6, 3, 0.14, RED, 2.9),
            volley.laser("nose", 7.5, 1.4, 3.5),
        ],
        [
            [volley.aimed("core", 2.8, 1, 0, ROSE, 1.4)],
            [volley.aimed("core", 2.6, 3, 8, ROSE, 1)],
            [volley.fan("core", 2.6, 5, 12, GOLD, 0.8)],
            [
                volley.burst("core", 2.4, 4, 0.13, RED, 0.6),
                volley.fan("core", 3, 3, 12, GOLD, 1.6),
            ],
            [
                volley.fan("core", 2.4, 7, 12, GOLD, 0.6),
                volley.aimed("core", 2.8, 1, 0, RED, 1.5),
            ],
            [
                volley.ring("core", 1.4, 14, 9, ROSE, 0.4),
                volley.fan("core", 2.8, 5, 12, GOLD, 1.2),
            ],
        ],
    ),
})


# Where the hidden weapons stand: the batteries in the gloves' bays (FB-SWING-WING-TITAN-10); the
# orb on the rotor's hub over the split fin, the racks under the dorsal fairing
# (FB-SWING-WING-TITAN-11).
BATTERY_AT = [19, -28]
BATTERY_POD = [BAY_FLOOR, BAY_FLOOR + 2.4]
ORB_AT = [HUB[0], HUB[1]]
ORB_POD = [HUB[2], HUB[2] + 2.4]
RACK_AT = [8, 54]
RACK_POD = [25, 27]
WING_SWING = swing(PIVOT, "up", [0, SWEEP])


def _fairing() -> list[list[float]]:
    """Return the right half of the tail's split section: the dorsal fairing and the fin's root."""
    return [
        [0, FAIRING[0]],
        [FAIRING_HALF, FAIRING[0]],
        [FAIRING_HALF, FAIRING[1]],
        [4, FIN[0]],
        [2, FIN[1]],
        [0, FIN[1]],
    ]


# Its transformations: once both wing guns are gone its wings sweep back and its gloves' bays open
# on a pair of batteries; once both barbettes are gone its tail splits into a rotor round an orb,
# its dorsal fairing opening on a pair of racks. The hatch over the spine rotor bursts as the rotor
# comes into use, in its last stage (BOSS-58).
SWING_WING_TITAN = with_weapons(
    merge(
        _SWING_WING_TITAN,
        {
            "transformParts": [
                ["wing-left", "wing-right"],
                ["barbette-left", "barbette-right"],
            ]
        },
    ),
    [
        hidden_weapon(
            "battery-left",
            "battery",
            [-BATTERY_AT[0], BATTERY_AT[1]],
            8,
            1120,
            1,
            "orange",
            1.2,
            BATTERY_POD,
            [0, 0, 0],
        ),
        hidden_weapon(
            "battery-right",
            "battery",
            BATTERY_AT,
            8,
            1120,
            1,
            "orange",
            2.0,
            BATTERY_POD,
            [0, 0, 0],
        ),
        hidden_weapon("orb", "orb", ORB_AT, 9, 1400, 2, "magenta", 1.0, ORB_POD, [0, 0, 0]),
        hidden_weapon(
            "rack-left",
            "rack",
            [-RACK_AT[0], RACK_AT[1]],
            7,
            1400,
            2,
            "red",
            1.4,
            RACK_POD,
            [0, 0, 0],
        ),
        hidden_weapon("rack-right", "rack", RACK_AT, 7, 1400, 2, "red", 2.4, RACK_POD, [0, 0, 0]),
    ],
    concat(
        moving_region("wing", 1, WING, WING_SWING, None, [WING_Y[0] - 0.5, 1000]),
        [
            armour_region("glove-bay", 1, BAY, "wing", [BAY_FLOOR - 0.5, GLOVE_Y[2] + 1]),
            armour_region("tail-split", 2, _fairing(), "shell", [18, 1000]),
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
                "spine-rotor",
            ),
        ],
    ),
)
