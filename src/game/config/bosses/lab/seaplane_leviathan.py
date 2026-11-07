# Copyright (c) 2026 Renaud Guillon
"""The Seaplane Leviathan, the Lab's L-17 final boss (specs/bosses/lab/L-17-seaplane-leviathan.md).

Lab boss: in the dev viewer only, no level brings it in. A gigantic flying boat seen from above: a
deep boat hull down its middle, a high gull wing across it on a pylon, three radial engines on
each wing with their propellers, a float hanging on struts under each wingtip, and a tall tail. It
fights first as a gunship (aimed pairs from its wing guns, bursts from its nose turret, fans from
its tail turret, a tracking laser from its dorsal blister). At its first transformation its
wingtip floats morph into mortars: each float's struts pull it up under the wing, it swings up
over the leading edge onto the wingtip, keel up, and its hull splits open along the keel into the
mortar's cradle (flak artillery). At its second its bow splits open along the keel into a hangar,
the two bow doors swinging apart (it changes shape, BOSS-45) and a launch deck sliding out over
the bow, and the propeller hubs of its two inner engines morph into a sweeper pair: the propellers
stop and retract, each spinner pitches up onto its cowling and peels open, and a sweeping laser
rises out of it (a carrier: Hornets and sweeping beams).

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


# FB-SEAPLANE-LEVIATHAN-01: the boat hull's outline (its right half, bow to stern; mirrored), its
# keel, its bevel's waist (the chine) and its deck.
HULL = [  # type: list[list[float]]
    [0, -80],
    [5, -76],
    [10, -66],
    [13, -52],
    [13.5, -30],
    [13.5, 20],
    [11, 40],
    [7, 58],
    [3.5, 74],
    [0, 78],
]
HULL_LOW = 2
HULL_CHINE = 13
DECK = 21
# The bow (FB-SEAPLANE-LEVIATHAN-10): its upper hull from the stem back to `BOW_END` splits along
# the keel into two doors over the hangar's floor (the lower hull, up to `BAY_FLOOR`); each door
# swings `DOOR_OPEN` degrees out about its after outer corner.
BOW_END = -42
BAY_FLOOR = 8
DOOR_OPEN = 68
# The wing (FB-SEAPLANE-LEVIATHAN-02): the pylon over the hull (`[y0, y1]`, its top), the inner
# gull panels rising from it to the kink (X) and the outer panels' underside, waist and top out to
# the tips; the leading and trailing edges' Y at the root and at the tip.
PYLON = [-20, 16]
PYLON_TOP = 25
KINK = 26
WING_UNDER = 29.5
WING_WAIST = 32
WING_TOP = 33
TIP = 94
LEADING = [-16, -13]
TRAILING = [11, 6]
# The radial engines on the outer panels (FB-SEAPLANE-LEVIATHAN-02): their X, the nacelles' axis
# height, radius and `[y0, y1]` (the cowling's front to the tail), the propellers' hub Y and reach.
ENGINES = [36, 54, 72]
NACELLE_H = 31
NACELLE_RADIUS = 4.8
NACELLE = [-26, 6]
HUB_Y = -27.5
PROP_RADIUS = 8.4
# The wingtip floats (FB-SEAPLANE-LEVIATHAN-09): their X, `[y0, y1]`, half width, keel and deck at
# rest, hanging on two struts (their Ys) from the wing's underside.
FLOAT_X = 85
FLOAT = [-24, 6]
FLOAT_HALF = 4.2
FLOAT_KEEL = 15
FLOAT_DECK = 22
STRUTS = [-14, -2]
# The tall tail (FB-SEAPLANE-LEVIATHAN-02): the fin's `[y0, y1]` at its root and its top, its top's
# height; the tailplane's `[y0, y1]`, span and height.
FIN = [44, 70]
FIN_TOP_Y = [56, 68]
FIN_TOP = 60
TAILPLANE = [54, 66]
TAILPLANE_SPAN = 26
TAILPLANE_H = 42

RED = bullet("red", 190)
ORANGE = bullet("orange", 180)
GOLD = bullet("orange", 175)
BLUE = bullet("blue", 175)


def fpart(part_id: str, at: list[Any], radius: float, health: float, more: Any = None) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    options: Any = {"drop": 0.6}
    if more != None:
        options = merge(options, more)
    return part(part_id, at, radius, health, options)


# The guns (BOSS-58, FB-SEAPLANE-LEVIATHAN-03): twin barrels on each wing gun's turret (in its
# blister on the gull panel), three on the nose turret's and two on the tail turret's, the dorsal
# blister's laser turret, and the core's on the pylon and the after deck: a twin-barrelled turret
# and a rotor (its last spiral), under a hatch until then.
WING_GUN_AT = [20, -2]
WING_GUN_H = 32.6
WING_GUN = {"size": 4.4, "barrels": 2, "gap": 3, "bore": 1.1, "length": 7.5}
NOSE_AT = [0, -64]
NOSE_H = 22.6
NOSE_GUN = {"size": 4.8, "barrels": 3, "gap": 1.2, "bore": 1.1, "length": 8}
TAIL_AT = [0, 72]
TAIL_H = 22.4
TAIL_GUN = {"size": 4.2, "barrels": 2, "gap": 2.8, "bore": 1, "length": 7}
LASER_AT = [0, -32]
LASER_H = 24.4
LASER = {"size": 4.6, "bore": 1.8, "length": 9, "turret": True}
DORSAL_AT = [0, 0]
DORSAL_H = PYLON_TOP + 0.6
DORSAL_GUN = {"size": 5, "barrels": 2, "gap": 3.2, "bore": 1.2, "length": 8}
ROTOR_AT = [0, 30]
ROTOR_H = DECK + 0.6
ROTOR = {"size": 5, "barrels": 14, "layout": "ring", "bore": 0.75, "length": 3.6}

_SEAPLANE_LEVIATHAN = record({
    "id": "seaplane-leviathan",
    # Its points, its core's drop and its parts' drops (FB-SEAPLANE-LEVIATHAN-13).
    "stats": stats({
        "id": "seaplane-leviathan",
        "name": "Seaplane Leviathan",
        "size": 5.5,
        "coreRadius": 22,
        "coreHealth": 2200,
        "points": 9500,
        "groundSpeed": 0.8,
        "coreDrop": 1,
        "parts": [
            fpart("wing-gun-left", [-WING_GUN_AT[0], WING_GUN_AT[1]], 9, 700),
            fpart("wing-gun-right", WING_GUN_AT, 9, 700),
            fpart("nose-turret", NOSE_AT, 9, 780),
            fpart("tail-turret", TAIL_AT, 9, 740),
            fpart("dorsal-laser", LASER_AT, 9, 820),
        ],
    }),
    # Where it stops and how it moves in place (FB-SEAPLANE-LEVIATHAN-06): a huge, heavy flying
    # boat: slow, short sways.
    "stopFraction": 0.7,
    "sway": {"amplitude": 26, "period": 11},
    "bob": {"amplitude": 5, "period": 5.5},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-SEAPLANE-LEVIATHAN-03).
    "mounts": [
        gun_mount(
            "wing-gun-left",
            "wing-gun-left",
            [-WING_GUN_AT[0], WING_GUN_AT[1]],
            WING_GUN_H,
            WING_GUN,
        ),
        gun_mount("wing-gun-right", "wing-gun-right", WING_GUN_AT, WING_GUN_H, WING_GUN),
        gun_mount("nose-turret", "nose-turret", NOSE_AT, NOSE_H, NOSE_GUN),
        gun_mount("tail-turret", "tail-turret", TAIL_AT, TAIL_H, TAIL_GUN),
        laser_mount("dorsal-laser", "dorsal-laser", LASER_AT, LASER_H, LASER),
        gun_mount("dorsal", "core", DORSAL_AT, DORSAL_H, DORSAL_GUN),
        gun_mount("stern-rotor", "core", ROTOR_AT, ROTOR_H, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-SEAPLANE-LEVIATHAN-08): a
    # gunship's aimed pairs, bursts, fans and tracking laser; the core's aimed shots, spreads,
    # fans and bursts, ending in the stern rotor's spiral.
    "stages": stages(
        [
            volley.aimed("wing-gun-left", 2.2, 2, 6, RED, 0.8),
            volley.aimed("wing-gun-right", 2.2, 2, 6, RED, 1.9),
            volley.burst("nose-turret", 2.6, 3, 0.12, ORANGE, 1.3),
            volley.fan("tail-turret", 3.0, 5, 10, BLUE, 2.2),
            volley.laser("dorsal-laser", 7.5, 1.4, 3.2),
        ],
        [
            [volley.aimed("core", 2.8, 1, 0, GOLD, 1.4)],
            [volley.aimed("core", 2.6, 3, 8, GOLD, 1)],
            [volley.fan("core", 2.4, 5, 12, GOLD, 0.9)],
            [volley.burst("core", 2.4, 4, 0.13, RED, 0.7)],
            [
                volley.fan("core", 2.6, 7, 12, GOLD, 0.8),
                volley.aimed("core", 3.0, 1, 0, RED, 1.6),
            ],
            [
                volley.ring("core", 1.4, 14, 9, BLUE, 0.4),
                volley.fan("core", 2.8, 5, 12, GOLD, 1.2),
            ],
        ],
    ),
})


def on_rig(weapon: Any) -> Any:
    """Return a hidden weapon that rises in place out of a piece the view rig morphs (BOSS-46).

    As `hidden_weapons.tail_cannon` (D-228): its look is on a `rig`, so it comes out of no armour
    region and does not swing up on a hinge; the model rises it out of the morphing piece.
    """
    return merge(weapon, {"look": merge(weapon.look, {"rig": True})})


# Where the hidden weapons stand: the mortars on the wingtips, in the opened floats
# (FB-SEAPLANE-LEVIATHAN-09); the hangar on the centre line on the bow's floor, the sweepers on
# the inner engines' cowlings, in their opened spinners (FB-SEAPLANE-LEVIATHAN-10).
MORTAR_AT = [FLOAT_X, -8]
MORTAR_POD = [WING_TOP + 0.6, WING_TOP + 3.4]
HANGAR_AT = [0, -60]
HANGAR_POD = [BAY_FLOOR, BAY_FLOOR + 5]
SWEEPER_AT = [ENGINES[0], -22]
SWEEPER_POD = [NACELLE_H + NACELLE_RADIUS + 0.4, NACELLE_H + NACELLE_RADIUS + 2.6]


def _bow_door() -> list[list[float]]:
    """Return the right bow door's outline: the bow's right half from the stem to `BOW_END`."""
    result: list[list[float]] = [q for q in HULL if q[1] < BOW_END]
    result.append([13.3, BOW_END])
    result.append([0, BOW_END])
    return result


def _float() -> list[list[float]]:
    """Return the right float's outline (with its struts' feet)."""
    x0 = FLOAT_X - FLOAT_HALF - 0.5
    x1 = FLOAT_X + FLOAT_HALF + 0.5
    return [[x0, FLOAT[0] - 1], [x1, FLOAT[0] - 1], [x1, FLOAT[1] + 1], [x0, FLOAT[1] + 1]]


def _hatch() -> list[list[float]]:
    return [
        [
            ROTOR_AT[0] + 6.2 * math.cos(k * math.pi / 4 + math.pi / 8),
            ROTOR_AT[1] + 6.2 * math.sin(k * math.pi / 4 + math.pi / 8),
        ]
        for k in range(8)
    ]


# FB-SEAPLANE-LEVIATHAN-10: each bow door swings out about its after outer corner, about the
# vertical.
DOOR_SWING = swing([13.3, BOW_END, DECK], "up", [0, DOOR_OPEN])

# Its transformations: once both wing guns are gone its floats morph into mortars (their armour
# region hands over to the view rig, which flips them up and splits them open); once its nose and
# tail turrets are gone its bow doors swing apart on a hangar and its inner engines' spinners
# morph into sweepers. The hatch over the stern rotor bursts as the rotor comes into use, in its
# last stage (BOSS-58).
SEAPLANE_LEVIATHAN = with_weapons(
    merge(
        _SEAPLANE_LEVIATHAN,
        {
            "transformParts": [
                ["wing-gun-left", "wing-gun-right"],
                ["nose-turret", "tail-turret"],
            ]
        },
    ),
    [
        on_rig(
            hidden_weapon(
                "mortar-left",
                "mortar",
                [-MORTAR_AT[0], MORTAR_AT[1]],
                6,
                660,
                1,
                "orange",
                1.2,
                MORTAR_POD,
            )
        ),
        on_rig(
            hidden_weapon("mortar-right", "mortar", MORTAR_AT, 6, 660, 1, "orange", 2.0, MORTAR_POD)
        ),
        hidden_weapon("hangar", "hangar", HANGAR_AT, 9, 820, 2, "orange", 1.6, HANGAR_POD),
        on_rig(
            hidden_weapon(
                "sweeper-left",
                "sweeper",
                [-SWEEPER_AT[0], SWEEPER_AT[1]],
                5,
                820,
                2,
                "red",
                1.2,
                SWEEPER_POD,
            )
        ),
        on_rig(
            hidden_weapon(
                "sweeper-right", "sweeper", SWEEPER_AT, 5, 820, 2, "red", 3.0, SWEEPER_POD
            )
        ),
    ],
    concat(
        [armour_region("floats", 1, _float(), "shell", [FLOAT_KEEL - 0.5, WING_UNDER])],
        concat(
            moving_region("bow-door", 2, _bow_door(), DOOR_SWING, None, [BAY_FLOOR, 1000]),
            [armour_region("rotor-hatch", None, _hatch(), "ring", None, False, "stern-rotor")],
        ),
    ),
)
