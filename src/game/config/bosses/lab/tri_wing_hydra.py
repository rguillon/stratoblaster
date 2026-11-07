# Copyright (c) 2026 Renaud Guillon
"""L-1 final boss of the Lab: the Tri-Wing Hydra (specs/bosses/lab/L-1-tri-wing-hydra.md).

A three-headed hydra seen from above: a plated body with three long necks fanned out in front of
it, each swaying (BOSS-33) with a turret head at its end, two shoulder plates, membrane wings at its
flanks and a tail. Its widely spaced heads catch the player in a crossfire. Offsets in px from its
centre, X right and Y up (its nose points down, at -Y). Lab boss: in the dev viewer only.
"""

from game.config.bosses.boss_guns import gun_mount, laser_mount, missile_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


GREEN = bullet("green", 180)
ORANGE = bullet("orange", 175)

# Height of the belly the armour lies on, and of the armour's top (FB-TRI-WING-HYDRA-05).
BELLY_TOP = 8
ARMOUR_TOP = 18
# The heads (FB-TRI-WING-HYDRA-03): where each sits, and the root of the neck it swings on.
HEAD_LEFT = [-54, -46]
HEAD_CENTRE = [0, -70]
NECK_LEFT = [-15, -22]
NECK_CENTRE = [0, -27]
# A head's turret on its crown: three barrels side by side, sweeping its fans and spreads.
HEAD_GUN = {"size": 5, "barrels": 3, "gap": 1.2, "bore": 1.1, "length": 7}
HEAD_GUN_HEIGHT = 10.5
# The shoulder plates: where each sits, and the height of its pauldron's top.
SHOULDER = [30, -6]
SHOULDER_TOP = 13


def fpart(part_id: str, at: list[Any], radius: float, health: float, options: Any = None) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57, `part_drop_chance`)."""
    extra = {} if options == None else options
    return part(part_id, at, radius, health, merge({"drop": 0.6}, extra))


def _neck(x: float, y: float, amplitude: float, period: float, phase: float) -> Any:
    """Return a neck's joint at its root `(x, y)`, swinging `amplitude` degrees to and fro."""
    return record({
        "x": x,
        "y": y,
        "swing": {"amplitudeDeg": amplitude, "period": period, "phase": phase},
    })


_TRI_WING_HYDRA = record({
    "id": "tri-wing-hydra",
    # Its points, its core's drop and its parts' drops (FB-TRI-WING-HYDRA-13).
    "stats": stats({
        "id": "tri-wing-hydra",
        "name": "Tri-Wing Hydra",
        "size": 4.5,
        "coreRadius": 22,
        "coreHealth": 2000,
        "points": 8000,
        "groundSpeed": 0.8,
        "coreDrop": 1,
        # Its necks sway at their roots, out of step (FB-TRI-WING-HYDRA-02, BOSS-33).
        "joints": {
            "neck-left": _neck(NECK_LEFT[0], NECK_LEFT[1], 9, 4.4, 0),
            "neck-right": _neck(-NECK_LEFT[0], NECK_LEFT[1], -9, 4.4, 0.45),
            "neck-centre": _neck(NECK_CENTRE[0], NECK_CENTRE[1], 7, 3.6, 0.2),
        },
        # The outer heads first, then the shoulders: the parts each transformation calls for, in
        # the order the debug key breaks them (`transformParts`).
        "parts": [
            fpart("head-left", HEAD_LEFT, 12, 800, {"joint": "neck-left"}),
            fpart("head-right", [-HEAD_LEFT[0], HEAD_LEFT[1]], 12, 800, {"joint": "neck-right"}),
            fpart("shoulder-left", [-SHOULDER[0], SHOULDER[1]], 13, 850),
            fpart("shoulder-right", SHOULDER, 13, 850),
            fpart("head-centre", HEAD_CENTRE, 12, 800, {"joint": "neck-centre"}),
        ],
    }),
    # Where it stops and how it moves in place (FB-TRI-WING-HYDRA-06).
    "stopFraction": 0.73,
    "sway": {"amplitude": 40, "period": 9},
    "bob": {"amplitude": 8, "period": 4.2},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-TRI-WING-HYDRA-03): a three-barrelled turret on each head's
    # crown, a block of four missile ports on the left shoulder and a laser on the right one. The
    # core has none: it dies with its last gun (BOSS-58).
    "mounts": [
        gun_mount(
            "head-left", "head-left", HEAD_LEFT, HEAD_GUN_HEIGHT, merge(HEAD_GUN, {"restDeg": 35})
        ),
        gun_mount(
            "head-right",
            "head-right",
            [-HEAD_LEFT[0], HEAD_LEFT[1]],
            HEAD_GUN_HEIGHT,
            merge(HEAD_GUN, {"restDeg": -35}),
        ),
        gun_mount("head-centre", "head-centre", HEAD_CENTRE, HEAD_GUN_HEIGHT, HEAD_GUN),
        missile_mount("shoulder-left", "shoulder-left", [-SHOULDER[0], -4], SHOULDER_TOP, 4),
        laser_mount(
            "shoulder-right",
            "shoulder-right",
            [SHOULDER[0], -10],
            SHOULDER_TOP,
            {"size": 4.5, "bore": 2.2, "length": 10},
        ),
    ],
    # Its parts' volleys, then what each stage adds (FB-TRI-WING-HYDRA-08): the outer heads' aimed
    # spreads cross from either side, the centre head sweeps fans straight down, and the heads left
    # fire harder as the others go. Its fans are 12 degrees apart, its spreads 10 (BOSS-58).
    "stages": stages(
        [
            volley.aimed("head-left", 2.2, 3, 10, GREEN, 0.8),
            volley.aimed("head-right", 2.2, 3, 10, GREEN, 1.9),
            volley.fan("head-centre", 2.6, 5, 12, ORANGE, 1.4),
            volley.missiles("shoulder-left", 6, 2, 30, 3),
            volley.laser("shoulder-right", 6.5, 1.4, 4.5),
        ],
        [
            [],
            [volley.burst("head-centre", 2.8, 3, 0.16, ORANGE, 1)],
            [volley.burst("head-centre", 2.4, 4, 0.14, ORANGE, 0.8)],
            [volley.aimed("head-centre", 2.4, 3, 10, ORANGE, 0.8)],
            [volley.burst("head-centre", 2.2, 5, 0.12, ORANGE, 0.6)],
            # Its last stage: the orb's second spiral, turning the other way.
            [volley.ring("orb", 2.6, 10, -13, GREEN, 2)],
        ],
    ),
})

# Its transformations (D-224, FB-TRI-WING-HYDRA-10, FB-TRI-WING-HYDRA-11): once both outer heads
# are gone its back plating bursts off for a pair of missile racks; once both shoulders are gone
# its breastplate bursts off for a pair of gun batteries and an orb on its centre line.
TRI_WING_HYDRA = with_weapons(
    merge(
        _TRI_WING_HYDRA,
        {"transformParts": [["head-left", "head-right"], ["shoulder-left", "shoulder-right"]]},
    ),
    [
        hidden_weapon("rack-left", "rack", [-12, 25], 8, 680, 1, "green", 1.2, [BELLY_TOP, 12]),
        hidden_weapon("rack-right", "rack", [12, 25], 8, 680, 1, "green", 2.0, [BELLY_TOP, 12]),
        hidden_weapon(
            "battery-left", "battery", [-15, -13], 8, 850, 2, "orange", 1.2, [BELLY_TOP, 12]
        ),
        hidden_weapon(
            "battery-right", "battery", [15, -13], 8, 850, 2, "orange", 2.0, [BELLY_TOP, 12]
        ),
        hidden_weapon("orb", "orb", [0, 3], 7, 850, 2, "green", 1.6, [BELLY_TOP, 11]),
    ],
    [
        # FB-TRI-WING-HYDRA-05: the back plating, the carapace over the rear of its body, from its
        # middle to the root of its tail; the racks lie under it.
        armour_region(
            "back",
            1,
            [
                [-23, 9],
                [23, 9],
                [26, 18],
                [23, 32],
                [15, 42],
                [0, 46],
                [-15, 42],
                [-23, 32],
                [-26, 18],
            ],
            "shell",
            None,
            False,
        ),
        # The breastplate, from its middle to the necks' roots; the batteries and the orb lie
        # under it.
        armour_region(
            "breast",
            2,
            [
                [-23, 9],
                [-26, -4],
                [-23, -18],
                [-14, -27],
                [0, -31],
                [14, -27],
                [23, -18],
                [26, -4],
                [23, 9],
            ],
            "shell",
            None,
            False,
        ),
    ],
)
