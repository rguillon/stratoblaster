# Copyright (c) 2026 Renaud Guillon
"""The Clockwork Citadel, the Lab's L-24 final boss (specs/bosses/lab/L-24-clockwork-citadel.md).

Lab boss: in the dev viewer only, no level brings it in. A gigantic flying clock-tower fortress: a
square stone citadel on a stepped plinth, a bell tower at each corner, a huge clock face on its
roof whose minute hand sweeps round (it orbits, BOSS-34), exposed gear trains on its flanks, a
great pendulum swinging out of its back wall and a gatehouse at its front. It starts with three
guns: the front bell towers' turrets and the gatehouse's fixed noon gun; its gear trains, pendulum
and minute hand carry none, but each lost part brings a new core gun out (angled casemates, the
back towers' turrets under their roofs, broadside casemates, the cuckoo gun, a rotor).

Once both gear trains are gone its great wheels unmesh (they slide out of the flanks, BOSS-45), an
orb riding each; once the pendulum and the hand are gone the clock face splits down the middle and
its halves slide apart, a mortar riding each, and a lance rises out of the movement on the centre
line.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, slide
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# FB-CLOCKWORK-CITADEL-01: the plinth's half width and top, the citadel block's half width and its
# roof, the parapet round the roof (its width and top).
PLINTH = [53, 6]
BLOCK = 48
ROOF = 16
PARAPET = [3, 19]
# The clock face on the roof (FB-CLOCKWORK-CITADEL-02): its radius and its plate's top; the
# movement under it (its floor, seen once the face splits), the centre boss the hands turn on (its
# radius and top) and the arbor over it (radius and top: the hour hand's pivot).
FACE_RADIUS = 34
FACE_TOP = 17.6
MOVEMENT = 12.5
CENTRE = [9, 19.4]
ARBOR = [2.6, 23]
# The minute hand (FB-CLOCKWORK-CITADEL-03): its part's centre at rest (pointing at six o'clock),
# its length from the centre, and how fast it sweeps round (the boss's spin, radians a second:
# clockwise as the player sees it). No gun: a fixed gun on a turning ring would not turn its shots
# with it (the engine turns an orbiting part's muzzles, not their headings).
HAND_AT = [0, -17]
HAND_LENGTH = 31
SPIN = -0.3

# The corner bell towers (FB-CLOCKWORK-CITADEL-04): the right front one's centre (the others are
# mirrored), their drums' radius and top. The front pair's belfries are parts, each a twin turret
# on its drum; the back pair's turrets wait under their roofs (hatches, BOSS-58).
TOWER_AT = [48, -48]
TOWER_RADIUS = 11
TOWER_TOP = 28
TOWER_GUN = {"size": 4.4, "barrels": 2, "gap": 1.4, "bore": 1.1, "length": 7}
ROOF_RADIUS = 9.5
# The gatehouse at the front (FB-CLOCKWORK-CITADEL-05): `[half width, front, top]` (its back in the
# block); its fixed noon gun on it, three barrels straight down, out from the start.
GATE = [13, -61, 13]
NOON_AT = [0, -55]
NOON_GUN = {
    "size": 3.8,
    "barrels": 3,
    "gap": 2.6,
    "bore": 1.0,
    "length": 7,
    "turret": False,
    "restDeg": 0,
}
# The cuckoo house over the gate, on the roof's front edge: its centre, its house's half width,
# depth and top (a hatch); the cuckoo gun's turret inside, under it.
CUCKOO_AT = [0, -42]
CUCKOO_HOUSE = [6, 5, 26]
CUCKOO_GUN = {"size": 3.8, "barrels": 3, "gap": 1.1, "bore": 0.9, "length": 6.5}
# The front casemates (angled out and down, fixed) and the broadside casemates (fixed, out of the
# flanks): the right ones' places and headings; their guns rise out of open sponsons.
CASEMATE_AT = [28, -51]
CASEMATE_DEG = -35
BROADSIDE_AT = [51, -2]
BROADSIDE_DEG = -90
CASEMATE_TOP = 10
CASEMATE_GUN = {"size": 3, "barrels": 2, "gap": 2.4, "bore": 0.9, "length": 6, "turret": False}
BROADSIDE_GUN = {"size": 3.2, "barrels": 3, "gap": 2.4, "bore": 0.9, "length": 6, "turret": False}
# The rotor under its hatch on the roof's back (its last spiral).
ROTOR_AT = [0, 41]
ROTOR_HATCH = 5.6
CORE_ROTOR = {"size": 4.4, "barrels": 16, "layout": "ring", "bore": 0.7, "length": 3.2}

# The gear trains on the flanks (FB-CLOCKWORK-CITADEL-06): the left one's centre (on its shelf);
# no gun. The great wheels behind them: the right one's centre and radius as drawn (meshed into
# the flank), its rail's height, and how far it slides out as it unmeshes.
GEARS_AT = [-60, -22]
SHELF_TOP = 8
WHEEL_AT = [56, 18]
WHEEL_RADIUS = 12
WHEEL_SLIDE = 14
WHEEL_HEIGHTS = [SHELF_TOP, SHELF_TOP + 2]
# The pendulum out of the back wall (FB-CLOCKWORK-CITADEL-07): its pivot, its bob (the part) and
# how it swings (degrees either way, seconds a swing to and fro).
PENDULUM_PIVOT = [0, 51]
BOB_AT = [0, 76]
BOB_RADIUS = 11
PENDULUM_SWING = [16, 3.2]

# Its bullets: the bells' magenta shots, the core's red ones and the spiral.
BELL_SHOT = bullet("magenta", 170)
RED = bullet("red", 180)
SPIRAL = bullet("orange", 160)


def mirrored(at: list[Any]) -> list[Any]:
    """Return `at` mirrored across the centre line."""
    return [-at[0], at[1]]


def fpart(part_id: str, at: list[Any], radius: float, health: float, options: Any = None) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    return part(part_id, at, radius, health, merge({"drop": 0.6}, options or {}))


def _fixed(options: Any, deg: float) -> Any:
    return merge(options, {"restDeg": deg})


def _on(shot: Any, mount_id: str) -> Any:
    return merge(shot, {"mount": mount_id})


def _pair(stem: str, every: float, count: int, first: float) -> list[Any]:
    """Return the volleys of the fixed pair `stem`-right and -left: all barrels at once each."""
    return [
        _on(volley.fan("core", every, count, 0, RED, first), stem + "-right"),
        _on(volley.fan("core", every, count, 0, RED, first + every / 2), stem + "-left"),
    ]


def _noon(every: float, first: float) -> Any:
    return _on(volley.fan("core", every, 3, 0, RED, first), "noon-gun")


def _tower(side: str, shape: str, every: float, first: float) -> Any:
    mount = "tower-back-" + side
    if shape == "burst":
        return _on(volley.burst("core", every, 3, 0.14, RED, first), mount)
    return _on(volley.aimed("core", every, 2, 8, RED, first), mount)


_CLOCKWORK_CITADEL = record({
    "id": "clockwork-citadel",
    # Its points, its core's drop and its parts' drops (FB-CLOCKWORK-CITADEL-13). The gear trains
    # first, then the pendulum and the hand: the parts each transformation calls for, in the order
    # the debug key breaks them (`transformParts`).
    "stats": stats({
        "id": "clockwork-citadel",
        "name": "Clockwork Citadel",
        "size": 5,
        "coreRadius": 22,
        "coreHealth": 4300,
        "points": 12000,
        "groundSpeed": 0.6,
        "coreDrop": 1,
        # The pendulum swings out of the back wall (BOSS-33).
        "joints": {
            "pendulum": {
                "x": PENDULUM_PIVOT[0],
                "y": PENDULUM_PIVOT[1],
                "swing": {"amplitudeDeg": PENDULUM_SWING[0], "period": PENDULUM_SWING[1]},
            },
        },
        "parts": [
            fpart("gear-left", GEARS_AT, 12, 1300),
            fpart("gear-right", mirrored(GEARS_AT), 12, 1300),
            fpart("pendulum", BOB_AT, BOB_RADIUS, 1500, {"joint": "pendulum"}),
            fpart("hand", HAND_AT, 9, 1200, {"orbits": True}),
            fpart("bell-left", mirrored(TOWER_AT), TOWER_RADIUS, 1400),
            fpart("bell-right", TOWER_AT, TOWER_RADIUS, 1400),
        ],
    }),
    # Where it stops and how it moves in place (FB-CLOCKWORK-CITADEL-08): a slow, heavy drift.
    "stopFraction": 0.7,
    "sway": {"amplitude": 34, "period": 11},
    "bob": {"amplitude": 4, "period": 5},
    "spinRate": SPIN,
    "guns": {},
    # Its gun mounts (BOSS-58, FB-CLOCKWORK-CITADEL-04, FB-CLOCKWORK-CITADEL-05).
    "mounts": [
        gun_mount("bell-left", "bell-left", mirrored(TOWER_AT), TOWER_TOP, TOWER_GUN),
        gun_mount("bell-right", "bell-right", TOWER_AT, TOWER_TOP, TOWER_GUN),
        gun_mount("noon-gun", "core", NOON_AT, GATE[2], NOON_GUN),
        gun_mount(
            "casemate-right", "core", CASEMATE_AT, CASEMATE_TOP, _fixed(CASEMATE_GUN, CASEMATE_DEG)
        ),
        gun_mount(
            "casemate-left",
            "core",
            mirrored(CASEMATE_AT),
            CASEMATE_TOP,
            _fixed(CASEMATE_GUN, -CASEMATE_DEG),
        ),
        gun_mount("tower-back-left", "core", [-TOWER_AT[0], -TOWER_AT[1]], TOWER_TOP, TOWER_GUN),
        gun_mount("tower-back-right", "core", [TOWER_AT[0], -TOWER_AT[1]], TOWER_TOP, TOWER_GUN),
        gun_mount(
            "broadside-right",
            "core",
            BROADSIDE_AT,
            CASEMATE_TOP,
            _fixed(BROADSIDE_GUN, BROADSIDE_DEG),
        ),
        gun_mount(
            "broadside-left",
            "core",
            mirrored(BROADSIDE_AT),
            CASEMATE_TOP,
            _fixed(BROADSIDE_GUN, -BROADSIDE_DEG),
        ),
        gun_mount("cuckoo-gun", "core", CUCKOO_AT, ROOF, CUCKOO_GUN),
        gun_mount("core-rotor", "core", ROTOR_AT, ROOF, CORE_ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-CLOCKWORK-CITADEL-09): the front
    # belfries' turrets sweep aimed pairs in turn. The core's noon gun fires its three barrels
    # straight down from the start; each stage brings a new gun out: the front casemates angled out,
    # the back towers' turrets (a burst, then aimed pairs), the broadsides, the cuckoo gun's aimed
    # spreads, then the rotor's spiral of 16.
    "stages": stages(
        [
            volley.aimed("bell-left", 2.6, 2, 8, BELL_SHOT, 1.4),
            volley.aimed("bell-right", 2.6, 2, 8, BELL_SHOT, 2.7),
        ],
        [
            [_noon(2.2, 0.6)],
            concat([_noon(2.6, 1.0)], _pair("casemate", 2.2, 2, 0.5)),
            concat([_tower("left", "burst", 2.6, 0.6)], _pair("casemate", 2.6, 2, 1.0)),
            [
                _noon(2.6, 0.8),
                _tower("left", "aimed", 2.6, 1.2),
                _tower("right", "burst", 2.4, 0.5),
            ],
            concat(
                [_noon(3.0, 1.2), _tower("right", "aimed", 2.8, 0.8)],
                _pair("broadside", 2.0, 3, 0.4),
            ),
            concat(
                [
                    _on(volley.aimed("core", 2.4, 3, 9, RED, 0.5), "cuckoo-gun"),
                    _tower("left", "burst", 2.8, 1.0),
                ],
                _pair("broadside", 2.4, 3, 0.9),
            ),
            concat(
                [volley.ring("core", 1.3, 16, 11.25, SPIRAL, 0.4), _noon(2.6, 1.0)],
                _pair("broadside", 2.6, 3, 0.7),
            ),
        ],
    ),
})


def wheel_outline() -> list[list[float]]:
    """Return the right great wheel's outline as drawn (meshed into the flank): a 16-gon."""
    n = 16
    return [
        [
            WHEEL_AT[0] + WHEEL_RADIUS * math.cos(2 * math.pi * k / n),
            WHEEL_AT[1] + WHEEL_RADIUS * math.sin(2 * math.pi * k / n),
        ]
        for k in range(n)
    ]


def half_face() -> list[list[float]]:
    """Return the clock face's right half as drawn: a half disc right of the centre line."""
    n = 12
    return [
        [
            FACE_RADIUS * math.cos(-math.pi / 2 + math.pi * k / n),
            FACE_RADIUS * math.sin(-math.pi / 2 + math.pi * k / n),
        ]
        for k in range(n + 1)
    ]


def _octagon(at: list[Any], radius: float) -> list[list[float]]:
    return [
        [
            at[0] + radius * math.cos(k * math.pi / 4 + math.pi / 8),
            at[1] + radius * math.sin(k * math.pi / 4 + math.pi / 8),
        ]
        for k in range(8)
    ]


# FB-CLOCKWORK-CITADEL-10: each great wheel slides straight out of its flank (unmeshing), an orb
# riding its hub. FB-CLOCKWORK-CITADEL-11: each half of the clock face slides out across the roof,
# `FACE_SLIDE` px, a mortar riding it; the lance rises from the movement on the centre line.
WHEEL_MOTION = slide([[0, 0, 0], [WHEEL_SLIDE, 0, 0]])
ORB_AT = [WHEEL_AT[0] + WHEEL_SLIDE, WHEEL_AT[1]]
ORB_POD = [WHEEL_HEIGHTS[1], WHEEL_HEIGHTS[1] + 2.5]
FACE_SLIDE = 14
FACE_MOTION = slide([[0, 0, 0], [FACE_SLIDE, 0, 0]])
FACE_HEIGHTS = [ROOF, FACE_TOP]
MORTAR_AT = [32, 8]
MORTAR_POD = [FACE_TOP, FACE_TOP + 2.5]
LANCE_AT = [0, -18]
LANCE_POD = [MOVEMENT, MOVEMENT + 3]

# Its transformations: once both gear trains are gone its great wheels unmesh, an orb on each;
# once the pendulum and the hand are gone its clock face splits, a mortar on each half, and the
# lance rises between them. The cuckoo house, the back towers' roofs and the rotor's hatch burst as
# their guns come into use (BOSS-58).
CLOCKWORK_CITADEL = with_weapons(
    merge(
        _CLOCKWORK_CITADEL,
        {"transformParts": [["gear-left", "gear-right"], ["pendulum", "hand"]]},
    ),
    [
        hidden_weapon("orb-left", "orb", mirrored(ORB_AT), 9, 1200, 1, "orange", 1.2, ORB_POD),
        hidden_weapon("orb-right", "orb", ORB_AT, 9, 1200, 1, "orange", 2.0, ORB_POD),
        hidden_weapon(
            "mortar-left", "mortar", mirrored(MORTAR_AT), 8, 1500, 2, "red", 1.2, MORTAR_POD
        ),
        hidden_weapon("mortar-right", "mortar", MORTAR_AT, 8, 1500, 2, "red", 2.0, MORTAR_POD),
        hidden_weapon("lance", "lance", LANCE_AT, 7, 1500, 2, "red", 1.6, LANCE_POD),
    ],
    concat(
        concat(
            moving_region("wheel", 1, wheel_outline(), WHEEL_MOTION, None, WHEEL_HEIGHTS),
            moving_region("face", 2, half_face(), FACE_MOTION, None, FACE_HEIGHTS),
        ),
        [
            armour_region(
                "cuckoo-house",
                None,
                [
                    [CUCKOO_AT[0] - CUCKOO_HOUSE[0], CUCKOO_AT[1] - CUCKOO_HOUSE[1]],
                    [CUCKOO_AT[0] + CUCKOO_HOUSE[0], CUCKOO_AT[1] - CUCKOO_HOUSE[1]],
                    [CUCKOO_AT[0] + CUCKOO_HOUSE[0], CUCKOO_AT[1] + CUCKOO_HOUSE[1]],
                    [CUCKOO_AT[0] - CUCKOO_HOUSE[0], CUCKOO_AT[1] + CUCKOO_HOUSE[1]],
                ],
                "shell",
                None,
                False,
                "cuckoo-gun",
            ),
            armour_region(
                "roof-left",
                None,
                _octagon([-TOWER_AT[0], -TOWER_AT[1]], ROOF_RADIUS),
                "ring",
                None,
                False,
                "tower-back-left",
            ),
            armour_region(
                "roof-right",
                None,
                _octagon([TOWER_AT[0], -TOWER_AT[1]], ROOF_RADIUS),
                "ring",
                None,
                False,
                "tower-back-right",
            ),
            armour_region(
                "rotor-hatch",
                None,
                _octagon(ROTOR_AT, ROTOR_HATCH),
                "ring",
                None,
                False,
                "core-rotor",
            ),
        ],
    ),
)
