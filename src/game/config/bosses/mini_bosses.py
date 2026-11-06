# Copyright (c) 2026 Renaud Guillon
"""The World 1 mini bosses (specs/bosses/mini/1-1-reef-warden.md to 1-5-sentinel.md).

2 or 3 destroyable parts each (BOSS-13). Offsets in px from the boss's centre, X right and Y up
(its nose points down, at -Y). The stage patterns are the agent's design (BOSS-21): the parts fire
the same while they stand, the core fires something new at every stage, and the last stage (only
the core left) a ring or spiral used before by no stage of that boss. Health values are tuned so
that a player with guns at level 3 always on target needs the fight times of BOSS-56 (World 1's:
WLD-1-29), their full health going up from 1-1 to 1-5 (BOSS-55, WLD-1-27).
"""

import math

from game.config.bosses.boss_guns import gun_mount, laser_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import (
    armour_region,
    hidden_weapon,
    tail_cannon,
    with_weapons,
)
from game.config.record import merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


ORANGE = bullet("orange", 170)
RED = bullet("red", 190)
BLUE = bullet("blue", 185)
GREEN = bullet("green", 180)
PURPLE = bullet("purple", 195)

# The guns' muzzles (phase 7 review): the tips of the barrels their models draw, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).

# The Reef Warden's side cannons' twin-barrelled turrets (MB-REEF-WARDEN-03).
REEF_CANNON = {"size": 9, "barrels": 2, "gap": 5, "bore": 1.6, "length": 11}

# The Scorpion's claw cannons' turrets: three barrels side by side, sweeping their aimed fans
# (MB-SCORPION-03, MB-SCORPION-08).
SCORPION_CLAW = {"size": 4.5, "barrels": 3, "gap": 1.2, "bore": 1.1, "length": 11}

# The Sentinel's hull guns' twin-barrelled turrets, sweeping their aimed pairs (MB-SENTINEL-03).
SENTINEL_GUN = {"size": 9, "barrels": 2, "gap": 3.6, "bore": 1.3, "length": 12}

# 1-1: a wide hover-gunboat with a cyan ring under its rim; two side cannons shield the core
# (MB-REEF-WARDEN-07).
_REEF_WARDEN = record({
    "id": "reef-warden",
    # Its points and its parts' drops (MB-REEF-WARDEN-11).
    "stats": stats({
        "id": "reef-warden",
        "name": "Reef Warden",
        "size": 3,
        "coreRadius": 20,
        "coreHealth": 960,
        "points": 3000,
        "groundSpeed": 0.5,
        "parts": [
            part("cannon-left", [-36, -2], 14, 620),
            part("cannon-right", [36, -2], 14, 620),
        ],
    }),
    # Where it stops and how it moves in place (MB-REEF-WARDEN-06).
    "stopFraction": 0.72,
    "sway": {"amplitude": 70, "period": 7},
    "bob": {"amplitude": 8, "period": 3.5},
    "guns": {},
    # Its gatlings come out once both its side cannons are destroyed (MB-REEF-WARDEN-10).
    "transforms": [2],
    # Its gun mounts (BOSS-58, MB-REEF-WARDEN-03): a side cannon on each flank. Its core carries
    # none: its gatlings are its last guns, and it dies with them.
    "mounts": [
        gun_mount("cannon-left", "cannon-left", [-36, -2], 4, REEF_CANNON),
        gun_mount("cannon-right", "cannon-right", [36, -2], 4, REEF_CANNON),
    ],
    # Its parts' volleys; its core does not fire (MB-REEF-WARDEN-08).
    "stages": stages(
        [
            volley.burst("cannon-left", 2.6, 3, 0.18, RED, 1),
            volley.burst("cannon-right", 2.6, 3, 0.18, RED, 2.3),
        ],
        [[]],
    ),
})

# The Breakwater's mortars, a single short, fat barrel each in a cradle on a turntable, its axis
# high enough for the barrel to rest in it (MB-BREAKWATER-03).
BREAKWATER_MORTAR = {
    "size": 7,
    "barrels": 1,
    "bore": 3.6,
    "length": 4,
    "style": "mortar",
    "axis": 0.8,
}

# 1-2: an armoured flying barge; its front plate shields the core, two mortars lob big bullets
# (MB-BREAKWATER-07).
_BREAKWATER = record({
    "id": "breakwater",
    # Its points and its parts' drops (MB-BREAKWATER-11).
    "stats": stats({
        "id": "breakwater",
        "name": "Breakwater",
        "size": 3,
        "coreRadius": 18,
        "coreHealth": 930,
        "points": 3500,
        "groundSpeed": 0.4,
        "parts": [
            part("ram-plate", [0, -34], 18, 810),
            part("mortar-left", [-34, 12], 13, 430),
            part("mortar-right", [34, 12], 13, 430),
        ],
    }),
    # Where it stops and how it moves in place (MB-BREAKWATER-06).
    "stopFraction": 0.72,
    "sway": {"amplitude": 60, "period": 8},
    "bob": {"amplitude": 6, "period": 4},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-BREAKWATER-03): a mortar's single heavy barrel on each flank
    # (the ram plate has no weapon), and the core's bow turret in its mouth (its fans, aimed shots
    # and bursts) and the rotor on the plate grafted on its shell (its rings).
    "mounts": [
        gun_mount("mortar-left", "mortar-left", [-34, 12], 9.5, BREAKWATER_MORTAR),
        gun_mount("mortar-right", "mortar-right", [34, 12], 9.5, BREAKWATER_MORTAR),
        gun_mount(
            "bow",
            "core",
            [0, -20],
            4.4,
            {"size": 6, "barrels": 3, "gap": 1.2, "bore": 1.2, "length": 4},
        ),
        gun_mount(
            "shell-rotor",
            "core",
            [0, -2],
            16.6,
            {"size": 5, "barrels": 10, "layout": "ring", "bore": 0.9, "length": 3.5},
        ),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-BREAKWATER-08). BOSS-58: the fan
    # spaced as the bow turret's barrels (12°).
    "stages": stages(
        [
            volley.aimed("mortar-left", 2.4, 1, 0, bullet("orange", 110, 7), 1.2),
            volley.aimed("mortar-right", 2.4, 1, 0, bullet("orange", 110, 7), 2.4),
        ],
        [
            [volley.fan("core", 3, 3, 12, RED, 1.6)],
            [volley.aimed("core", 2.4, 3, 12, RED, 0.6)],
            [volley.burst("core", 2.2, 4, 0.15, RED, 0.6)],
            [volley.ring("core", 1.7, 10, 9, RED, 0.4)],
        ],
    ),
})

# The Dust Devil's blade pods' rotors, a barrel each way along the ring (MB-DUST-DEVIL-03).
DUST_DEVIL_ROTOR = {"size": 3.5, "barrels": 2, "layout": "ring", "bore": 1, "length": 6}

# 1-3: a gyro gunship; three blade pods on its turning ring fire spirals and shield the core
# (MB-DUST-DEVIL-07).
_DUST_DEVIL = record({
    "id": "dust-devil",
    # Its points and its parts' drops (MB-DUST-DEVIL-11).
    "stats": stats({
        "id": "dust-devil",
        "name": "Dust Devil",
        "size": 3,
        "coreRadius": 18,
        "coreHealth": 1230,
        "points": 4000,
        "groundSpeed": 0.5,
        "parts": [
            part("blade-1", [0, -40], 14, 620, {"orbits": True}),
            part("blade-2", [34.6, 20], 14, 620, {"orbits": True}),
            part("blade-3", [-34.6, 20], 14, 620, {"orbits": True}),
        ],
    }),
    # Where it stops and how it moves in place (MB-DUST-DEVIL-06).
    "stopFraction": 0.72,
    "sway": {"amplitude": 60, "period": 9},
    "bob": {"amplitude": 10, "period": 3},
    "spinRate": 0.7,
    "guns": {},
    # Its gun mounts (BOSS-58, MB-DUST-DEVIL-03): a two-barrelled rotor on each blade pod, its
    # barrels along the ring (it fires both ways along it, turning with it), and the core's stacked
    # guns on its hub: the rotor (its rings) under the turret (its aimed shots and bursts).
    "mounts": [
        gun_mount("blade-1", "blade-1", [0, -40], 5, merge(DUST_DEVIL_ROTOR, {"restDeg": 90})),
        gun_mount("blade-2", "blade-2", [34.6, 20], 5, merge(DUST_DEVIL_ROTOR, {"restDeg": -30})),
        gun_mount("blade-3", "blade-3", [-34.6, 20], 5, merge(DUST_DEVIL_ROTOR, {"restDeg": 30})),
        gun_mount(
            "hub-turret",
            "core",
            [0, 0],
            9.9,
            {"size": 3.5, "barrels": 3, "gap": 0.8, "bore": 0.8, "length": 5},
        ),
        gun_mount(
            "hub-rotor",
            "core",
            [0, 0],
            7.7,
            {"size": 4.4, "barrels": 12, "layout": "ring", "bore": 0.6, "length": 2.5},
        ),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-DUST-DEVIL-08).
    "stages": stages(
        [
            volley.ring("blade-1", 1, 2, 23, GREEN, 0.4),
            volley.ring("blade-2", 1, 2, 23, GREEN, 0.73),
            volley.ring("blade-3", 1, 2, 23, GREEN, 1.06),
        ],
        [
            [volley.aimed("core", 3, 1, 0, ORANGE, 1.5)],
            [volley.aimed("core", 2.6, 3, 12, ORANGE, 0.8)],
            [volley.burst("core", 2.4, 4, 0.14, ORANGE, 0.6)],
            [volley.ring("core", 1.5, 12, 15, ORANGE, 0.4)],
        ],
    ),
})


def scorpion_arm(side: str) -> Any:
    """Return a Scorpion's arm (phase 7 review, MB-SCORPION-07), the left one drawn at -X.

    It swings at the shoulder, bends at the elbow and turns its claw at the wrist, while the claw's
    jaws open and close. The right arm is its mirror image, a little out of step, so the two arms
    never move together.
    """
    s = 1 if side == "left" else -1
    late = 0 if side == "left" else 0.37

    def joint(x: float, y: float, swing: list[Any], parent: str | None = None) -> Any:
        result = record({
            "x": -s * x,
            "y": y,
            "swing": {
                "amplitudeDeg": s * swing[0],
                "period": swing[1],
                "phase": swing[2] + late,
            },
        })
        if parent is not None:
            result["parent"] = parent + "-" + side
        return result

    # The jaws' hinges, outer and inner: where each claw's jaws turn as its model draws them.
    if side == "left":
        outer = joint(47, -20.5, [12, 1.1, 0], "wrist")
        inner = joint(38.5, -19, [-12, 1.1, 0], "wrist")
    else:
        outer = joint(46.3, -21, [12, 1.1, 0], "wrist")
        inner = joint(39, -19.7, [-12, 1.1, 0], "wrist")
    table: Any = {}
    table["shoulder-" + side] = joint(14, -10, [7, 4.4, 0])
    table["elbow-" + side] = joint(27.5, -18, [12, 3.2, 0.25], "shoulder")
    table["wrist-" + side] = joint(40, -22, [16, 2.4, 0.5], "elbow")
    table["jaw-" + side + "-outer"] = outer
    table["jaw-" + side + "-inner"] = inner
    return table


# 1-4: a gunship with a tail arched over its back, its stinger hanging in front of the core (so
# shots from below reach it); claws spread, the stinger fires a laser (MB-SCORPION-08).
_SCORPION = record({
    "id": "scorpion",
    # Its points and its parts' drops (MB-SCORPION-13).
    "stats": stats({
        "id": "scorpion",
        "name": "Scorpion",
        "size": 3.5,
        "coreRadius": 18,
        "coreHealth": 1470,
        "points": 4500,
        "groundSpeed": 0.5,
        "parts": [
            part("claw-left", [-42, -24], 14, 730, {"joint": "wrist-left"}),
            part("claw-right", [42, -24], 14, 730, {"joint": "wrist-right"}),
            # D-228: the tail cannon takes over from it as it turns round.
            part("stinger", [0, -34], 13, 730, {"retire": 1}),
        ],
        "joints": merge(scorpion_arm("left"), scorpion_arm("right")),
    }),
    # Where it stops and how it moves in place (MB-SCORPION-06).
    "stopFraction": 0.74,
    "sway": {"amplitude": 60, "period": 7.5},
    "bob": {"amplitude": 8, "period": 3.2},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-SCORPION-03, MB-SCORPION-08): a three-barrelled turret between
    # each claw's pincers (going with its wrist), the stinger's laser at the bulb's tip, and the
    # core's turret (its aimed shots) and rotor (its rings) on the head plate, either side of the
    # tail arched over it.
    "mounts": [
        gun_mount("claw-left", "claw-left", [-41, -30], 4, SCORPION_CLAW),
        gun_mount("claw-right", "claw-right", [41, -30], 4, SCORPION_CLAW),
        laser_mount("stinger", "stinger", [0, -42], 9.6, {"size": 3, "bore": 1.2, "length": 6}),
        gun_mount(
            "head",
            "core",
            [-9, -11],
            7,
            {"size": 4.5, "barrels": 1, "bore": 1.4, "length": 7},
        ),
        gun_mount(
            "head-rotor",
            "core",
            [11, -5],
            6.2,
            {"size": 4, "barrels": 8, "layout": "ring", "bore": 0.9, "length": 3.5},
        ),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-SCORPION-09). BOSS-58: its rings
    # are of 8, one bullet per barrel of its rotor, each stage's spinning or timed its own way.
    "stages": stages(
        [
            volley.aimed("claw-left", 2.2, 3, 10, BLUE, 1),
            volley.aimed("claw-right", 2.2, 3, 10, BLUE, 2.1),
            volley.laser("stinger", 5.5, 1.4, 2.5),
        ],
        [
            [volley.aimed("core", 3, 1, 0, PURPLE, 1.5)],
            [volley.ring("core", 2.4, 8, 0, PURPLE, 0.8)],
            [volley.ring("core", 2, 8, 10, PURPLE, 0.6)],
            [
                volley.ring("core", 1.4, 8, 8, PURPLE, 0.4),
                volley.aimed("core", 2.4, 1, 0, BLUE, 1),
            ],
        ],
    ),
})

# 1-5: a twin-hull police interceptor; two hull guns and a drone bay at its nose shield the core
# (MB-SENTINEL-07).
_SENTINEL = record({
    "id": "sentinel",
    # Its points and its parts' drops (MB-SENTINEL-11).
    "stats": stats({
        "id": "sentinel",
        "name": "Sentinel",
        "size": 3.5,
        "coreRadius": 18,
        "coreHealth": 1570,
        "points": 5000,
        "groundSpeed": 0.6,
        "parts": [
            part("gun-left", [-40, -8], 13, 780),
            part("gun-right", [40, -8], 13, 780),
            part("drone-bay", [0, -36], 15, 780),
        ],
    }),
    # Where it stops and how it moves in place (MB-SENTINEL-06).
    "stopFraction": 0.74,
    "sway": {"amplitude": 70, "period": 6.5},
    "bob": {"amplitude": 8, "period": 3},
    "launches": [{"from": "drone-bay", "kind": "hornets", "count": 2, "every": 5.5, "first": 3}],
    "guns": {},
    # Its gun mounts (BOSS-58, MB-SENTINEL-03): a hull gun's twin-barrelled turret on each body's
    # outer flank, and the core's two guns on the bodies' noses, clear of the thorax's plating and
    # the racks under it: the fan turret (its fans) on the blue body, the rotor (its ring) on the
    # red one. The drone bay launches its Hornets and has no gun.
    "mounts": [
        gun_mount("gun-left", "gun-left", [-40, -8], 4, SENTINEL_GUN),
        gun_mount("gun-right", "gun-right", [40, -8], 4, SENTINEL_GUN),
        gun_mount(
            "fan",
            "core",
            [-30, -42],
            5.1,
            {"size": 5, "barrels": 7, "gap": 0.8, "bore": 0.9, "length": 8},
        ),
        gun_mount(
            "rotor",
            "core",
            [30, -42],
            5.1,
            {"size": 5.5, "barrels": 14, "layout": "ring", "bore": 0.8, "length": 3},
        ),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-SENTINEL-08). BOSS-58: its fans are
    # 12° apart, the spacing of its fan turret's barrels.
    "stages": stages(
        [
            volley.aimed("gun-left", 1.7, 2, 8, BLUE, 0.8),
            volley.aimed("gun-right", 1.7, 2, 8, RED, 1.65),
        ],
        [
            [volley.fan("core", 2.8, 3, 12, BLUE, 1.4)],
            [volley.fan("core", 2.4, 5, 12, RED, 0.8)],
            [volley.fan("core", 2.2, 7, 12, BLUE, 0.6)],
            [
                volley.ring("core", 1.3, 14, 7, RED, 0.4),
                volley.fan("core", 2.6, 5, 12, BLUE, 1),
            ],
        ],
    ),
})

# Its hidden weapons (boss transformations, D-224, MB-REEF-WARDEN-10): at transformation 1 its back
# plating bursts off, baring a dark metal frame (MB-REEF-WARDEN-05), and a pair of gatling turrets
# unfold.
REEF_WARDEN = with_weapons(
    _REEF_WARDEN,
    [
        hidden_weapon("gatling-left", "gatling", [-13, -25], 11, 500, 1, "red", 1.2, 8.0),
        hidden_weapon("gatling-right", "gatling", [13, -25], 11, 500, 1, "red", 2.0, 8.0),
    ],
    [
        # MB-REEF-WARDEN-05 (D-254): the plating is a horseshoe round its shelled back, from just
        # behind the snout (at -Y) to its middle; the gatlings lie under its arms.
        armour_region(
            "back",
            1,
            [
                [21, -2],
                [23, -8],
                [22, -16],
                [17, -24],
                [9, -30],
                [0, -33],
                [-9, -30],
                [-17, -24],
                [-22, -16],
                [-23, -8],
                [-21, -2],
                [-15, -2],
                [-15, -10],
                [-11, -18],
                [-7, -24],
                [0, -27],
                [7, -24],
                [11, -18],
                [15, -10],
                [15, -2],
            ],
            "shell",
            None,
            False,
        ),
    ],
)

# Its hidden weapons (boss transformations, D-224, MB-BREAKWATER-10): at transformation 1 its back
# plating bursts off, baring a dark metal frame (MB-BREAKWATER-05), and a pair of missile racks
# unfold.
BREAKWATER = with_weapons(
    _BREAKWATER,
    [
        hidden_weapon("rack-left", "rack", [-11, 33], 9, 650, 1, "orange", 1.2, 17.7),
        hidden_weapon("rack-right", "rack", [11, 33], 9, 650, 1, "orange", 2.0, 17.7),
    ],
    [
        # MB-BREAKWATER-05 (D-254): the plating is its rear shell, a lozenge the shell's own shape
        # from its middle to its tail (at +Y); the racks lie under it.
        armour_region(
            "back",
            1,
            [
                [0, 14],
                [12, 15],
                [20, 18],
                [23, 22],
                [23, 29],
                [22, 34],
                [14, 38],
                [0, 41],
                [-14, 38],
                [-22, 34],
                [-23, 29],
                [-23, 22],
                [-20, 18],
                [-12, 15],
            ],
            "shell",
            None,
            False,
        ),
        # The hatch over its shell rotor (BOSS-58): it bursts as the rotor comes into use, in its
        # last stage, and the rotor rises out of it.
        armour_region(
            "rotor-hatch",
            None,
            [[7 * math.cos(k * math.pi / 4), -2 + 7 * math.sin(k * math.pi / 4)] for k in range(8)],
            "ring",
            None,
            False,
            "shell-rotor",
        ),
    ],
)

# Its hidden weapons (boss transformations, D-224, MB-DUST-DEVIL-10): at transformation 1 its back
# plating bursts off, baring a dark metal frame (MB-DUST-DEVIL-05), and a pair of ring emitters
# unfold.
DUST_DEVIL = with_weapons(
    _DUST_DEVIL,
    [
        hidden_weapon("orb-left", "orb", [-12, 5], 8, 500, 1, "green", 1.2, 10.2),
        hidden_weapon("orb-right", "orb", [12, 5], 8, 500, 1, "green", 2.0, 10.2),
    ],
    [
        # MB-DUST-DEVIL-05 (D-254): the plating is the bell's domed cap, round the hub carrying its
        # emitter: two half-rings (the right one and its mirror image) from 4.8 to 15.2 px out; the
        # orbs lie under them.
        armour_region(
            "back",
            1,
            [
                [0, -15.2],
                [5.8, -14],
                [10.7, -10.7],
                [14, -5.8],
                [15.2, 0],
                [14, 5.8],
                [10.7, 10.7],
                [5.8, 14],
                [0, 15.2],
                [0, 4.8],
                [3.4, 3.4],
                [4.8, 0],
                [3.4, -3.4],
                [0, -4.8],
            ],
            "shell",
            None,
        ),
    ],
)

# Where its tail cannon ends up, its tail unfolded straight out behind it (D-228).
SCORPION_TAIL_CANNON = [0, 108]

# Its transformation (D-224, D-228, MB-SCORPION-11): once both claws are gone it turns round, its
# back plating bursts off, and its tail unfolds straight out behind it (now towards the player) into
# a cannon firing a giant laser; the stinger it replaces leaves the fight.
SCORPION = with_weapons(
    merge(
        _SCORPION,
        {
            # D-228: it transforms once both its claws are gone, turning round as it does.
            "transformParts": [["claw-left", "claw-right"]],
            "turns": [math.pi],
        },
    ),
    [tail_cannon("tail-cannon", SCORPION_TAIL_CANNON, 15, 1100, 1, 1.5)],
    [
        # MB-SCORPION-11 (D-254): the plating is the abdomen's shell, a lozenge the shell's own
        # shape from under the head plate (at -Y) to the tail; the tail rig rises through it.
        armour_region(
            "back",
            1,
            [
                [12, 0],
                [14, 3],
                [16, 8],
                [16, 16],
                [14, 21],
                [10, 27],
                [0, 31.5],
                [-10, 27],
                [-14, 21],
                [-16, 16],
                [-16, 8],
                [-14, 3],
                [-12, 0],
            ],
            "shell",
            None,
            False,
        ),
    ],
)

# Its hidden weapons (boss transformations, D-224, MB-SENTINEL-10): at transformation 1 its back
# plating bursts off, baring a dark metal frame (MB-SENTINEL-05), and a pair of missile racks
# unfold.
SENTINEL = with_weapons(
    _SENTINEL,
    [
        hidden_weapon("rack-left", "rack", [-12, -7], 8, 620, 1, "blue", 1.2, 6.1),
        hidden_weapon("rack-right", "rack", [12, -7], 8, 620, 1, "blue", 2.0, 6.1),
    ],
    [
        # MB-SENTINEL-05: the plating over its thorax, a lozenge the thorax's own shape (its nose
        # at -Y); the racks lie under it.
        armour_region(
            "back",
            1,
            [
                [0, -24],
                [7, -20],
                [12.5, -12],
                [14, 0],
                [12.5, 12],
                [7, 22],
                [0, 28],
                [-7, 22],
                [-12.5, 12],
                [-14, 0],
                [-12.5, -12],
                [-7, -20],
            ],
            "shell",
            None,
            False,
        ),
    ],
)
