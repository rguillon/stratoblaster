# Copyright (c) 2026 Renaud Guillon
"""The Skyport Hub, the Lab's L-22 final boss (specs/bosses/lab/L-22-skyport-hub.md).

Lab boss: in the dev viewer only (no level brings it in). A gigantic flying airport seen from
above: an X of four runways radiating from a round central terminal on an octagonal apron, a
control tower behind the terminal, a pier at the front (the concourse), at the back (the radar's)
and either side (a fuel depot's), taxiway lights, a ducted lift fan under each runway's end.

Its guns at the start: a fixed battery at the end of each front runway, firing along the runway, and
the turret on the control tower. Its fuel depots and radar carry no gun: as its parts fall, new guns
rise out of hatches on its runways, its piers and its apron. Once both fuel depots are gone, its
rear runways swing forward round the terminal into their place (it changes shape, BOSS-45), a
sweeper riding each; once its radar is gone, its terminal's roof splits and its halves slide apart
on rails (BOSS-45), a rack riding each, and a hangar rises between them on the centre line.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

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


DEG = math.pi / 180

# FB-SKYPORT-HUB-01: the deck's top (runways, apron, piers) and its foot; the apron's octagon
# (its flat sides `APRON` out); the runways' half width, where they start and end (px out from
# the centre, along their diagonals) and their headings (degrees from config +X: front right,
# front left, rear right, rear left).
DECK = 6
DECK_LOW = 2
APRON = 30
RUNWAY_HALF = 8
RUNWAY_ROOT = 14
RUNWAY_END = 78
FRONT_DEG = -45
REAR_DEG = 45
# The lift fans past each runway's end (FB-SKYPORT-HUB-06): their centre out along it and radius.
FAN_OUT = 84
FAN_R = 9
# The piers: `[half width, from, to]` along the centre line (front, back) or across (the sides,
# their middle at `SIDE_Y`).
FRONT_PIER = [9, -APRON + 2, -54]
BACK_PIER = [10, APRON - 2, 62]
SIDE_PIER = [APRON - 2, 62]
SIDE_Y = -3
SIDE_HALF = 9
# The terminal (the core): an octagon `TERMINAL` out, its walls' top; its roof (two halves that
# slide apart, FB-SKYPORT-HUB-11) between `ROOF`.
TERMINAL = 16
TERMINAL_WALL = 12
ROOF = [12, 15.5]
ROOF_SLIDE = 13
# The control tower behind the terminal: its centre, its shaft's radius and top, its cab's radius
# and roof.
TOWER_AT = [0, 24]
TOWER_SHAFT = 4
CAB_FLOOR = 27
CAB_R = 6.5
CAB_TOP = 32
# The parts (FB-SKYPORT-HUB-03): the runway-end batteries (on the front runways), the fuel depots
# (on the side piers) and the radar (on the back pier).
GUN_OUT = 66
DEPOT_AT = [49, SIDE_Y]
RADAR_AT = [0, 52]


def on_runway(deg: float, out: float) -> list[float]:
    """Return the point `out` px from the centre along the runway heading `deg`."""
    return [out * math.cos(deg * DEG), out * math.sin(deg * DEG)]


def runway_outline(deg: float) -> list[list[float]]:
    """Return the outline of the runway heading `deg`: from its root to its end, a rounded tip."""
    c = math.cos(deg * DEG)
    s = math.sin(deg * DEG)
    # Its side: a quarter turn counter-clockwise.
    nx = -s
    ny = c

    def at(out: float, side: float) -> list[float]:
        return [out * c + side * nx, out * s + side * ny]

    w = RUNWAY_HALF
    return [
        at(RUNWAY_ROOT, -w),
        at(RUNWAY_END, -w),
        at(RUNWAY_END + 4, -w * 0.5),
        at(RUNWAY_END + 4, w * 0.5),
        at(RUNWAY_END, w),
        at(RUNWAY_ROOT, w),
    ]


GUN_AT = on_runway(FRONT_DEG, GUN_OUT)
# Where each front battery points: along its runway, out (its restDeg, from the nose, positive
# towards the screen's left): the right one 45° to the screen's right.
GUN_DEG = -45
BATTERY = {"size": 4.6, "barrels": 3, "gap": 2.6, "bore": 1.0, "length": 7, "turret": False}
BATTERY_TOP = DECK + 3.5
# The core's guns (FB-SKYPORT-HUB-07): the control tower's turret (from the start), the front
# runways' turrets (stage 1), the front pier's fixed laser (stage 2), the side piers' missile
# blocks (stage 3), the front runways' fixed casemates (stage 4) and the back pier's rotor (its
# last spiral, stage 5); each late one under a hatch.
TOWER_GUN = {"size": 4.4, "barrels": 3, "gap": 1.2, "bore": 1.0, "length": 7}
RUNWAY_GUN_AT = on_runway(FRONT_DEG, 34)
RUNWAY_GUN = {"size": 4.2, "barrels": 2, "gap": 1.3, "bore": 1.0, "length": 6.5}
LANCE_AT = [0, -46]
LANCE = {"size": 3.6, "bore": 1.9, "length": 9}
SILO_AT = [36, SIDE_Y]
CASEMATE_AT = on_runway(FRONT_DEG, 51)
CASEMATE = {"size": 4, "barrels": 3, "gap": 2.6, "bore": 0.9, "length": 6, "turret": False}
ROTOR_AT = [0, 38]
ROTOR = {"size": 4.6, "barrels": 16, "layout": "ring", "bore": 0.75, "length": 3.4}

RED = bullet("red", 185)
ORANGE = bullet("orange", 170)
MAGENTA = bullet("magenta", 180)
SPIRAL = bullet("orange", 160)


def mirror_x(at: list[Any]) -> list[Any]:
    """Return `at` mirrored across the centre line."""
    return [-at[0], at[1]]


def fpart(part_id: str, at: list[Any], radius: float, health: float) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    return part(part_id, at, radius, health, {"drop": 0.6})


def _core_gun(mount_id: str, shot: Any) -> Any:
    """Return the core's `shot` fired from its mount `mount_id`."""
    return merge(shot, {"mount": mount_id})


# The core's volleys, gun by gun (FB-SKYPORT-HUB-08).
RUNWAY_GUNS = [
    _core_gun("runway-gun-left", volley.aimed("core", 2.8, 2, 8, MAGENTA, 1.0)),
    _core_gun("runway-gun-right", volley.aimed("core", 2.8, 2, 8, MAGENTA, 2.4)),
]
LANCE_BEAM = _core_gun("lance", volley.laser("core", 7, 1.4, 1.6))
SILOS = [
    _core_gun("silo-left", volley.missiles("core", 6.5, 2, 30, 1.4)),
    _core_gun("silo-right", volley.missiles("core", 6.5, 2, 30, 4.6)),
]
CASEMATES = [
    _core_gun("casemate-left", volley.fan("core", 2.6, 3, 0, RED, 0.8, -GUN_DEG)),
    _core_gun("casemate-right", volley.fan("core", 2.6, 3, 0, RED, 2.1, GUN_DEG)),
]

_SKYPORT_HUB = record({
    "id": "skyport-hub",
    # Its points, its core's drop and its parts' drops (FB-SKYPORT-HUB-13).
    "stats": stats({
        "id": "skyport-hub",
        "name": "Skyport Hub",
        "size": 5.2,
        "coreRadius": 18,
        "coreHealth": 2200,
        "points": 9500,
        "groundSpeed": 0.8,
        "coreDrop": 1,
        "parts": [
            fpart("gun-left", mirror_x(GUN_AT), 9, 800),
            fpart("gun-right", GUN_AT, 9, 800),
            fpart("depot-left", mirror_x(DEPOT_AT), 11, 750),
            fpart("depot-right", DEPOT_AT, 11, 750),
            fpart("radar", RADAR_AT, 10, 900),
        ],
    }),
    # Where it stops and how it moves in place (FB-SKYPORT-HUB-06): a vast, slow drift.
    "stopFraction": 0.72,
    "sway": {"amplitude": 36, "period": 11},
    "bob": {"amplitude": 4, "period": 5},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-SKYPORT-HUB-07).
    "mounts": [
        gun_mount(
            "gun-left", "gun-left", mirror_x(GUN_AT), BATTERY_TOP, merge(BATTERY, {"restDeg": 45})
        ),
        gun_mount("gun-right", "gun-right", GUN_AT, BATTERY_TOP, merge(BATTERY, {"restDeg": -45})),
        gun_mount("tower-gun", "core", TOWER_AT, CAB_TOP, TOWER_GUN),
        gun_mount("runway-gun-left", "core", mirror_x(RUNWAY_GUN_AT), DECK, RUNWAY_GUN),
        gun_mount("runway-gun-right", "core", RUNWAY_GUN_AT, DECK, RUNWAY_GUN),
        laser_mount("lance", "core", LANCE_AT, DECK, LANCE),
        missile_mount("silo-left", "core", mirror_x(SILO_AT), DECK, 2),
        missile_mount("silo-right", "core", SILO_AT, DECK, 2),
        gun_mount(
            "casemate-left",
            "core",
            mirror_x(CASEMATE_AT),
            DECK,
            merge(CASEMATE, {"restDeg": -GUN_DEG}),
        ),
        gun_mount(
            "casemate-right", "core", CASEMATE_AT, DECK, merge(CASEMATE, {"restDeg": GUN_DEG})
        ),
        gun_mount("hub-rotor", "core", ROTOR_AT, DECK, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-SKYPORT-HUB-08): the runway-end
    # batteries fire rows of three along their runways; the depots and the radar nothing. The core's
    # tower turret fires a new aimed pattern at every stage, and a new gun joins it at each: the
    # runway turrets, the lance, the silos, the casemates, then the back pier's rotor's spiral.
    "stages": stages(
        [
            volley.fan("gun-left", 2.4, 3, 0, ORANGE, 1.0, -GUN_DEG),
            volley.fan("gun-right", 2.4, 3, 0, ORANGE, 2.2, GUN_DEG),
        ],
        [
            [_core_gun("tower-gun", volley.aimed("core", 2.2, 1, 0, MAGENTA, 1.4))],
            concat(
                [_core_gun("tower-gun", volley.burst("core", 2.6, 3, 0.14, MAGENTA, 0.8))],
                RUNWAY_GUNS,
            ),
            concat(
                [_core_gun("tower-gun", volley.aimed("core", 2.4, 3, 9, MAGENTA, 0.8)), LANCE_BEAM],
                RUNWAY_GUNS,
            ),
            concat(
                [_core_gun("tower-gun", volley.burst("core", 2.4, 4, 0.12, RED, 0.6)), LANCE_BEAM],
                concat(RUNWAY_GUNS, SILOS),
            ),
            concat(
                [_core_gun("tower-gun", volley.aimed("core", 2.2, 2, 6, RED, 0.6)), LANCE_BEAM],
                concat(RUNWAY_GUNS, concat(SILOS, CASEMATES)),
            ),
            concat(
                [
                    _core_gun("hub-rotor", volley.ring("core", 1.4, 16, 11.25, SPIRAL, 0.4)),
                    _core_gun("tower-gun", volley.burst("core", 2.2, 3, 0.12, RED, 1.0)),
                    LANCE_BEAM,
                ],
                concat(RUNWAY_GUNS, concat(SILOS, CASEMATES)),
            ),
        ],
    ),
})

# FB-SKYPORT-HUB-05: the rear runways swing forward round the terminal, about the vertical through
# their roots, `REAR_SWING` degrees (clockwise for the right one, seen from above), into the place
# the fuel depots held. Drawn at rest.
REAR_PIVOT = on_runway(REAR_DEG, RUNWAY_ROOT)
REAR_SWING = -27
REAR_MOTION = swing([REAR_PIVOT[0], REAR_PIVOT[1], DECK], "up", [0, REAR_SWING])
RUNWAY_HEIGHTS = [DECK_LOW, DECK]
# Where the sweepers ride the rear runways once swung (FB-SKYPORT-HUB-10), out from their pivot,
# and their pods' foot and top.
SWEEPER_OUT = 40
SWEEPER_POD = [DECK, DECK + 3]
# FB-SKYPORT-HUB-11: the terminal's roof halves (drawn closed) slide apart, `ROOF_SLIDE` each way;
# a rack rides each, the hangar rises on the centre line between them.
ROOF_MOTION = slide([[0, 0, 0], [ROOF_SLIDE, 0, 0]])
RACK_DRAWN = [6.5, 0]
RACK_POD = [ROOF[1], ROOF[1] + 2]
HANGAR_POD = [DECK, DECK + 4]


def sweeper_at() -> list[float]:
    """Return where the right sweeper ends up: on the swung rear runway, `SWEEPER_OUT` out."""
    a = (REAR_DEG + REAR_SWING) * DEG
    return [
        REAR_PIVOT[0] + SWEEPER_OUT * math.cos(a),
        REAR_PIVOT[1] + SWEEPER_OUT * math.sin(a),
    ]


def roof_outline() -> list[list[float]]:
    """Return the right roof half's outline (drawn closed): half the terminal's octagon."""
    t = TERMINAL
    c = t * math.tan(math.pi / 8)
    return [[0, -t], [c, -t], [t, -c], [t, c], [c, t], [0, t]]


def octagon(at: list[Any], radius: float) -> list[list[float]]:
    """Return an octagon `radius` round `at` (a hatch's outline)."""
    return [
        [
            at[0] + radius * math.cos(k * math.pi / 4 + math.pi / 8),
            at[1] + radius * math.sin(k * math.pi / 4 + math.pi / 8),
        ]
        for k in range(8)
    ]


def hatch(region_id: str, mount_id: str, at: list[Any], radius: float) -> Any:
    """Return the hatch over the core's mount `mount_id` (BOSS-58): an octagon round `at`."""
    return armour_region(region_id, None, octagon(at, radius), "ring", None, False, mount_id)


SWEEPER_AT = sweeper_at()

# Its transformations: once both fuel depots are gone its rear runways swing forward, a sweeper
# riding each; once its radar is gone its terminal's roof slides apart, a rack on each half and the
# hangar rising between them. Its late core guns rise out of hatches as they come into use.
SKYPORT_HUB = with_weapons(
    merge(
        _SKYPORT_HUB,
        {"transformParts": [["depot-left", "depot-right"], ["radar"]]},
    ),
    [
        hidden_weapon(
            "sweeper-left",
            "sweeper",
            mirror_x(SWEEPER_AT),
            8,
            720,
            1,
            "orange",
            1.2,
            SWEEPER_POD,
        ),
        hidden_weapon(
            "sweeper-right", "sweeper", SWEEPER_AT, 8, 720, 1, "orange", 4.0, SWEEPER_POD
        ),
        hidden_weapon(
            "rack-left",
            "rack",
            [-(RACK_DRAWN[0] + ROOF_SLIDE), RACK_DRAWN[1]],
            7,
            720,
            2,
            "orange",
            1.2,
            RACK_POD,
        ),
        hidden_weapon(
            "rack-right",
            "rack",
            [RACK_DRAWN[0] + ROOF_SLIDE, RACK_DRAWN[1]],
            7,
            720,
            2,
            "orange",
            2.6,
            RACK_POD,
        ),
        hidden_weapon("hangar", "hangar", [0, 0], 9, 720, 2, "orange", 1.6, HANGAR_POD),
    ],
    concat(
        moving_region(
            "rear-runway", 1, runway_outline(REAR_DEG), REAR_MOTION, None, RUNWAY_HEIGHTS
        ),
        concat(
            moving_region("roof", 2, roof_outline(), ROOF_MOTION, "shell", ROOF),
            [
                hatch("runway-hatch-left", "runway-gun-left", mirror_x(RUNWAY_GUN_AT), 5.5),
                hatch("runway-hatch-right", "runway-gun-right", RUNWAY_GUN_AT, 5.5),
                hatch("lance-hatch", "lance", LANCE_AT, 5.5),
                armour_region(
                    "silo-hatch-left",
                    None,
                    octagon(mirror_x(SILO_AT), 7),
                    "shell",
                    None,
                    False,
                    "silo-left",
                ),
                armour_region(
                    "silo-hatch-right",
                    None,
                    octagon(SILO_AT, 7),
                    "shell",
                    None,
                    False,
                    "silo-right",
                ),
                hatch("casemate-hatch-left", "casemate-left", mirror_x(CASEMATE_AT), 5.5),
                hatch("casemate-hatch-right", "casemate-right", CASEMATE_AT, 5.5),
                hatch("rotor-hatch", "hub-rotor", ROTOR_AT, 6),
            ],
        ),
    ),
)
