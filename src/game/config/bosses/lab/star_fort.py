# Copyright (c) 2026 Renaud Guillon
"""The Star Fort, the Lab's L-25 final boss (specs/bosses/lab/L-25-star-fort.md).

Lab boss: in the dev viewer only, no level brings it in. The climax: a gigantic flying star fort
seen from above, a five-pointed Vauban fortress on a slab of floating rock, ringed by a moat of
glowing energy: angled bastions round a central keep and its parade ground, a ravelin in front of
each forward curtain, a gatehouse in the rear one. It comes in with three guns (the cavalier's
turret in its nose bastion and a fixed gun on each ravelin's face); every part it loses opens more
embrasures along its bastions' faces, fixed guns firing along the faces' normals, so it bristles
more and more. Once the moat's two pylons are down its rear bastions swing out on their pivots like
wings (BOSS-45), a sweeper laser riding each; once both ravelins are down its keep rises on its
rock (a moving piece sliding up, BOSS-45), a gatling on its roof, and the parade ground's flagstones
burst off on a battery each side. A fortress first, a laser cross-fire next, at last a keep raining
fire from high above.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount, laser_mount
from game.config.bosses.boss_kit import bullet, bursting, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import move_point, moving_region, slide, swing
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


DEG = math.pi / 180


def polar(radius: float, angle_deg: float) -> list[float]:
    """Return the point `radius` px from the centre, `angle_deg` from the nose towards +X."""
    a = angle_deg * DEG
    return [radius * math.sin(a), -radius * math.cos(a)]


# FB-STAR-FORT-01: its five bastions' capitals (degrees from the nose, towards +X), their salients'
# radius, their shoulders' (where a face meets its flank) and their flank roots' (where a flank
# meets the curtain), each `[radius, degrees off the capital]`.
BASTIONS = [0, 72, 144, -144, -72]
SALIENT_R = 68
SHOULDER = [40, 20]  # type: list[float]
FLANK = [35, 24]  # type: list[float]
# A ravelin in front of each forward curtain (FB-STAR-FORT-03): its capital, its apex' radius and
# its base corners' `[radius, degrees off the capital]`.
RAVELIN_DEG = 36
RAVELIN_APEX = 53
RAVELIN_BASE = [39, 8]  # type: list[float]
# Heights: the rock's top, the ramparts' top, the parade ground inside them, the ravelins' top.
ROCK_TOP = 2
WALL_TOP = 10
PARADE = 5
RAVELIN_TOP = 9
# The moat of energy round it (FB-STAR-FORT-02): its inner and outer radius and its height.
MOAT = [70.5, 74]  # type: list[float]
MOAT_H = 3
# The keep (FB-STAR-FORT-11): its centre, its radius, its roof's height, and how far it rises.
KEEP_AT = [0, 6]
KEEP_R = 11
KEEP_TOP = 20
KEEP_RISE = 16


def bastion_outline(capital: float) -> list[list[float]]:
    """Return the outline of the bastion on `capital`: flank root, shoulder, salient, and back."""
    return [
        polar(FLANK[0], capital - FLANK[1]),
        polar(SHOULDER[0], capital - SHOULDER[1]),
        polar(SALIENT_R, capital),
        polar(SHOULDER[0], capital + SHOULDER[1]),
        polar(FLANK[0], capital + FLANK[1]),
    ]


def ravelin_outline(capital: float) -> list[list[float]]:
    """Return the outline of the ravelin on `capital`: a triangle pointing out."""
    return [
        polar(RAVELIN_BASE[0], capital - RAVELIN_BASE[1]),
        polar(RAVELIN_APEX, capital),
        polar(RAVELIN_BASE[0], capital + RAVELIN_BASE[1]),
    ]


def face_gun(a: list[float], b: list[float], share: float, inset: float) -> list[float]:
    """Return a gun on the face from `a` to `b` (outward on its left): `[x, y, degrees]`.

    `share` of the way along it, `inset` px in from it, and the way its normal points out
    (degrees from the nose, towards +X).
    """
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    length = math.hypot(dx, dy)
    nx = dy / length
    ny = -dx / length
    # The normal pointing away from the centre.
    mx = a[0] + dx * share
    my = a[1] + dy * share
    if nx * mx + ny * my < 0:
        nx = -nx
        ny = -ny
    return [mx - nx * inset, my - ny * inset, math.atan2(nx, -ny) / DEG]


def mirror_gun(gun: list[float]) -> list[float]:
    """Return the gun mirroring `gun` across the centre line."""
    return [-gun[0], gun[1], -gun[2]]


# The parts (FB-STAR-FORT-03): the moat's pylons on the rear bastions, the ravelins, the cavalier
# (a raised gun platform in the nose bastion) and the gatehouse in the rear curtain.
PYLON_AT = polar(50, 144)
RAVELIN_AT = polar(45, RAVELIN_DEG)
CAVALIER_AT = [0, -40]
CAVALIER_TOP = WALL_TOP
GATEHOUSE_AT = [0, 36]
GATE_TOP = 14

# The guns as it comes in (FB-STAR-FORT-08): the cavalier's turret, and on each ravelin a fixed
# twin gun out of its front face.
CAVALIER_GUN = {"size": 5, "barrels": 3, "gap": 1.3, "bore": 1, "length": 8}
RAVELIN_GUN = face_gun(
    polar(RAVELIN_BASE[0], RAVELIN_DEG - RAVELIN_BASE[1]),
    polar(RAVELIN_APEX, RAVELIN_DEG),
    0.55,
    3.2,
)
EMBRASURE = {"size": 3.2, "barrels": 3, "gap": 2.5, "bore": 0.9, "length": 5.5, "turret": False}
TWIN_EMBRASURE = {"size": 3, "barrels": 2, "gap": 2.5, "bore": 0.95, "length": 5.5, "turret": False}
# The embrasures each lost part opens (FB-STAR-FORT-09), right side (mirrored): the nose bastion's
# faces, the side bastions' front faces, the side bastions' mortars, the curtains behind the
# ravelins; on the centre line, the nose salient's laser and, last, the parade ground's rotor.
NOSE_GUN = face_gun(polar(SALIENT_R, 0), polar(SHOULDER[0], SHOULDER[1]), 0.62, 3.2)
SIDE_GUN = face_gun(polar(SHOULDER[0], 72 - SHOULDER[1]), polar(SALIENT_R, 72), 0.45, 3.4)
SIDE_MORTAR_AT = polar(47, 72)
SIDE_MORTAR_DEG = 40
SIDE_MORTAR = {
    "size": 4.6,
    "barrels": 1,
    "bore": 2.9,
    "length": 4.4,
    "style": "mortar",
    "axis": 0.8,
    "turret": False,
}
CURTAIN_GUN = face_gun(polar(FLANK[0], FLANK[1]), polar(FLANK[0], 72 - FLANK[1]), 0.5, 3)
LASER_AT = [0, -57]
SALIENT_LASER = {"size": 3.4, "bore": 1.6, "length": 8, "restDeg": 0}
ROTOR_AT = [0, -19]
ROTOR = {"size": 5, "barrels": 16, "layout": "ring", "bore": 0.7, "length": 3.4}
# The hatches over them (BOSS-58): an octagon this wide round each, over the rampart.
HATCH_R = 5.2

ORANGE = bullet("orange", 180)
RED = bullet("red", 200)
MAGENTA = bullet("magenta", 185)
PURPLE = bullet("purple", 190)
# The side bastions' mortar flak (FB-STAR-FORT-08): a big, slow shell bursting into a ring of 8.
FLAK = bursting("orange", 100, 7, [1.2, 8, bullet("red", 150)])


def fpart(part_id: str, at: list[Any], radius: float, health: float) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    return part(part_id, at, radius, health, {"drop": 0.6})


def _fixed(mount_id: str, gun: list[float], height: float, options: Any) -> Any:
    """Return a fixed gun on the core at `gun` (`[x, y, degrees]`), along its face's normal."""
    return gun_mount(
        mount_id, "core", [gun[0], gun[1]], height, merge(options, {"restDeg": -gun[2]})
    )


def _pair(prefix: str, gun: list[float], height: float, options: Any) -> list[Any]:
    """Return the fixed guns `prefix-left` and `prefix-right`, mirror images (see `_fixed`)."""
    return [
        _fixed(prefix + "-left", mirror_gun(gun), height, options),
        _fixed(prefix + "-right", gun, height, options),
    ]


def _salvo(mount_id: str, gun: list[float], every: float, count: int, b: Any, first: float) -> Any:
    """Return a volley of the fixed gun `mount_id`: one bullet a barrel, along them."""
    return merge(volley.fan("core", every, count, 0, b, first, gun[2]), {"mount": mount_id})


def _salvos(prefix: str, gun: list[float], every: float, count: int, b: Any, first: float) -> Any:
    """Return the salvos of the fixed guns `prefix-left` and `prefix-right`, half a beat apart."""
    return [
        _salvo(prefix + "-left", mirror_gun(gun), every, count, b, first),
        _salvo(prefix + "-right", gun, every, count, b, first + every / 2),
    ]


SIDE_MORTAR_GUN = [SIDE_MORTAR_AT[0], SIDE_MORTAR_AT[1], SIDE_MORTAR_DEG]


def _stage(k: int) -> list[Any]:
    """Return the core's volleys in stage `k` (FB-STAR-FORT-08, FB-STAR-FORT-09).

    Each stage opens one more pair of embrasures (one gun on the centre line in stage 4, the rotor
    in the last one) and keeps the ones before, a little slower as more join.
    """
    volleys: list[Any] = []
    if k >= 1:
        volleys.extend(_salvos("nose", NOSE_GUN, 2.6 + 0.1 * k, 3, ORANGE, 0.6))
    if k >= 2:
        volleys.extend(_salvos("side", SIDE_GUN, 2.6 + 0.1 * k, 3, RED, 1.0))
    if k >= 3:
        volleys.extend(_salvos("mortar", SIDE_MORTAR_GUN, 3.6 + 0.1 * k, 1, FLAK, 1.6))
    if k >= 4:
        volleys.append(merge(volley.laser("core", 6.5, 1.6, 2.0), {"mount": "salient-laser"}))
    if k >= 5:
        volleys.extend(_salvos("curtain", CURTAIN_GUN, 2.4 + 0.1 * k, 2, MAGENTA, 0.8))
    if k >= 6:
        volleys.append(merge(volley.ring("core", 1.3, 16, 8, PURPLE, 0.4), {"mount": "rotor"}))
    return volleys


_STAR_FORT = record({
    "id": "star-fort",
    # Its points, its core's drop and its parts' drops (FB-STAR-FORT-13).
    "stats": stats({
        "id": "star-fort",
        "name": "Star Fort",
        "size": 5.5,
        "coreRadius": 22,
        "coreHealth": 5000,
        "points": 17000,
        "groundSpeed": 0.2,
        "coreDrop": 1,
        "parts": [
            fpart("pylon-left", [-PYLON_AT[0], PYLON_AT[1]], 8, 1500),
            fpart("pylon-right", PYLON_AT, 8, 1500),
            fpart("ravelin-left", [-RAVELIN_AT[0], RAVELIN_AT[1]], 9, 1600),
            fpart("ravelin-right", RAVELIN_AT, 9, 1600),
            fpart("cavalier", CAVALIER_AT, 9, 1800),
            fpart("gatehouse", GATEHOUSE_AT, 9, 1500),
        ],
    }),
    # Where it stops and how it moves in place (FB-STAR-FORT-06): a mountain of stone, barely
    # drifting.
    "stopFraction": 0.7,
    "sway": {"amplitude": 18, "period": 14},
    "bob": {"amplitude": 3, "period": 6},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-STAR-FORT-03, FB-STAR-FORT-09).
    "mounts": concat(
        [
            gun_mount("cavalier", "cavalier", CAVALIER_AT, CAVALIER_TOP, CAVALIER_GUN),
            gun_mount(
                "ravelin-left",
                "ravelin-left",
                [-RAVELIN_GUN[0], RAVELIN_GUN[1]],
                RAVELIN_TOP,
                merge(TWIN_EMBRASURE, {"restDeg": RAVELIN_GUN[2]}),
            ),
            gun_mount(
                "ravelin-right",
                "ravelin-right",
                [RAVELIN_GUN[0], RAVELIN_GUN[1]],
                RAVELIN_TOP,
                merge(TWIN_EMBRASURE, {"restDeg": -RAVELIN_GUN[2]}),
            ),
        ],
        _pair("nose", NOSE_GUN, WALL_TOP, EMBRASURE),
        _pair("side", SIDE_GUN, WALL_TOP, EMBRASURE),
        _pair("mortar", SIDE_MORTAR_GUN, WALL_TOP, SIDE_MORTAR),
        [laser_mount("salient-laser", "core", LASER_AT, WALL_TOP, SALIENT_LASER)],
        _pair("curtain", CURTAIN_GUN, WALL_TOP, TWIN_EMBRASURE),
        [gun_mount("rotor", "core", ROTOR_AT, PARADE, ROTOR)],
    ),
    # Its parts' volleys, then the core's pattern per stage (FB-STAR-FORT-08): the cavalier sweeps
    # aimed spreads, the ravelins' fixed guns cross their streams under it; the core fires nothing
    # as it comes in, then one more pair of embrasures at each stage (see `_stage`).
    "stages": stages(
        [
            volley.aimed("cavalier", 2.6, 3, 9, ORANGE, 1.4),
            volley.fan("ravelin-left", 2.8, 2, 0, RED, 1.0, -RAVELIN_GUN[2]),
            volley.fan("ravelin-right", 2.8, 2, 0, RED, 2.4, RAVELIN_GUN[2]),
        ],
        [_stage(k) for k in range(7)],
    ),
})

# FB-STAR-FORT-10: the right rear bastion as drawn, between its heights, and its swing out about
# the vertical through its outer flank root (the left one is its mirror image); the sweeper riding
# it stands in its pylon's socket.
REAR_BASTION = bastion_outline(144)
BASTION_Y = [ROCK_TOP - 0.5, WALL_TOP + 0.5]  # type: list[float]
BASTION_PIVOT = [REAR_BASTION[0][0], REAR_BASTION[0][1], 0]
BASTION_SWING = swing(BASTION_PIVOT, "up", [0, -40])
SWEEPER_AT = move_point(BASTION_SWING, -40, [PYLON_AT[0], PYLON_AT[1], 0])
SWEEPER_POD = [WALL_TOP, WALL_TOP + 3]
# FB-STAR-FORT-11: the keep's outline (an octagon round it), between its heights, and its slide
# up; the gatling on its roof once risen.
KEEP_OUTLINE = [
    [
        KEEP_AT[0] + (KEEP_R + 1) * math.cos(k * math.pi / 4 + math.pi / 8),
        KEEP_AT[1] + (KEEP_R + 1) * math.sin(k * math.pi / 4 + math.pi / 8),
    ]
    for k in range(8)
]
KEEP_Y = [PARADE, KEEP_TOP + 1]  # type: list[float]
KEEP_SLIDE = slide([[0, 0, 0], [0, 0, KEEP_RISE]])
GATLING_POD = [KEEP_TOP + KEEP_RISE, KEEP_TOP + KEEP_RISE + 3]
# The parade ground's flagstones over each battery (the right ones; mirrored), and the battery.
BATTERY_AT = [19, 8]
FLAGSTONES = [[12, 2], [27, 2], [27, 14], [12, 14]]  # type: list[list[float]]
FLAGSTONE_Y = [PARADE - 0.5, PARADE + 1.5]  # type: list[float]
BATTERY_POD = [PARADE, PARADE + 3]


def _hatch(mount_id: str, at: list[Any]) -> Any:
    """Return the hatch over the core gun `mount_id` at `at` (BOSS-58): an octagonal shutter."""
    outline = [
        [
            at[0] + HATCH_R * math.cos(k * math.pi / 4 + math.pi / 8),
            at[1] + HATCH_R * math.sin(k * math.pi / 4 + math.pi / 8),
        ]
        for k in range(8)
    ]
    return armour_region(mount_id + "-hatch", None, outline, "ring", None, False, mount_id)


def _hatches() -> list[Any]:
    """Return the hatches over every embrasure and the rotor."""
    result: list[Any] = []
    for prefix_gun in [
        ["nose", NOSE_GUN],
        ["side", SIDE_GUN],
        ["mortar", SIDE_MORTAR_GUN],
        ["curtain", CURTAIN_GUN],
    ]:
        name: Any = prefix_gun[0]
        gun: Any = prefix_gun[1]
        result.append(_hatch(name + "-left", [-gun[0], gun[1]]))
        result.append(_hatch(name + "-right", [gun[0], gun[1]]))
    result.append(_hatch("salient-laser", LASER_AT))
    result.append(_hatch("rotor", ROTOR_AT))
    return result


# Its transformations: once both pylons are down its rear bastions swing out, a sweeper riding
# each; once both ravelins are down its keep rises, a gatling on its roof, and the flagstones
# either side of it burst off on a battery each. Each embrasure's hatch bursts as its gun first
# comes into use (BOSS-58, FB-STAR-FORT-09).
STAR_FORT = with_weapons(
    merge(
        _STAR_FORT,
        {
            "transformParts": [
                ["pylon-left", "pylon-right"],
                ["ravelin-left", "ravelin-right"],
            ]
        },
    ),
    [
        hidden_weapon(
            "sweeper-left",
            "sweeper",
            [-SWEEPER_AT[0], SWEEPER_AT[1]],
            7,
            1440,
            1,
            "red",
            1.0,
            SWEEPER_POD,
        ),
        hidden_weapon(
            "sweeper-right",
            "sweeper",
            [SWEEPER_AT[0], SWEEPER_AT[1]],
            7,
            1440,
            1,
            "red",
            3.0,
            SWEEPER_POD,
        ),
        hidden_weapon(
            "battery-left",
            "battery",
            [-BATTERY_AT[0], BATTERY_AT[1]],
            8,
            1800,
            2,
            "red",
            1.0,
            BATTERY_POD,
        ),
        hidden_weapon("battery-right", "battery", BATTERY_AT, 8, 1800, 2, "red", 2.0, BATTERY_POD),
        hidden_weapon("gatling", "gatling", KEEP_AT, 7, 1800, 2, "magenta", 1.4, GATLING_POD),
    ],
    concat(
        moving_region("bastion", 1, REAR_BASTION, BASTION_SWING, None, BASTION_Y),
        moving_region("keep", 2, KEEP_OUTLINE, KEEP_SLIDE, None, KEEP_Y, False),
        [armour_region("flagstones", 2, FLAGSTONES, "shell", FLAGSTONE_Y)],
        _hatches(),
    ),
)
