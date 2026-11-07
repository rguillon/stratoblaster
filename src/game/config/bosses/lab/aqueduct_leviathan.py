# Copyright (c) 2026 Renaud Guillon
"""The Aqueduct Leviathan, the Lab's L-23 final boss (L-23-aqueduct-leviathan.md).

Lab boss: in the dev viewer only, no level brings it in. A gigantic flying viaduct seen from
above, spanning across the screen: five stone piers with pointed cutwaters, iron arch ribs between
them, a channel of glowing water carried along its whole length, a gate tower at each end and a
keep over its middle pier, two lift engines slung in front of its outer piers. It comes in with
three guns: a fixed triple gun hung under each of two arches and the keep's turret. Every part it
loses brings out more guns from under hatches (under further arches, on the piers' cutwaters, on
the keep's face). Once two parts are gone the sluice houses over its inner piers slide back along
the channel and a lance rises out of each lock (BOSS-45 slides); once four are gone the channel
breaks at the keep, its two middle sections swing forward like gates (BOSS-45 swings), a gatling
on each bared arch, and the keep's front cutwater bursts off on an orb.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

from game.config.bosses.boss_guns import gun_mount, laser_mount, missile_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, slide, swing
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# FB-AQUEDUCT-LEVIATHAN-01: the piers' X (the middle one under the keep), their half width, their
# body's half depth, their cutwaters (square to `CUT_SQUARE`, pointed to `CUT_TIP`) and their top.
PIERS = [-72, -36, 0, 36, 72]
PIER_HALF = 6
PIER_DEPTH = 20
CUT_SQUARE = 24
CUT_TIP = 31
PIER_TOP = 16.5
# The abutments at its ends (their gate towers are parts): `[inner x, outer x]`, half depth, top.
ABUTMENT = [94, 114]
ABUTMENT_HALF = 13
TOWER_TOP = 38
# The arch ribs: their faces' Y `[outer, inner]` (front; the back ones mirrored), the height they
# spring from and their crown's.
RIB = [-14, -10]
SPRING = 4
CROWN = 15.5
# The water channel along its top: its half width, its floor, its walls' top and the water's
# surface, from one abutment to the other.
CHANNEL_HALF = 6
CHANNEL_FLOOR = 17
CHANNEL_TOP = 23
WATER = 21.5
# The keep over the middle pier: its half width, half depth and top.
KEEP_HALF = 9
KEEP_DEPTH = 11
KEEP_TOP = 44

RED = bullet("red", 185)
ORANGE = bullet("orange", 175)
SHELL = bullet("orange", 160, 5)

# Its guns (BOSS-58, FB-AQUEDUCT-LEVIATHAN-03): a fixed triple gun hung under each middle arch (its
# parts), and the core's: the keep's twin turret; fixed triple guns under the outer arches; twin
# turrets on the outer piers' back cutwaters; a fixed laser on the keep's face; missile blocks on
# the inner piers' back cutwaters; fixed twin guns on their front cutwaters; the rotor on the
# middle pier's back cutwater (its last spiral). Every one but the keep's turret under a hatch.
ARCH_GUN_AT = [54, -20]
OUTER_GUN_AT = [86, -20]
ARCH_GUN_H = 9
ARCH_GUN = {
    "size": 4,
    "barrels": 3,
    "gap": 1.0,
    "bore": 1.0,
    "length": 8,
    "turret": False,
    "restDeg": 0,
}
KEEP_GUN = {"size": 5.2, "barrels": 2, "gap": 1.4, "bore": 1.1, "length": 8}
PIER_TURRET_AT = [72, 26]
PIER_TURRET = {"size": 4.4, "barrels": 2, "gap": 1.2, "bore": 1.0, "length": 7}
KEEP_LASER_AT = [0, -13]
KEEP_LASER_H = 26
KEEP_LASER = {"size": 3.4, "bore": 1.6, "length": 7}
MISSILE_AT = [36, 26]
CUT_GUN_AT = [36, -26]
CUT_GUN = {
    "size": 3.4,
    "barrels": 2,
    "gap": 1.0,
    "bore": 0.9,
    "length": 6.5,
    "turret": False,
    "restDeg": 0,
}
ROTOR_AT = [0, 26]
ROTOR = {"size": 4.6, "barrels": 14, "layout": "ring", "bore": 0.75, "length": 3.2}


def fpart(part_id: str, at: list[Any], radius: float, health: float) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    return part(part_id, at, radius, health, {"drop": 0.6})


def _named(shot: Any, mount_id: str) -> Any:
    """`shot` fired from the core's mount `mount_id` (BOSS-58)."""
    return merge(shot, {"mount": mount_id})


def _pair(make: Any, base: str, firsts: list[Any]) -> list[Any]:
    """Return a volley `make(first)` from the left and the right mounts `base`-left/-right."""
    return [
        _named(make(firsts[0]), base + "-left"),
        _named(make(firsts[1]), base + "-right"),
    ]


# The core's guns that join in as it loses parts (the round's gun progression, FB-AQUEDUCT-
# LEVIATHAN-08); once out they keep firing.
OUTER = _pair(lambda f: volley.fan("core", 2.8, 3, 0, RED, f), "outer-gun", [1.0, 2.4])
PIER = _pair(lambda f: volley.aimed("core", 2.8, 1, 0, ORANGE, f), "pier-turret", [0.8, 2.0])
LASER = [_named(volley.laser("core", 7, 1.4, 2.0), "keep-laser")]
MISSILES = _pair(lambda f: volley.missiles("core", 6.5, 2, 20, f), "missile", [1.6, 4.8])
CUT = _pair(lambda f: volley.fan("core", 2.4, 2, 0, SHELL, f), "cut-gun", [0.6, 1.8])


def _keep(shot: Any) -> Any:
    return _named(shot, "keep-gun")


_AQUEDUCT_LEVIATHAN = record({
    "id": "aqueduct-leviathan",
    # Its points, its core's drop and its parts' drops (FB-AQUEDUCT-LEVIATHAN-13).
    "stats": stats({
        "id": "aqueduct-leviathan",
        "name": "Aqueduct Leviathan",
        "size": 6.4,
        "coreRadius": 14,
        "coreHealth": 2650,
        "points": 10000,
        "groundSpeed": 0.4,
        "coreDrop": 1,
        "parts": [
            fpart("arch-gun-left", [-ARCH_GUN_AT[0], -18], 9, 950),
            fpart("arch-gun-right", [ARCH_GUN_AT[0], -18], 9, 950),
            # The lift engines and the gate towers carry no gun.
            fpart("engine-left", [-PIERS[4], -40], 11, 1100),
            fpart("engine-right", [PIERS[4], -40], 11, 1100),
            fpart("tower-left", [-104, 0], 13, 1250),
            fpart("tower-right", [104, 0], 13, 1250),
        ],
    }),
    # Where it stops and how it moves in place (FB-AQUEDUCT-LEVIATHAN-06): very wide, it drifts
    # only a little.
    "stopFraction": 0.76,
    "sway": {"amplitude": 18, "period": 12},
    "bob": {"amplitude": 3, "period": 5.5},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-AQUEDUCT-LEVIATHAN-03).
    "mounts": [
        gun_mount(
            "arch-gun-left",
            "arch-gun-left",
            [-ARCH_GUN_AT[0], ARCH_GUN_AT[1]],
            ARCH_GUN_H,
            ARCH_GUN,
        ),
        gun_mount("arch-gun-right", "arch-gun-right", ARCH_GUN_AT, ARCH_GUN_H, ARCH_GUN),
        gun_mount("keep-gun", "core", [0, 0], KEEP_TOP, KEEP_GUN),
        gun_mount(
            "outer-gun-left", "core", [-OUTER_GUN_AT[0], OUTER_GUN_AT[1]], ARCH_GUN_H, ARCH_GUN
        ),
        gun_mount("outer-gun-right", "core", OUTER_GUN_AT, ARCH_GUN_H, ARCH_GUN),
        gun_mount(
            "pier-turret-left",
            "core",
            [-PIER_TURRET_AT[0], PIER_TURRET_AT[1]],
            PIER_TOP,
            PIER_TURRET,
        ),
        gun_mount("pier-turret-right", "core", PIER_TURRET_AT, PIER_TOP, PIER_TURRET),
        laser_mount("keep-laser", "core", KEEP_LASER_AT, KEEP_LASER_H, KEEP_LASER),
        missile_mount("missile-left", "core", [-MISSILE_AT[0], MISSILE_AT[1]], PIER_TOP, 2),
        missile_mount("missile-right", "core", MISSILE_AT, PIER_TOP, 2),
        gun_mount("cut-gun-left", "core", [-CUT_GUN_AT[0], CUT_GUN_AT[1]], PIER_TOP, CUT_GUN),
        gun_mount("cut-gun-right", "core", CUT_GUN_AT, PIER_TOP, CUT_GUN),
        gun_mount("rotor", "core", ROTOR_AT, PIER_TOP, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-AQUEDUCT-LEVIATHAN-08): the arch
    # guns' parallel triples straight down; the keep's turret fires something new each stage while
    # one more pair of guns (or the keep's laser) joins in, and last the rotor's spiral of 14.
    "stages": stages(
        [
            volley.fan("arch-gun-left", 2.6, 3, 0, RED, 1.0),
            volley.fan("arch-gun-right", 2.6, 3, 0, RED, 2.3),
        ],
        [
            [_keep(volley.aimed("core", 2.4, 1, 0, ORANGE, 1.4))],
            concat([_keep(volley.aimed("core", 2.6, 2, 6, ORANGE, 1.2))], OUTER),
            concat([_keep(volley.burst("core", 2.6, 3, 0.13, ORANGE, 1.0))], OUTER, PIER),
            concat([_keep(volley.aimed("core", 2.8, 3, 8, ORANGE, 1.2))], OUTER, PIER, LASER),
            concat(
                [_keep(volley.burst("core", 2.8, 4, 0.12, ORANGE, 0.8))],
                OUTER,
                PIER,
                LASER,
                MISSILES,
            ),
            concat(
                [_keep(volley.aimed("core", 2.4, 1, 0, ORANGE, 1.0))],
                OUTER,
                PIER,
                LASER,
                MISSILES,
                CUT,
            ),
            concat(
                [
                    _named(volley.ring("core", 1.6, 14, 12.9, ORANGE, 0.4), "rotor"),
                    _keep(volley.burst("core", 2.8, 3, 0.13, ORANGE, 1.2)),
                ],
                OUTER,
                PIER,
                LASER,
                MISSILES,
                CUT,
            ),
        ],
    ),
})

# Its first transformation (FB-AQUEDUCT-LEVIATHAN-10): the sluice house over each inner pier, as
# drawn (the right one; mirrored), slides back along the channel; a lance rises out of the lock it
# covered.
SLUICE = [29.5, 42.5, -10, 9]
SLUICE_TOP = 28
SLUICE_SLIDE = slide([[0, 0, 0], [0, 13, 0]])
LANCE_AT = [36, -4]
LANCE_POD = [CHANNEL_FLOOR, CHANNEL_FLOOR + 2]
# Its second (FB-AQUEDUCT-LEVIATHAN-11): the channel's middle sections (the right one; mirrored),
# from the keep's face to the inner pier, swing forward about their outer front corner like gates;
# a gatling on each bared arch; the keep's front cutwater bursts off on an orb.
LEAF = [KEEP_HALF + 0.5, 29.5, -CHANNEL_HALF, CHANNEL_HALF]
LEAF_SWING = swing([LEAF[1], LEAF[2], CHANNEL_FLOOR], "up", [0, 90])
GATLING_AT = [19.5, 0]
GATLING_POD = [CHANNEL_FLOOR + 0.6, CHANNEL_FLOOR + 2.4]
CUTWATER = [
    [-PIER_HALF, -18],
    [PIER_HALF, -18],
    [PIER_HALF, -CUT_SQUARE],
    [0, -CUT_TIP],
    [-PIER_HALF, -CUT_SQUARE],
]
CUTWATER_LOW = 8
ORB_AT = [0, -24]
ORB_POD = [CUTWATER_LOW + 0.6, CUTWATER_LOW + 3]


def _box(b: list[Any]) -> list[list[Any]]:
    """Return the outline of the box `[x0, x1, y0, y1]`."""
    return [[b[0], b[2]], [b[1], b[2]], [b[1], b[3]], [b[0], b[3]]]


def _hatch(region_id: str, at: list[Any], half: list[Any], mount_id: str) -> Any:
    """Return the hatch over the core's mount `mount_id` (BOSS-58): a box `half` round `at`."""
    b = [at[0] - half[0], at[0] + half[0], at[1] - half[1], at[1] + half[1]]
    return armour_region(region_id, None, _box(b), "shell", None, False, mount_id)


def _hatches(base: str, at: list[Any], half: list[Any]) -> list[Any]:
    """Return the hatches over the mounts `base`-left and `base`-right."""
    return [
        _hatch(base + "-hatch-left", [-at[0], at[1]], half, base + "-left"),
        _hatch(base + "-hatch-right", at, half, base + "-right"),
    ]


# The hatches' half sizes: the shrouds under the outer arches, the caps on the cutwaters, the
# keep's shutter.
SHROUD_HALF = [5.5, 3.5]
CAP_HALF = [5.5, 4.5]
SHUTTER_HALF = [4, 2.5]

AQUEDUCT_LEVIATHAN = with_weapons(
    _AQUEDUCT_LEVIATHAN,
    [
        hidden_weapon(
            "lance-left",
            "lance",
            [-LANCE_AT[0], LANCE_AT[1]],
            7,
            1000,
            1,
            "red",
            1.2,
            LANCE_POD,
        ),
        hidden_weapon("lance-right", "lance", LANCE_AT, 7, 1000, 1, "red", 2.4, LANCE_POD),
        hidden_weapon(
            "gatling-left",
            "gatling",
            [-GATLING_AT[0], GATLING_AT[1]],
            7,
            1250,
            2,
            "orange",
            1.2,
            GATLING_POD,
        ),
        hidden_weapon(
            "gatling-right", "gatling", GATLING_AT, 7, 1250, 2, "orange", 2.0, GATLING_POD
        ),
        hidden_weapon("orb", "orb", ORB_AT, 7, 1250, 2, "orange", 1.6, ORB_POD),
    ],
    concat(
        moving_region("sluice", 1, _box(SLUICE), SLUICE_SLIDE, "shell", [PIER_TOP, SLUICE_TOP]),
        moving_region(
            "leaf", 2, _box(LEAF), LEAF_SWING, "wing", [CHANNEL_FLOOR, CHANNEL_TOP + 0.5]
        ),
        [
            armour_region("cutwater", 2, CUTWATER, "shell", [CUTWATER_LOW, PIER_TOP], False),
            _hatch("keep-shutter", KEEP_LASER_AT, SHUTTER_HALF, "keep-laser"),
            _hatch("rotor-hatch", ROTOR_AT, CAP_HALF, "rotor"),
        ],
        _hatches("outer-gun", OUTER_GUN_AT, SHROUD_HALF),
        _hatches("pier-turret", PIER_TURRET_AT, CAP_HALF),
        _hatches("missile", MISSILE_AT, CAP_HALF),
        _hatches("cut-gun", CUT_GUN_AT, CAP_HALF),
    ),
)
