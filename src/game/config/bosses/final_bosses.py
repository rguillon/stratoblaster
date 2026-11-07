# Copyright (c) 2026 Renaud Guillon
"""The World 1 final bosses (specs/bosses/final/1-1-storm-petrel.md to 1-5-overlord.md).

4 to 6 destroyable parts each (BOSS-13). Offsets in px from the boss's centre, X right and Y up
(its nose points down, at -Y). Stage patterns as for the mini bosses (see `mini_bosses.py`); the
core of a final boss always drops a bonus (BOSS-57).
"""

from game.config.bosses.boss_guns import gun_mount, laser_mount, missile_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, slide, swing
from game.config.bosses.weapon_kinds import WEAPON_FIRE
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


def fpart(part_id: str, at: list[Any], radius: float, health: float, options: Any = None) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57, `part_drop_chance`)."""
    extra = {} if options == None else options
    return part(part_id, at, radius, health, merge({"drop": 0.6}, extra))


RED = bullet("red", 190)
MAGENTA = bullet("magenta", 185)
GREEN = bullet("green", 180)
ORANGE = bullet("orange", 175)
BLUE = bullet("blue", 190)
PURPLE = bullet("purple", 195)

# The guns' muzzles (phase 7 review): the tips of the barrels their models draw, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).

# The Mesa Fortress's lances' laser emitters (FB-MESA-FORTRESS-03).
MESA_LANCE = {"size": 7, "bore": 3.5, "length": 30}

# The Refinery Titan's rotary turrets' rotors: three barrels, one per bullet of their rings
# (FB-REFINERY-TITAN-03).
TITAN_ROTARY = {"size": 6, "barrels": 3, "layout": "ring", "bore": 1.3, "length": 9}

# The Storm Petrel's wing pods' fan turrets (FB-STORM-PETREL-03).
PETREL_POD = {"size": 5.5, "barrels": 3, "gap": 1.2, "bore": 1.2, "length": 7}

# 1-1: a seaplane bomber; wing gun pods (they shield the core), a tail missile rack, a belly plate
# (FB-STORM-PETREL-07).
# Once its second transformation has revealed its cannon and sweepers (stage 4), its batteries
# (FB-STORM-PETREL-10) fire twice as often: a second fan each, between their usual ones.
_BATTERY = WEAPON_FIRE.battery
_BATTERY_RUSH = [
    volley.fan(
        part_id,
        _BATTERY.every,
        _BATTERY.count,
        _BATTERY.spacingDeg,
        bullet("magenta", _BATTERY.speed),
        first + _BATTERY.every / 2,
    )
    for part_id, first in [("battery-left", 1.2), ("battery-right", 2.0)]
]

_STORM_PETREL = record({
    "id": "storm-petrel",
    # Its points, its core's drop and its parts' drops (FB-STORM-PETREL-13).
    "stats": stats({
        "id": "storm-petrel",
        "name": "Storm Petrel",
        "size": 4.5,
        "coreRadius": 20,
        "coreHealth": 2010,
        "points": 8000,
        "groundSpeed": 1.5,
        "coreDrop": 1,
        "parts": [
            fpart("pod-left", [-56, 4], 15, 1010),
            fpart("pod-right", [56, 4], 15, 1010),
            fpart("missile-rack", [0, 40], 14, 820),
            fpart("belly-plate", [0, -32], 15, 920),
        ],
    }),
    # Where it stops and how it moves in place (FB-STORM-PETREL-06).
    "stopFraction": 0.72,
    "sway": {"amplitude": 45, "period": 8},
    "bob": {"amplitude": 10, "period": 4},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-STORM-PETREL-03): a fan turret on each wing pod's collar, a block
    # of missile ports in the tail rack. The core has none: it dies with its last gun (BOSS-58).
    "mounts": [
        gun_mount("pod-left", "pod-left", [-56, -6], 19.3, PETREL_POD),
        gun_mount("pod-right", "pod-right", [56, -6], 19.3, PETREL_POD),
        missile_mount("missile-rack", "missile-rack", [0, 40], 12.6, 4),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-STORM-PETREL-08): the wing pods
    # fire fast, in turn; the core never fires.
    "stages": stages(
        [
            volley.fan("pod-left", 1.2, 3, 15, MAGENTA, 0.6),
            volley.fan("pod-right", 1.2, 3, 15, MAGENTA, 1.2),
            volley.missiles("missile-rack", 5.5, 4, 30, 3),
        ],
        [[], [], [], [], _BATTERY_RUSH],
    ),
})

# The Gull Mothership's flak growths' twin-barrelled turrets, sweeping their aimed pairs
# (FB-GULL-MOTHERSHIP-03).
GULL_FLAK = {"size": 8.5, "barrels": 2, "gap": 3.2, "bore": 1.1, "length": 7.5}

# 1-2: a wide carrier; two hangar bays launch Gnats, two flak turrets; all four shield the core
# (FB-GULL-MOTHERSHIP-07).
_GULL_MOTHERSHIP = record({
    "id": "gull-mothership",
    # Its points, its core's drop and its parts' drops (FB-GULL-MOTHERSHIP-13).
    "stats": stats({
        "id": "gull-mothership",
        "name": "Gull Mothership",
        "size": 5,
        "coreRadius": 20,
        "coreHealth": 2280,
        "points": 9000,
        "groundSpeed": 0.6,
        "coreDrop": 1,
        "parts": [
            fpart("hangar-left", [-62, 6], 18, 1050),
            fpart("hangar-right", [62, 6], 18, 1050),
            fpart("flak-left", [-28, -32], 12, 790),
            fpart("flak-right", [28, -32], 12, 790),
        ],
    }),
    # Where it stops and how it moves in place (FB-GULL-MOTHERSHIP-06).
    "stopFraction": 0.74,
    "sway": {"amplitude": 40, "period": 9},
    "bob": {"amplitude": 8, "period": 4.5},
    "launches": [
        {"from": "hangar-left", "kind": "hornets", "count": 3, "every": 7, "first": 2.5},
        {"from": "hangar-right", "kind": "hornets", "count": 3, "every": 7, "first": 6},
    ],
    "guns": {},
    # Its gun mounts (BOSS-58, FB-GULL-MOTHERSHIP-03): a twin-gun turret on each flak growth's
    # crown, and the core's laser eye at its nose, the turret on the front of its back (its aimed
    # shots and fans) and two rotors down its spine (its rings of 8, then of 12).
    "mounts": [
        gun_mount("flak-left", "flak-left", [-28, -32], 6.5, GULL_FLAK),
        gun_mount("flak-right", "flak-right", [28, -32], 6.5, GULL_FLAK),
        laser_mount("eye", "core", [0, -58], 4.7, {"size": 6, "bore": 3.5, "length": 9.2}),
        gun_mount(
            "prow",
            "core",
            [0, -29],
            22,
            {"size": 6.5, "barrels": 5, "gap": 1.3, "bore": 1.1, "length": 8},
        ),
        gun_mount(
            "spine-rotor",
            "core",
            [0, 11],
            22,
            {"size": 6, "barrels": 12, "layout": "ring", "bore": 0.9, "length": 4.5},
        ),
        gun_mount(
            "tail-rotor",
            "core",
            [0, 31],
            22,
            {"size": 4.5, "barrels": 8, "layout": "ring", "bore": 0.9, "length": 4},
        ),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-GULL-MOTHERSHIP-08).
    "stages": stages(
        [
            volley.aimed("flak-left", 1.9, 2, 8, GREEN, 0.9),
            volley.aimed("flak-right", 1.9, 2, 8, GREEN, 1.85),
        ],
        [
            [volley.laser("core", 7, 1.5, 4)],
            [volley.laser("core", 6, 1.5, 2), volley.aimed("core", 2.6, 1, 0, ORANGE, 1)],
            [volley.laser("core", 5.5, 1.5, 2), volley.fan("core", 2.6, 5, 14, ORANGE, 1)],
            [
                volley.laser("core", 5, 1.5, 2),
                merge(volley.ring("core", 2.2, 8, 0, ORANGE, 1), {"mount": "tail-rotor"}),
            ],
            [volley.laser("core", 4.5, 1.6, 1.5), volley.ring("core", 1.5, 12, 9, GREEN, 0.4)],
        ],
    ),
})

# 1-3: a flying fortress; two laser lances and two missile silos shield the core
# (FB-MESA-FORTRESS-07).
_MESA_FORTRESS = record({
    "id": "mesa-fortress",
    # Its points, its core's drop and its parts' drops (FB-MESA-FORTRESS-13).
    "stats": stats({
        "id": "mesa-fortress",
        "name": "Mesa Fortress",
        "size": 5,
        "coreRadius": 22,
        "coreHealth": 3000,
        "points": 10000,
        "groundSpeed": 0,
        "coreDrop": 1,
        "parts": [
            fpart("lance-left", [-58, -12], 15, 1050),
            fpart("lance-right", [58, -12], 15, 1050),
            fpart("silo-left", [-28, 32], 13, 1500),
            fpart("silo-right", [28, 32], 13, 1500),
        ],
    }),
    # Where it stops and how it moves in place (FB-MESA-FORTRESS-06).
    "stopFraction": 0.74,
    "sway": {"amplitude": 35, "period": 10},
    "bob": {"amplitude": 6, "period": 5},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-MESA-FORTRESS-03): a laser emitter in each forelimb's cradle, a
    # block of four missile ports in each silo's mouth, and the core's fan turret on its brow (its
    # fans and aimed shots) and the rotor on its back behind the keep (its rings).
    "mounts": [
        laser_mount("lance-left", "lance-left", [-58, -16], 5, MESA_LANCE),
        laser_mount("lance-right", "lance-right", [58, -16], 5, MESA_LANCE),
        missile_mount("silo-left", "silo-left", [-28, 32], 12.4, 4),
        missile_mount("silo-right", "silo-right", [28, 32], 12.4, 4),
        gun_mount(
            "brow",
            "core",
            [0, -25],
            14,
            {"size": 6.5, "barrels": 7, "gap": 1.2, "bore": 1.1, "length": 9},
        ),
        gun_mount(
            "back-rotor",
            "core",
            [0, 48],
            13.5,
            {"size": 5, "barrels": 14, "layout": "ring", "bore": 0.7, "length": 3.2},
        ),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-MESA-FORTRESS-08); its fans all
    # 12 degrees apart, as the brow turret's barrels (BOSS-58).
    "stages": stages(
        [
            volley.laser("lance-left", 6, 1.4, 2),
            volley.laser("lance-right", 6, 1.4, 5),
            volley.missiles("silo-left", 5, 1, 0, 3.5),
            volley.missiles("silo-right", 5, 1, 0, 6),
        ],
        [
            [volley.fan("core", 3, 3, 12, RED, 1.5)],
            [volley.fan("core", 2.6, 5, 12, RED, 0.8)],
            [
                volley.fan("core", 2.6, 5, 12, RED, 0.8),
                volley.aimed("core", 2.2, 1, 0, ORANGE, 1.4),
            ],
            [volley.fan("core", 2.2, 7, 12, RED, 0.6)],
            [
                volley.ring("core", 1.5, 14, 12, ORANGE, 0.4),
                volley.fan("core", 2.6, 5, 12, RED, 1.2),
            ],
        ],
    ),
})

# 1-4: a heavy tanker-gunship; fuel tanks burst into bullet rings, rotary turrets spiral
# (FB-REFINERY-TITAN-07).
_REFINERY_TITAN = record({
    "id": "refinery-titan",
    # Its points, its core's drop and its parts' drops (FB-REFINERY-TITAN-12).
    "stats": stats({
        "id": "refinery-titan",
        "name": "Refinery Titan",
        "size": 5.5,
        "coreRadius": 22,
        "coreHealth": 4740,
        "points": 12000,
        "groundSpeed": 0.3,
        "coreDrop": 1,
        "parts": [
            fpart("tank-left", [-66, 18], 17, 1400),
            fpart("tank-right", [66, 18], 17, 1400),
            fpart("turret-left", [-32, -24], 14, 1810),
            fpart("turret-right", [32, -24], 14, 1810),
            fpart("missile-battery", [0, 38], 14, 1530),
        ],
    }),
    # Where it stops and how it moves in place (FB-REFINERY-TITAN-06).
    "stopFraction": 0.74,
    "sway": {"amplitude": 30, "period": 10},
    "bob": {"amplitude": 6, "period": 5},
    "breakRings": {
        "tank-left": {"count": 12, "bullet": ORANGE},
        "tank-right": {"count": 12, "bullet": ORANGE},
    },
    "guns": {},
    # Its gun mounts (BOSS-58, FB-REFINERY-TITAN-03): a three-barrelled rotor on each rotary
    # turret's base, a block of six missile ports on the brood, and the core's on its rear shell
    # either side of the brood (out of its plating's way): a fan turret (its aimed shots, bursts
    # and fans) on its right, a rotor (its rings) on its left. Its fuel tanks fire nothing: they
    # burst into rings (`breakRings`).
    "mounts": [
        gun_mount("turret-left", "turret-left", [-32, -24], 15, TITAN_ROTARY),
        gun_mount("turret-right", "turret-right", [32, -24], 15, TITAN_ROTARY),
        missile_mount("missile-battery", "missile-battery", [0, 38], 21, 6),
        gun_mount(
            "rear-turret",
            "core",
            [20, 28],
            12,
            {"size": 5, "barrels": 7, "gap": 1, "bore": 1, "length": 7},
        ),
        gun_mount(
            "rear-rotor",
            "core",
            [-20, 28],
            12,
            {"size": 4.5, "barrels": 14, "layout": "ring", "bore": 0.6, "length": 2.8},
        ),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-REFINERY-TITAN-08); its fans all
    # 12 degrees apart, as the rear turret's barrels (BOSS-58).
    "stages": stages(
        [
            volley.ring("turret-left", 0.7, 3, 19, ORANGE, 0.5),
            volley.ring("turret-right", 0.7, 3, -19, ORANGE, 0.85),
            volley.missiles("missile-battery", 5.5, 2, 30, 3),
        ],
        [
            [volley.aimed("core", 3, 1, 0, BLUE, 1.6)],
            [volley.aimed("core", 2.6, 3, 12, BLUE, 0.8)],
            [volley.burst("core", 2.4, 4, 0.14, BLUE, 0.6)],
            [volley.fan("core", 2.4, 5, 12, BLUE, 0.6)],
            [
                volley.fan("core", 2.2, 7, 12, BLUE, 0.6),
                volley.aimed("core", 2.6, 1, 0, ORANGE, 1.2),
            ],
            [
                volley.ring("core", 1.3, 14, 9, BLUE, 0.4),
                volley.burst("core", 2.8, 3, 0.14, ORANGE, 1),
            ],
        ],
    ),
})

# 1-5: a city-ship; wing lasers, missile batteries, and two shield generators guard the core
# (FB-OVERLORD-07).
_OVERLORD = record({
    "id": "overlord",
    # Its points, its core's drop and its parts' drops (FB-OVERLORD-13).
    "stats": stats({
        "id": "overlord",
        "name": "Overlord",
        "size": 6,
        "coreRadius": 24,
        "coreHealth": 5540,
        "points": 15000,
        "groundSpeed": 0.25,
        "coreDrop": 1,
        "parts": [
            fpart("laser-left", [-78, -6], 15, 1660),
            fpart("laser-right", [78, -6], 15, 1660),
            fpart("battery-left", [-46, 30], 14, 1520),
            fpart("battery-right", [46, 30], 14, 1520),
            fpart("generator-left", [-34, -36], 13, 1940),
            fpart("generator-right", [34, -36], 13, 1940),
        ],
    }),
    # Where it stops and how it moves in place (FB-OVERLORD-06).
    "stopFraction": 0.75,
    "sway": {"amplitude": 25, "period": 11},
    "bob": {"amplitude": 6, "period": 5},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-OVERLORD-03): a laser on each wing cannon's gland, a block of six
    # ports on each battery; on the citadel's weapon array a fanned turret in the middle (its aimed
    # shots, purple bursts and fans) between a twin cannon (its red bursts, on a turret of its own:
    # they aim at the player while its fans go down the screen) and a laser; the 14-barrel rotor on
    # its roof (its last ring), the missile ports on the boulevard behind it and a 10-barrel rotor
    # at the boulevard's tail (its first ring).
    "mounts": [
        laser_mount(
            "laser-left", "laser-left", [-78, -18], 6, {"size": 4.5, "bore": 2.4, "length": 12}
        ),
        laser_mount(
            "laser-right", "laser-right", [78, -18], 6, {"size": 4.5, "bore": 2.4, "length": 12}
        ),
        missile_mount("battery-left", "battery-left", [-46, 30], 14, 6),
        missile_mount("battery-right", "battery-right", [46, 30], 14, 6),
        gun_mount(
            "array",
            "core",
            [0, -28],
            19,
            {"size": 6, "barrels": 7, "gap": 1, "bore": 1.1, "length": 8},
        ),
        gun_mount(
            "array-cannon",
            "core",
            [14, -24],
            19,
            {"size": 4, "barrels": 2, "gap": 2.6, "bore": 1.2, "length": 7},
        ),
        laser_mount("array-laser", "core", [-14, -24], 19, {"size": 4, "bore": 2, "length": 9}),
        gun_mount(
            "roof-rotor",
            "core",
            [0, 0],
            30.8,
            {"size": 5, "barrels": 14, "layout": "ring", "bore": 0.9, "length": 5},
        ),
        gun_mount(
            "tail-rotor",
            "core",
            [0, 48],
            10,
            {"size": 4.5, "barrels": 10, "layout": "ring", "bore": 0.9, "length": 4.5},
        ),
        missile_mount("hatches", "core", [0, 34], 10, 4),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-OVERLORD-08).
    "stages": stages(
        [
            volley.laser("laser-left", 6.5, 1.4, 2),
            volley.laser("laser-right", 6.5, 1.4, 5.25),
            volley.missiles("battery-left", 5.5, 2, 24, 3.5),
            volley.missiles("battery-right", 5.5, 2, 24, 6.25),
        ],
        [
            [volley.aimed("core", 2.8, 1, 0, PURPLE, 1.4)],
            [volley.aimed("core", 2.4, 3, 12, PURPLE, 0.8)],
            [volley.burst("core", 2.4, 4, 0.13, PURPLE, 0.6)],
            # 12 degrees apart: the array's barrels' spacing (BOSS-58).
            [volley.fan("core", 2.4, 5, 12, PURPLE, 0.6)],
            [merge(volley.ring("core", 2, 10, 6, PURPLE, 0.6), {"mount": "tail-rotor"})],
            [
                volley.fan("core", 2.2, 7, 12, PURPLE, 0.6),
                merge(volley.burst("core", 2.6, 3, 0.13, RED, 1), {"mount": "array-cannon"}),
            ],
            [
                volley.ring("core", 1.2, 14, 9, PURPLE, 0.4),
                volley.laser("core", 5, 1.4, 2),
                volley.missiles("core", 6, 2, 30, 3),
            ],
        ],
    ),
})

# Its transformations (D-230; what it sheds and moves, FB-STORM-PETREL-05): once both wing pods are
# gone its outer wings swing 30 degrees forward about their leading edges' roots, and a gun battery
# slides out of each flank of its body onto each (FB-STORM-PETREL-10); once its rack and plate are
# gone its tail plating bursts off for a heavy cannon and its wing roots' for a pair of sweepers
# (FB-STORM-PETREL-11).
STORM_PETREL = with_weapons(
    merge(
        _STORM_PETREL,
        {
            "transformParts": [["pod-left", "pod-right"], ["missile-rack", "belly-plate"]],
            # Its batteries keep firing in its anger after its second transformation.
            "rageAlso": ["battery-left", "battery-right"],
        },
    ),
    [
        hidden_weapon(
            "battery-left", "battery", [-50, -5], 8, 810, 1, "magenta", 1.2, [9, 15], None, [-6, -5]
        ),
        hidden_weapon(
            "battery-right", "battery", [50, -5], 8, 810, 1, "magenta", 2.0, [9, 15], None, [6, -5]
        ),
        hidden_weapon("cannon", "cannon", [0, 32], 11, 1010, 2, "red", 1.4, 14.5),
        hidden_weapon("sweeper-left", "sweeper", [-19, -12], 6, 1010, 2, "magenta", 2.2, 12.9),
        hidden_weapon("sweeper-right", "sweeper", [19, -12], 6, 1010, 2, "magenta", 4.6, 12.9),
    ],
    concat(
        moving_region(
            "outer-wings",
            1,
            # The outer wing's own outline, beyond the hinge at x 31 (the membrane the model draws
            # there, D-254).
            [[31, -13.4], [36, -12], [74, -3], [77, 1], [76, 7], [56, 10], [31, 13.8]],
            swing([31, -13.4, 8], "up", [0, -30]),
            None,
            [4, 1000],
        ),
        [
            # The tail plating: a lozenge the shell's own shape over the tail (its tail at +Y).
            armour_region(
                "tail",
                2,
                [[-8, 48], [8, 48], [12.5, 30], [12.5, 18], [-12.5, 18], [-12.5, 30]],
                "shell",
                None,
                False,
            ),
            # The wing root: the membrane from the body's flank to the hinge, with its engine sac.
            armour_region(
                "wing-roots",
                2,
                [[12.5, -18.7], [31, -13.4], [31, 13.9], [30, 14], [12.5, 18.7]],
                "wing",
            ),
        ],
    ),
)

# Its hidden weapons (boss transformations, D-224; what it sheds, FB-GULL-MOTHERSHIP-05): at
# transformation 1 its flank armour bursts off, baring a dark metal frame, and a pair of laser
# lances unfold (FB-GULL-MOTHERSHIP-10); at transformation 2 its wing armour bursts off, baring a
# dark metal frame, and a pair of ring emitters unfold (FB-GULL-MOTHERSHIP-11).
GULL_MOTHERSHIP = with_weapons(
    _GULL_MOTHERSHIP,
    [
        hidden_weapon("pike-left", "lance", [-35, 23], 9, 840, 1, "green", 1.2, 9.6),
        hidden_weapon("pike-right", "lance", [35, 23], 9, 840, 1, "green", 2.0, 9.6),
        hidden_weapon("orb-left", "orb", [-37, -9], 7, 1050, 2, "green", 1.2, 7.6),
        hidden_weapon("orb-right", "orb", [37, -9], 7, 1050, 2, "green", 2.0, 7.6),
    ],
    [
        # The mantle's flank plates, out to its rim (D-254): the rear ones behind the middle, the
        # front ones in front of it, cut across the mantle's front at y -38.
        armour_region("flanks", 1, [[18, 6], [47, 6], [47, 30], [34, 48], [18, 54.4]], "wing"),
        armour_region(
            "wings", 2, [[22, 6], [47, 6], [47, -20], [40, -32], [33.1, -38], [22, -38]], "wing"
        ),
    ],
)

# Its transformations (D-230; what it sheds and moves, FB-MESA-FORTRESS-05): once both lances are
# gone its wing fronts burst off for a pair of gun batteries (FB-MESA-FORTRESS-10); once both silos
# are gone its keep splits along its ridge, the two halves of its roof sliding apart over a dark
# metal lattice as a heavy cannon rises between them, and its flank armour bursts off for a pair of
# sweepers (FB-MESA-FORTRESS-11).
MESA_FORTRESS = with_weapons(
    merge(
        _MESA_FORTRESS,
        {"transformParts": [["lance-left", "lance-right"], ["silo-left", "silo-right"]]},
    ),
    [
        hidden_weapon("battery-left", "battery", [-44, -26], 10, 1200, 1, "red", 1.2, 14),
        hidden_weapon("battery-right", "battery", [44, -26], 10, 1200, 1, "red", 2.2, 14),
        hidden_weapon("cannon", "cannon", [0, 14], 14, 1500, 2, "orange", 1.4, 22),
        hidden_weapon("sweeper-left", "sweeper", [-60, 22], 8, 1500, 2, "red", 2.4, 14),
        hidden_weapon("sweeper-right", "sweeper", [60, 22], 8, 1500, 2, "red", 6.4, 14),
    ],
    concat(
        [
            # The skirt's front flank plates, either side of the head, out to the rim (D-254).
            armour_region(
                "wings",
                1,
                [[16, -3.5], [46, -3.5], [46, -28], [38, -38], [22, -46], [16, -46.5]],
                "wing",
            ),
        ],
        # The keep's roof halves: the upper shell's own footprint, cut along the ridge.
        moving_region(
            "roof",
            2,
            [[0, -18], [22, -18], [22, 36], [0, 36]],
            slide([[0, 0, 0], [16, 0, 0]]),
            "shell",
            [16, 1000],
        ),
        [
            # The skirt's rear flank plates, with the forelimbs' scaly sinews (the sweepers rise
            # out of the limbs).
            armour_region(
                "flanks",
                2,
                [[34, -3.5], [46, -3.5], [46, 6], [72, 6], [80, 23], [46, 24], [46, 36], [34, 50]],
                "wing",
            ),
        ],
    ),
)

# Its hidden weapons (boss transformations, D-224; what it sheds, FB-REFINERY-TITAN-05): at
# transformation 1 its back plating bursts off, baring a dark metal frame, and a pair of gatling
# turrets unfold (FB-REFINERY-TITAN-10); at transformation 2 its spine plating bursts off, baring a
# dark metal frame, and a pair of ring emitters unfold (FB-REFINERY-TITAN-11).
REFINERY_TITAN = with_weapons(
    _REFINERY_TITAN,
    [
        hidden_weapon("gatling-left", "gatling", [-9, -13], 7, 1450, 1, "orange", 1.2, 25.7),
        hidden_weapon("gatling-right", "gatling", [9, -13], 7, 1450, 1, "orange", 2.0, 25.7),
        hidden_weapon("orb-left", "orb", [-9, -35], 7, 1810, 2, "orange", 1.2, 18.9),
        hidden_weapon("orb-right", "orb", [9, -35], 7, 1810, 2, "orange", 2.0, 18.9),
    ],
    [
        # The middle length of its shell, the plated skull over the core riding it (D-254).
        armour_region(
            "back",
            1,
            [[-27, 20], [27, 20], [32, 8], [32, -14], [27, -24], [-27, -24], [-32, -14], [-32, 8]],
            "shell",
            None,
            False,
        ),
        # The front length of its shell, out to its nose.
        armour_region(
            "spine",
            2,
            [
                [-27, -24],
                [27, -24],
                [27, -36],
                [20, -47],
                [17, -57],
                [6, -66],
                [-6, -66],
                [-17, -57],
                [-20, -47],
                [-27, -36],
            ],
            "shell",
            None,
            False,
        ),
    ],
)

# Its hidden weapons (boss transformations, D-224; what it sheds, FB-OVERLORD-05): at
# transformation 1 its flank armour bursts off, baring a dark metal frame, and a pair of laser
# lances unfold (FB-OVERLORD-10); at transformation 2 its spine plating bursts off, baring a dark
# metal frame, and a pair of flak mortars unfold (FB-OVERLORD-11).
OVERLORD = with_weapons(
    _OVERLORD,
    [
        hidden_weapon("pike-left", "lance", [-47, -1], 11, 1550, 1, "purple", 1.2, 41.1),
        hidden_weapon("pike-right", "lance", [47, -1], 11, 1550, 1, "purple", 2.0, 41.1),
        hidden_weapon("mortar-left", "mortar", [-13, -55], 11, 1940, 2, "purple", 1.2, 14.1),
        hidden_weapon("mortar-right", "mortar", [13, -55], 11, 1940, 2, "purple", 2.0, 14.1),
    ],
    [
        # The deck's flank plates, out to its edge, the city on them (D-254).
        armour_region(
            "flanks", 1, [[32, -42], [52, -42], [64, -18], [64, 30], [62.8, 32], [32, 32]], "wing"
        ),
        # The deck's front plate, before the citadel, with the boulevard's front.
        armour_region(
            "spine",
            2,
            [
                [0, -64],
                [26, -60],
                [52, -42],
                [32, -42],
                [32, -34],
                [-32, -34],
                [-32, -42],
                [-52, -42],
                [-26, -60],
            ],
            "shell",
            None,
            False,
        ),
    ],
)
