# Copyright (c) 2026 Renaud Guillon
"""The Floating Dam, the Lab's L-21 final boss (specs/bosses/lab/L-21-floating-dam.md).

Lab boss: in the dev viewer only (no level brings it in). A gigantic curved concrete arch dam flying
sideways across the screen, very wide and shallow: a road along its crest with a bascule bridge over
its spillway, a gatehouse at either end of the crest, sluice gates in its sloping face, a turbine
hall behind it, abutments at its ends with power pylons on them and the lines strung over it, lift
fans under its back. It comes in with three guns: the fixed guns behind its two outer sluice gates,
firing walls of bullets straight down the screen, and the control tower's turret. Each lost part
brings a new gun up out of a hatch. Once both outer sluices are gone its inner sluice gates lift up
its face and a battery rolls out of each; once both gatehouses are gone the bascule bridge over its
spillway raises its two leaves, the spillway's cover bursts, a cannon stands up on the weir either
side and a lance in the stilling basin below.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, bursting, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, slide, swing
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# FB-FLOATING-DAM-01: the wall's half length and its curve: its crest's centre line is at
# `CREST_Y - BOW (x / SPAN)²` (its ends come forward, its face concave towards the player); its
# section `[d, height]`, `d` px in front of that line (towards -Y), from its back foot round its
# back, its crest, its sloping face and its toe.
SPAN = 100
CREST_Y = 8
BOW = 18
CREST = 24
SECTION = [  # type: list[list[float]]
    [-6, -10],
    [-6, CREST],
    [5, CREST],
    [8, 20],
    [13, 12],
    [19, 2],
    [21, 0],
    [21, -6],
]
# The spillway notch in its middle (FB-FLOATING-DAM-12): its half width, its weir's crest (lower
# than the wall's), the stilling basin in front of its chute `[half width, front, top]`.
NOTCH = 14
WEIR_TOP = 14
BASIN = [14, -27, 2]
# The abutments at its ends `[inner x, outer x, front, back, top]` and the bastion on each one's
# front (its top), the pylons on them.
ABUTMENT = [SPAN - 2, SPAN + 14, -34, -1, 30]
BASTION_TOP = 16
# The outer sluices (FB-FLOATING-DAM-03): their centre, the outlet sill their gun stands on (its
# half width, front and back, top) and their gun.
SLUICE_AT = [66, -17]
SILL = [7.5, -25, -9, 9.8]
SLUICE_GUN_AT = [66, -21]
SLUICE_GUN = {
    "size": 5,
    "barrels": 4,
    "gap": 3.2,
    "bore": 1.1,
    "length": 6,
    "turret": False,
}
# The gatehouses on the crest's ends and the turbine hall behind its middle (FB-FLOATING-DAM-03):
# their centres and sizes `[half width, half depth, top]`.
GATEHOUSE_AT = [86, -3]
GATEHOUSE = [8, 6.5, 37]
HALL_AT = [0, 24]
HALL = [20, 8, 16]
# The control tower on the crest (its centre, half size, top) and its twin turret.
TOWER_AT = [26, 10.5]
TOWER = [4.5, 4, 32]
TOWER_GUN = {"size": 4.4, "barrels": 2, "gap": 1.3, "bore": 1.1, "length": 7}
# The late guns, each under its own hatch (FB-FLOATING-DAM-07): the abutments' casemates (fixed,
# raking in towards the middle), the mortar and the rotor on the crest's back, the road turret, the
# weirs' outlets on the face (fixed, straight down).
CASEMATE_AT = [107, -29]
CASEMATE_DEG = 22
CASEMATE = {
    "size": 4,
    "barrels": 3,
    "gap": 2.8,
    "bore": 0.9,
    "length": 6,
    "turret": False,
}
MORTAR_AT = [-26, 10]
MORTAR = {"size": 4.6, "barrels": 1, "bore": 2.2, "length": 6, "style": "mortar", "axis": 0.6}
ROAD_GUN_AT = [48, 7]
ROAD_GUN = {"size": 4.2, "barrels": 3, "gap": 1.1, "bore": 0.9, "length": 6}
ROTOR_AT = [-48, 7]
ROTOR = {"size": 4.4, "barrels": 16, "layout": "ring", "bore": 0.7, "length": 3.2}
OUTLET_AT = [24, -6]
OUTLET_TOP = 12.5
OUTLET = {
    "size": 3.8,
    "barrels": 3,
    "gap": 2.8,
    "bore": 0.9,
    "length": 5,
    "turret": False,
}
# The hatches' half sizes: square lids on the crest and the outlets, a plate on each bastion.
HATCH = 5.5
OUTLET_HATCH = [4.8, 4]
CASEMATE_HATCH = [5.5, 4.5]


def crest_y(x: float) -> float:
    """Return the Y of the crest's centre line at `x` (FB-FLOATING-DAM-01)."""
    k = x / SPAN
    return CREST_Y - BOW * k * k


def face_height(d: float) -> float:
    """Return the wall's height `d` px in front of its crest's centre line (on its face)."""
    for k in range(2, len(SECTION) - 1):
        a = SECTION[k - 1]
        b = SECTION[k]
        if a[0] <= d <= b[0]:
            return float(a[1] + (b[1] - a[1]) * (d - a[0]) / (b[0] - a[0]))
    return 0.0


WALL = bullet("orange", 150, 5)
RED = bullet("red", 180)
MAGENTA = bullet("magenta", 175)
SPIRAL = bullet("orange", 160)
FLAK = bursting("orange", 110, 8, [1.1, 8, bullet("red", 165)])


def fpart(part_id: str, at: list[Any], radius: float, health: float) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    return part(part_id, at, radius, health, {"drop": 0.6})


def _core(shot: Any, mount_id: str) -> Any:
    """Return `shot`, a core volley, fired from the core's mount `mount_id` (BOSS-58)."""
    return merge(shot, {"mount": mount_id})


def _pair(shot: Any, mount_id: str, later: float) -> list[Any]:
    """Return `shot` from the core's mounts `mount_id` -left and -right, the right `later`."""
    first = shot.first if shot.first != None else shot.every
    return [
        _core(shot, mount_id + "-left"),
        _core(merge(shot, {"first": first + later}), mount_id + "-right"),
    ]


def _casemates() -> list[Any]:
    """Return the abutments' crossfire: three bullets along their barrels, raking inwards."""
    return _pair(volley.fan("core", 2.6, 3, 0, RED, 0.6), "casemate", 1.3)


def _outlets() -> list[Any]:
    """Return the weir outlets' walls: three bullets side by side, straight down."""
    return _pair(volley.fan("core", 1.3, 3, 0, WALL, 0.4), "outlet", 0.65)


def _tower(shot: Any) -> Any:
    return _core(shot, "tower-gun")


_FLOATING_DAM = record({
    "id": "floating-dam",
    # Its points, its core's drop and its parts' drops (FB-FLOATING-DAM-13).
    "stats": stats({
        "id": "floating-dam",
        "name": "Floating Dam",
        "size": 6,
        "coreRadius": 18,
        "coreHealth": 1700,
        "points": 10000,
        "groundSpeed": 0.6,
        "coreDrop": 1,
        "parts": [
            fpart("sluice-left", [-SLUICE_AT[0], SLUICE_AT[1]], 11, 900),
            fpart("sluice-right", SLUICE_AT, 11, 900),
            fpart("gatehouse-left", [-GATEHOUSE_AT[0], GATEHOUSE_AT[1]], 10, 760),
            fpart("gatehouse-right", GATEHOUSE_AT, 10, 760),
            fpart("hall", HALL_AT, 13, 980),
        ],
    }),
    # Where it stops and how it moves in place (FB-FLOATING-DAM-06): a slow, heavy drift.
    "stopFraction": 0.74,
    "sway": {"amplitude": 30, "period": 12},
    "bob": {"amplitude": 3, "period": 5.2},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-FLOATING-DAM-07).
    "mounts": [
        gun_mount(
            "sluice-left",
            "sluice-left",
            [-SLUICE_GUN_AT[0], SLUICE_GUN_AT[1]],
            SILL[3],
            SLUICE_GUN,
        ),
        gun_mount("sluice-right", "sluice-right", SLUICE_GUN_AT, SILL[3], SLUICE_GUN),
        gun_mount("tower-gun", "core", TOWER_AT, TOWER[2], TOWER_GUN),
        gun_mount(
            "casemate-left",
            "core",
            [-CASEMATE_AT[0], CASEMATE_AT[1]],
            BASTION_TOP,
            merge(CASEMATE, {"restDeg": -CASEMATE_DEG}),
        ),
        gun_mount(
            "casemate-right",
            "core",
            CASEMATE_AT,
            BASTION_TOP,
            merge(CASEMATE, {"restDeg": CASEMATE_DEG}),
        ),
        gun_mount("mortar", "core", MORTAR_AT, CREST, MORTAR),
        gun_mount(
            "outlet-left",
            "core",
            [-OUTLET_AT[0], OUTLET_AT[1]],
            OUTLET_TOP,
            OUTLET,
        ),
        gun_mount("outlet-right", "core", OUTLET_AT, OUTLET_TOP, OUTLET),
        gun_mount("road-gun", "core", ROAD_GUN_AT, CREST, ROAD_GUN),
        gun_mount("rotor", "core", ROTOR_AT, CREST, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-FLOATING-DAM-08): the outer
    # sluices fire walls of four bullets side by side straight down; the gatehouses and the hall
    # carry no gun. The control tower's turret fires at every stage, a new aimed pattern each time,
    # and each stage brings a new gun out of its hatch: the abutments' crossfire, the mortar's flak,
    # the weir outlets' walls, the road turret's bursts, then the rotor's spiral of 16.
    "stages": stages(
        [
            volley.fan("sluice-left", 1.1, 4, 0, WALL, 0.5),
            volley.fan("sluice-right", 1.1, 4, 0, WALL, 1.05),
        ],
        [
            [_tower(volley.aimed("core", 2.4, 2, 7, MAGENTA, 1.2))],
            concat([_tower(volley.burst("core", 2.6, 3, 0.15, MAGENTA, 1.0))], _casemates()),
            concat(
                [
                    _tower(volley.aimed("core", 2.2, 2, 7, MAGENTA, 0.9)),
                    _core(volley.aimed("core", 3.4, 1, 0, FLAK, 1.6), "mortar"),
                ],
                _casemates(),
            ),
            concat(
                [
                    _tower(volley.aimed("core", 2.4, 3, 8, MAGENTA, 0.8)),
                    _core(volley.aimed("core", 3.4, 1, 0, FLAK, 1.6), "mortar"),
                ],
                _outlets(),
            ),
            concat(
                concat(
                    [
                        _tower(volley.aimed("core", 2.6, 2, 7, MAGENTA, 1.0)),
                        _core(volley.burst("core", 2.4, 4, 0.12, RED, 0.7), "road-gun"),
                    ],
                    _outlets(),
                ),
                _casemates(),
            ),
            concat(
                [
                    _core(volley.ring("core", 1.5, 16, 11.25, SPIRAL, 0.4), "rotor"),
                    _core(volley.burst("core", 2.4, 4, 0.12, RED, 0.9), "road-gun"),
                    _tower(volley.aimed("core", 2.4, 3, 8, MAGENTA, 1.4)),
                ],
                _outlets(),
            ),
        ],
    ),
})

# FB-FLOATING-DAM-10: the right inner sluice gate as drawn, its bay down the face and the outfall
# ledge in front of it (`[x0, x1, front, back]`): it lifts up the face, back and up, into its hoist
# on the crest; the left one is its mirror image. Its battery rolls out of the bay onto the ledge.
GATE = [33, 49, -32, 2]
GATE_LIFT = [0.0, 10.0, 12.0]
GATE_HEIGHTS = [0, CREST]
BATTERY_AT = [41, -24]
BATTERY_FROM = [41, -6]
BATTERY_POD = [1, 3.5]
# FB-FLOATING-DAM-11, FB-FLOATING-DAM-12: the bascule bridge's right leaf over the spillway, as
# drawn (down, the road across): its deck from the middle to the notch's side, across the crest;
# it lifts about its hinge on the notch's side (`LEAF_LIFT` degrees). The cannons stand on the
# weir under it, the lance in the stilling basin under the chute's cover.
LEAF = [  # type: list[list[float]]
    [0, CREST_Y - 5],
    [NOTCH - 0.5, CREST_Y - 5],
    [NOTCH - 0.5, CREST_Y + 6],
    [0, CREST_Y + 6],
]
LEAF_DECK = [CREST - 3, CREST]
LEAF_LIFT = 78
CANNON_AT = [7, 8]
CANNON_POD = [WEIR_TOP, WEIR_TOP + 3]
LANCE_AT = [0, -19]
LANCE_POD = [BASIN[2], BASIN[2] + 3]
COVER = [  # type: list[list[float]]
    [-NOTCH + 1.5, BASIN[1]],
    [NOTCH - 1.5, BASIN[1]],
    [NOTCH - 1.5, CREST_Y - 5.5],
    [-NOTCH + 1.5, CREST_Y - 5.5],
]


def _square(at: list[Any], half: list[Any]) -> list[list[float]]:
    """Return a hatch's outline: a rectangle `half` big either way round `at`."""
    return [
        [at[0] - half[0], at[1] - half[1]],
        [at[0] + half[0], at[1] - half[1]],
        [at[0] + half[0], at[1] + half[1]],
        [at[0] - half[0], at[1] + half[1]],
    ]


def _hatch(region_id: str, at: list[Any], half: list[Any], mount_id: str) -> Any:
    """Return the hatch over the core's mount `mount_id`: it bursts as that gun comes out."""
    return armour_region(region_id, None, _square(at, half), "shell", None, False, mount_id)


def _left(at: list[Any]) -> list[Any]:
    return [-at[0], at[1]]


def _battery(part_id: str, at: list[Any], src: list[Any], first: float) -> Any:
    return hidden_weapon(part_id, "battery", at, 8, 780, 1, "red", first, BATTERY_POD, None, src)


def _cannon(part_id: str, at: list[Any], first: float) -> Any:
    return hidden_weapon(part_id, "cannon", at, 6.5, 980, 2, "red", first, CANNON_POD)


# Its transformations: once both outer sluices are gone its inner sluice gates lift up its face and
# a battery rolls out of each; once both gatehouses are gone its bascule bridge raises its leaves
# (it changes shape, BOSS-45), the spillway's cover bursts, a cannon stands up either side of the
# weir and a lance in the stilling basin. Each late core gun bursts its hatch as it comes into use
# (BOSS-58).
FLOATING_DAM = with_weapons(
    merge(
        _FLOATING_DAM,
        {
            "transformParts": [
                ["sluice-left", "sluice-right"],
                ["gatehouse-left", "gatehouse-right"],
            ]
        },
    ),
    [
        _battery("battery-left", _left(BATTERY_AT), _left(BATTERY_FROM), 1.2),
        _battery("battery-right", BATTERY_AT, BATTERY_FROM, 2.0),
        _cannon("cannon-left", _left(CANNON_AT), 1.2),
        _cannon("cannon-right", CANNON_AT, 2.0),
        hidden_weapon("lance", "lance", LANCE_AT, 7, 980, 2, "red", 1.6, LANCE_POD),
    ],
    concat(
        concat(
            moving_region(
                "gate",
                1,
                [[GATE[0], GATE[2]], [GATE[1], GATE[2]], [GATE[1], GATE[3]], [GATE[0], GATE[3]]],
                slide([[0.0, 0.0, 0.0], GATE_LIFT]),
                None,
                GATE_HEIGHTS,
            ),
            moving_region(
                "leaf",
                2,
                LEAF,
                swing([NOTCH - 0.5, 0, CREST], "along", [0, LEAF_LIFT]),
                None,
                LEAF_DECK,
            ),
        ),
        [
            armour_region("cover", 2, COVER, "shell", [0, WEIR_TOP + 1], False),
            _hatch("casemate-hatch-left", _left(CASEMATE_AT), CASEMATE_HATCH, "casemate-left"),
            _hatch("casemate-hatch-right", CASEMATE_AT, CASEMATE_HATCH, "casemate-right"),
            _hatch("mortar-hatch", MORTAR_AT, [HATCH, HATCH], "mortar"),
            _hatch("outlet-hatch-left", _left(OUTLET_AT), OUTLET_HATCH, "outlet-left"),
            _hatch("outlet-hatch-right", OUTLET_AT, OUTLET_HATCH, "outlet-right"),
            _hatch("road-hatch", ROAD_GUN_AT, [HATCH, HATCH], "road-gun"),
            _hatch("rotor-hatch", ROTOR_AT, [HATCH, HATCH], "rotor"),
        ],
    ),
)

# For the model: the pylons' places (on the abutments) and their top.
PYLON_AT = [107, -12]
PYLON_TOP = 54
