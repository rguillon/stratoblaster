# Copyright (c) 2026 Renaud Guillon
"""The Iron Lighthouse, the Lab's L-22 mini boss (specs/bosses/lab/L-22-iron-lighthouse.md).

Lab boss: in the dev viewer only, no level brings it in. A gigantic flying lighthouse: a round
riveted iron platform held up by a ring of propellers under its rim, a tall lighthouse tower on it
(its lantern room, gallery rail and revolving lens on top), two keeper's cottages on its front, an
iron buttress either side of the tower and a dynamo house at its back. Its lantern's beam is a fixed
laser straight down the screen; the buttresses' casemates fire fixed rows down and out. As it loses
parts, guns rise out of its cottages' roofs and its landing stage; once both buttresses are gone the
deck leaves they stood on drop open like trapdoors (they change shape, BOSS-45) and an orb rises out
of each well (MB-IRON-LIGHTHOUSE-10). Its last guns: its lamp, then a rotor out of its lantern's
dome.

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


# MB-IRON-LIGHTHOUSE-01: the platform's radius, its deck's top and its rim's foot.
PLATFORM_R = 38
DECK = 6
DECK_LOW = 2
# The tower (the core): its centre, its foot's and its top's radius, its gallery's floor; the
# lantern room's radius and roof, and the dome over it (the rotor's hatch).
TOWER_AT = [0, 6]
TOWER_FOOT = 9.5
TOWER_NECK = 6
GALLERY = 30
GALLERY_R = 8.6
LANTERN_R = 5
LANTERN_TOP = 37
DOME_R = 6
# The deck leaves (MB-IRON-LIGHTHOUSE-05): the right one's hinge along `x = LEAF_X`, between
# `LEAF_Y` (front and back); out to the rim. They drop `LEAF_DROP` degrees about the hinge.
LEAF_X = 18
LEAF_Y = [-12, 21]
LEAF_DROP = 96
# The buttresses (MB-IRON-LIGHTHOUSE-03): their centres; each one's casemate at its foot.
BUTTRESS_AT = [27, 4]
CASEMATE_AT = [30, -2]
CASEMATE_TOP = 10
CASEMATE_DEG = 32
# The dynamo house at its back (no gun): its centre.
DYNAMO_AT = [0, 28]
# The keeper's cottages on its front (the core's): their centres, half sizes `[x, y]`, walls' top
# and ridge.
COTTAGE_AT = [16, -21]
COTTAGE_HALF = [5.5, 4.5]
COTTAGE_WALL = 11
COTTAGE_RIDGE = 15
# The landing stage at its bow: its gun's place and height, under a hatch.
BOW_AT = [0, -31]
BOW_TOP = DECK + 1
# The propeller ring under the rim (MB-IRON-LIGHTHOUSE-06): its propellers' angles (degrees, from
# config +X), their ducts' radius out and their own radius.
PROPS = [50, 130, 230, 310]
PROP_OUT = 43
PROP_R = 8
# The hoop the propellers' ducts hang on (its foot's height) and the blades' height.
HOOP_H = DECK_LOW - 3.5
HOOP_LIFT = HOOP_H + 1.2

# The guns (BOSS-58): the lamp (a fixed laser in the lantern, pointing down the screen), the
# casemates' fixed rows of three, the cottages' twin turrets, the bow's fixed row of four and the
# lantern's rotor (its last spiral).
LAMP = {"size": 3, "bore": 1.6, "length": 9}
LAMP_TOP = GALLERY + 1.5
CASEMATE = {"size": 4, "barrels": 3, "gap": 2.6, "bore": 0.9, "length": 6, "turret": False}
COTTAGE_GUN = {"size": 4, "barrels": 2, "gap": 1.3, "bore": 1.0, "length": 6.5}
BOW_GUN = {
    "size": 4.4,
    "barrels": 4,
    "gap": 2.4,
    "bore": 0.9,
    "length": 6,
    "turret": False,
}
ROTOR = {"size": 4.2, "barrels": 12, "layout": "ring", "bore": 0.8, "length": 3.2}

RED = bullet("red", 185)
ORANGE = bullet("orange", 170)
MAGENTA = bullet("magenta", 180)
SPIRAL = bullet("orange", 160)


def _core_gun(mount_id: str, shot: Any) -> Any:
    """Return the core's `shot` fired from its mount `mount_id`."""
    return merge(shot, {"mount": mount_id})


# The lantern's beam (MB-IRON-LIGHTHOUSE-08): a laser straight down the screen, in every stage.
LAMP_BEAM = _core_gun("lamp", volley.laser("core", 6.5, 1.6, 2.2))
# The cottages' twin turrets (from stage 1 on) and the landing stage's row (from stage 2 on).
COTTAGES = [
    _core_gun("cottage-left", volley.aimed("core", 2.6, 2, 8, MAGENTA, 0.9)),
    _core_gun("cottage-right", volley.burst("core", 2.8, 3, 0.14, MAGENTA, 1.8)),
]
BOW = _core_gun("bow-gun", volley.fan("core", 2.4, 4, 0, RED, 1.2))

_IRON_LIGHTHOUSE = record({
    "id": "iron-lighthouse",
    # Its points and its parts' drops (MB-IRON-LIGHTHOUSE-11).
    "stats": stats({
        "id": "iron-lighthouse",
        "name": "Iron Lighthouse",
        "size": 3.6,
        "coreRadius": 13,
        "coreHealth": 1500,
        "points": 3800,
        "groundSpeed": 0.4,
        "parts": [
            part("buttress-left", [-BUTTRESS_AT[0], BUTTRESS_AT[1]], 10, 650),
            part("buttress-right", BUTTRESS_AT, 10, 650),
            part("dynamo", DYNAMO_AT, 10, 750),
        ],
    }),
    # Where it stops and how it moves in place (MB-IRON-LIGHTHOUSE-06): a slow, heavy drift.
    "stopFraction": 0.72,
    "sway": {"amplitude": 46, "period": 9},
    "bob": {"amplitude": 5, "period": 4.4},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-IRON-LIGHTHOUSE-07).
    "mounts": [
        gun_mount(
            "buttress-left",
            "buttress-left",
            [-CASEMATE_AT[0], CASEMATE_AT[1]],
            CASEMATE_TOP,
            merge(CASEMATE, {"restDeg": CASEMATE_DEG}),
        ),
        gun_mount(
            "buttress-right",
            "buttress-right",
            CASEMATE_AT,
            CASEMATE_TOP,
            merge(CASEMATE, {"restDeg": -CASEMATE_DEG}),
        ),
        laser_mount("lamp", "core", TOWER_AT, LAMP_TOP, LAMP),
        gun_mount(
            "cottage-left", "core", [-COTTAGE_AT[0], COTTAGE_AT[1]], COTTAGE_WALL, COTTAGE_GUN
        ),
        gun_mount("cottage-right", "core", COTTAGE_AT, COTTAGE_WALL, COTTAGE_GUN),
        gun_mount("bow-gun", "core", BOW_AT, BOW_TOP, BOW_GUN),
        gun_mount("lantern-rotor", "core", TOWER_AT, LANTERN_TOP, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-IRON-LIGHTHOUSE-08): the
    # casemates fire rows of three down and out, the dynamo nothing; the core's lamp fires its beam
    # at every stage, the cottages' turrets join it at stage 1, the landing stage's row at stage 2,
    # the lantern's rotor's spiral of 12 at stage 3.
    "stages": stages(
        [
            volley.fan("buttress-left", 2.6, 3, 0, ORANGE, 1.0, CASEMATE_DEG),
            volley.fan("buttress-right", 2.6, 3, 0, ORANGE, 2.3, -CASEMATE_DEG),
        ],
        [
            [LAMP_BEAM],
            concat([LAMP_BEAM], COTTAGES),
            concat([LAMP_BEAM, BOW], COTTAGES),
            concat(
                [
                    LAMP_BEAM,
                    BOW,
                    _core_gun("lantern-rotor", volley.ring("core", 1.5, 12, 15, SPIRAL, 0.4)),
                ],
                COTTAGES,
            ),
        ],
    ),
})


def leaf_outline() -> list[list[float]]:
    """Return the right deck leaf's outline: from its hinge out to the rim's arc."""
    a0 = math.asin(LEAF_Y[0] / PLATFORM_R)
    a1 = math.asin(LEAF_Y[1] / PLATFORM_R)
    arc = [
        [
            PLATFORM_R * math.cos(a0 + (a1 - a0) * k / 6),
            PLATFORM_R * math.sin(a0 + (a1 - a0) * k / 6),
        ]
        for k in range(7)
    ]
    return concat([[LEAF_X, LEAF_Y[0]]], concat(arc, [[LEAF_X, LEAF_Y[1]]]))


def octagon(at: list[Any], radius: float) -> list[list[float]]:
    """Return an octagon `radius` round `at` (a hatch's outline)."""
    return [
        [
            at[0] + radius * math.cos(k * math.pi / 4 + math.pi / 8),
            at[1] + radius * math.sin(k * math.pi / 4 + math.pi / 8),
        ]
        for k in range(8)
    ]


def box_outline(at: list[Any], half: list[Any]) -> list[list[float]]:
    """Return the rectangle `half` either way round `at`."""
    return [
        [at[0] - half[0], at[1] - half[1]],
        [at[0] + half[0], at[1] - half[1]],
        [at[0] + half[0], at[1] + half[1]],
        [at[0] - half[0], at[1] + half[1]],
    ]


# MB-IRON-LIGHTHOUSE-05: each deck leaf drops about its hinge (along the boss, at the deck's top)
# from flat (as drawn) to hanging; the left one is its mirror image. It leaves its well's floor.
LEAF_MOTION = swing([LEAF_X, 0, DECK], "along", [0, LEAF_DROP])
LEAF_HEIGHTS = [DECK_LOW, DECK]
# The orbs (MB-IRON-LIGHTHOUSE-10): where they rise in the wells, their pods' foot and top.
ORB_AT = [28, 3]
ORB_POD = [DECK_LOW + 0.5, DECK + 0.5]

# Its transformation (BOSS-45, MB-IRON-LIGHTHOUSE-10): once both buttresses are gone the deck
# leaves they stood on drop open and an orb rises out of each well. The hatches over its late core
# guns burst as they come into use (BOSS-58): the cottages' roofs, the landing stage's hatch and
# the lantern's dome.
IRON_LIGHTHOUSE = with_weapons(
    merge(_IRON_LIGHTHOUSE, {"transformParts": [["buttress-left", "buttress-right"]]}),
    [
        hidden_weapon(
            "orb-left", "orb", [-ORB_AT[0], ORB_AT[1]], 8, 600, 1, "orange", 1.2, ORB_POD
        ),
        hidden_weapon("orb-right", "orb", ORB_AT, 8, 600, 1, "orange", 2.0, ORB_POD),
    ],
    concat(
        moving_region("leaf", 1, leaf_outline(), LEAF_MOTION, "shell", LEAF_HEIGHTS),
        [
            armour_region(
                "roof-left",
                None,
                box_outline([-COTTAGE_AT[0], COTTAGE_AT[1]], COTTAGE_HALF),
                "shell",
                None,
                False,
                "cottage-left",
            ),
            armour_region(
                "roof-right",
                None,
                box_outline(COTTAGE_AT, COTTAGE_HALF),
                "shell",
                None,
                False,
                "cottage-right",
            ),
            armour_region("bow-hatch", None, octagon(BOW_AT, 5.5), "ring", None, False, "bow-gun"),
            armour_region(
                "dome", None, octagon(TOWER_AT, DOME_R), "ring", None, False, "lantern-rotor"
            ),
        ],
    ),
)
