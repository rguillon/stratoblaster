# Copyright (c) 2026 Renaud Guillon
"""The Lab's L-9 final boss, the Folding Citadel (specs/bosses/lab/L-9-folding-citadel.md).

A flat, square fortress folded shut like an origami box: four great wall panels hinged on the
edges of its square base, leaning in over its courtyard round a central keep, a corner tower at
each corner. Lab boss: in the dev viewer only (no level brings it in). At its first transformation
its panels swing open outward like a flower (it changes shape, BOSS-45), a missile rack riding in on
each side panel; at its second the plating of its front courtyard bursts off on a pair of batteries
and a gatling.

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


DEG = math.pi / 180

# FB-FOLDING-CITADEL-01: the base's half width (its edges are the panels' hinges), the hinges'
# height (the base deck's top), each panel's length from its hinge to its outer edge and its
# thickness, and how far each panel is folded up from flat at rest (130°: leaning in over the
# courtyard, 50° from the ground).
BASE = 44
HINGE_H = 4
PANEL_LENGTH = 32
PANEL_THICK = 3
FOLD = 130
# The panel's lean at rest from the ground, and its tip's distance from the centre and height.
LEAN = 180 - FOLD
TIP_OUT = BASE - PANEL_LENGTH * math.cos(LEAN * DEG)
TIP_H = HINGE_H + PANEL_LENGTH * math.sin(LEAN * DEG)
# A panel's outer edge is shorter than its hinge, so that folded up its sides meet its neighbours'
# along the box's diagonals: half of it.
TIP_HALF = TIP_OUT

# The keep in the middle (FB-FOLDING-CITADEL-02): its half width and its roof's height.
KEEP_HALF = 17
KEEP_TOP = 30
# The corner towers: their centres' distance out along each axis, their radius and their top.
TOWER_AT = 53
TOWER_RADIUS = 9
TOWER_TOP = 16


def side_panel() -> list[list[float]]:
    """Return the right side panel's outline as drawn, folded up at rest (seen from above).

    A trapezoid from its hinge in to its tip, its sides along the box's diagonals.
    """
    return [[BASE, -BASE], [TIP_OUT, -TIP_HALF], [TIP_OUT, TIP_HALF], [BASE, BASE]]


def front_panel() -> list[list[float]]:
    """Return the front panel's outline as drawn, folded up at rest (its hinge at -Y)."""
    return [[-BASE, -BASE], [BASE, -BASE], [TIP_HALF, -TIP_OUT], [-TIP_HALF, -TIP_OUT]]


def back_panel() -> list[list[float]]:
    """Return the back panel's outline as drawn, folded up at rest (its hinge at +Y)."""
    return [[BASE, BASE], [-BASE, BASE], [-TIP_HALF, TIP_OUT], [TIP_HALF, TIP_OUT]]


# FB-FOLDING-CITADEL-05: each panel is drawn folded up as it rests (both its faces then face the
# camera's way) and swings `FOLD` degrees about its hinge (the top inner edge of its open pose) to
# lie flat open. The right one about the boss's length (its left mirrored), the front and back
# ones across it.
SIDE_SWING = swing([BASE, 0, HINGE_H], "along", [0, FOLD])
FRONT_SWING = swing([0, -BASE, HINGE_H], "across", [0, FOLD])
BACK_SWING = swing([0, BASE, HINGE_H], "across", [0, -FOLD])
# The heights a panel lies between, open flat: under its hinge.
PANEL_HEIGHTS = [HINGE_H - PANEL_THICK, HINGE_H]


def folded(v: float, h: float) -> list[float]:
    """Where a point `v` px out from the right hinge, `h` px over the open panel, sits at rest.

    Returns `[x, height]` (the panel folded up `FOLD` degrees).
    """
    a = -FOLD * DEG
    return [BASE + h * math.sin(a) + v * math.cos(a), HINGE_H + h * math.cos(a) - v * math.sin(a)]


# The wall guns (FB-FOLDING-CITADEL-03): on a sponson bolted on each side panel's outer face, 14 px
# up it from its hinge.
SPONSON_V = 14
_SPONSON = folded(SPONSON_V, -PANEL_THICK)
WALL_AT = [math.floor(_SPONSON[0] + 2), 0]
WALL_GUN_HEIGHT = math.floor(_SPONSON[1] + 3)

# The courtyard's front plating (FB-FOLDING-CITADEL-11), bared once the panels are open and shed at
# the second transformation: `[x0, x1, y0, y1]`, its top.
COURT = [-40, 40, -41, -19]
COURT_TOP = HINGE_H + 3

GOLD = bullet("orange", 180)
RED = bullet("red", 190)
MAGENTA = bullet("magenta", 175)


def fpart(part_id: str, at: list[Any], radius: float, health: float) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    return part(part_id, at, radius, health, {"drop": 0.6})


BASTION_LEFT = [-TOWER_AT, -TOWER_AT]
BASTION_RIGHT = [TOWER_AT, -TOWER_AT]
TOWER_LEFT = [-TOWER_AT, TOWER_AT]
TOWER_RIGHT = [TOWER_AT, TOWER_AT]
CUPOLA_TOP = TOWER_TOP + 4.5

# The guns: twin barrels on the wall sponsons, three on the front bastions' turrets, a laser turret
# on each rear tower, and the keep's: a five-barrelled fan turret on its front and a rotor on its
# roof, under a hatch until its last stage.
WALL_GUN = {"size": 4.5, "barrels": 2, "gap": 2.8, "bore": 1.1, "length": 7.5}
BASTION_GUN = {"size": 5, "barrels": 3, "gap": 1.2, "bore": 1.1, "length": 7.5}
TOWER_LASER = {"size": 5, "bore": 2.2, "length": 10, "turret": True}
KEEP_GUN = {"size": 6, "barrels": 5, "gap": 1, "bore": 1, "length": 8}
KEEP_ROTOR = {"size": 5.5, "barrels": 16, "layout": "ring", "bore": 0.7, "length": 3.4}
KEEP_GUN_AT = [0, -9]
ROTOR_AT = [0, 7]

_FOLDING_CITADEL = record({
    "id": "folding-citadel",
    # Its points, its core's drop and its parts' drops (FB-FOLDING-CITADEL-13).
    "stats": stats({
        "id": "folding-citadel",
        "name": "Folding Citadel",
        "size": 4.5,
        "coreRadius": 20,
        "coreHealth": 4000,
        "points": 14000,
        "groundSpeed": 0.3,
        "coreDrop": 1,
        "parts": [
            fpart("wall-left", [-WALL_AT[0], 0], 11, 1200),
            fpart("wall-right", WALL_AT, 11, 1200),
            fpart("bastion-left", BASTION_LEFT, 11, 1400),
            fpart("bastion-right", BASTION_RIGHT, 11, 1400),
            fpart("tower-left", TOWER_LEFT, 11, 1550),
            fpart("tower-right", TOWER_RIGHT, 11, 1550),
        ],
    }),
    # Where it stops and how it moves in place (FB-FOLDING-CITADEL-06): heavy and slow.
    "stopFraction": 0.73,
    "sway": {"amplitude": 26, "period": 11},
    "bob": {"amplitude": 4, "period": 5},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-FOLDING-CITADEL-03).
    "mounts": [
        gun_mount("wall-left", "wall-left", [-WALL_AT[0], 0], WALL_GUN_HEIGHT, WALL_GUN),
        gun_mount("wall-right", "wall-right", WALL_AT, WALL_GUN_HEIGHT, WALL_GUN),
        gun_mount("bastion-left", "bastion-left", BASTION_LEFT, CUPOLA_TOP, BASTION_GUN),
        gun_mount("bastion-right", "bastion-right", BASTION_RIGHT, CUPOLA_TOP, BASTION_GUN),
        laser_mount("tower-left", "tower-left", TOWER_LEFT, CUPOLA_TOP, TOWER_LASER),
        laser_mount("tower-right", "tower-right", TOWER_RIGHT, CUPOLA_TOP, TOWER_LASER),
        gun_mount("keep-gun", "core", KEEP_GUN_AT, KEEP_TOP, KEEP_GUN),
        gun_mount("keep-rotor", "core", ROTOR_AT, KEEP_TOP, KEEP_ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-FOLDING-CITADEL-08): closed, tight
    # aimed fire (the wall guns' aimed pairs, the bastions' bursts, the towers' aimed lasers, the
    # keep's single shots and narrow spreads); open, wide fans 12° apart (BOSS-58), ending in the
    # roof rotor's spiral.
    "stages": stages(
        [
            volley.aimed("wall-left", 1.9, 2, 5, RED, 0.8),
            volley.aimed("wall-right", 1.9, 2, 5, RED, 1.75),
            volley.burst("bastion-left", 2.6, 3, 0.14, GOLD, 1.2),
            volley.burst("bastion-right", 2.6, 3, 0.14, GOLD, 2.5),
            volley.laser("tower-left", 7.5, 1.4, 2.5),
            volley.laser("tower-right", 7.5, 1.4, 6.25),
        ],
        [
            [volley.aimed("core", 2.6, 1, 0, RED, 1.4)],
            [volley.aimed("core", 2.4, 3, 6, RED, 1)],
            [volley.fan("core", 2.4, 7, 12, GOLD, 0.8)],
            [
                volley.fan("core", 2.2, 5, 12, GOLD, 0.6),
                volley.aimed("core", 2.8, 1, 0, RED, 1.5),
            ],
            [
                volley.fan("core", 2.6, 9, 12, GOLD, 0.6),
                volley.burst("core", 2.8, 3, 0.14, RED, 1.6),
            ],
            [
                volley.fan("core", 2.4, 11, 10, MAGENTA, 0.6),
                volley.aimed("core", 2.6, 3, 12, RED, 1.4),
            ],
            [
                volley.ring("core", 1.3, 16, 9, GOLD, 0.4),
                volley.fan("core", 2.6, 7, 12, RED, 1.2),
            ],
        ],
    ),
})

# Where the racks ride (on the side panels, open: FB-FOLDING-CITADEL-10), and where the batteries
# and the gatling stand on the front courtyard (FB-FOLDING-CITADEL-11).
RACK_AT = [BASE + 18, 0]
BATTERY_AT = [24, -31]
GATLING_AT = [0, -31]

# Its transformations: once both wall guns are gone its four panels swing open outward like a box
# unfolding, a rack riding in on each side panel; once both bastions are gone the front courtyard's
# plating bursts off for a pair of batteries and a gatling on the centre line. The hatch over the
# keep's rotor bursts as the rotor comes into use, in its last stage (BOSS-58).
FOLDING_CITADEL = with_weapons(
    merge(
        _FOLDING_CITADEL,
        {"transformParts": [["wall-left", "wall-right"], ["bastion-left", "bastion-right"]]},
    ),
    [
        hidden_weapon(
            "rack-left",
            "rack",
            [-RACK_AT[0], RACK_AT[1]],
            9,
            1240,
            1,
            "orange",
            1.2,
            [HINGE_H, HINGE_H + 3],
        ),
        hidden_weapon(
            "rack-right", "rack", RACK_AT, 9, 1240, 1, "orange", 2.0, [HINGE_H, HINGE_H + 3]
        ),
        hidden_weapon(
            "battery-left",
            "battery",
            [-BATTERY_AT[0], BATTERY_AT[1]],
            9,
            1550,
            2,
            "red",
            1.2,
            [HINGE_H, COURT_TOP + 1],
        ),
        hidden_weapon(
            "battery-right",
            "battery",
            BATTERY_AT,
            9,
            1550,
            2,
            "red",
            2.0,
            [HINGE_H, COURT_TOP + 1],
        ),
        hidden_weapon(
            "gatling", "gatling", GATLING_AT, 8, 1550, 2, "magenta", 1.6, [HINGE_H, COURT_TOP + 1]
        ),
    ],
    concat(
        concat(
            moving_region("panel", 1, side_panel(), SIDE_SWING, None, [PANEL_HEIGHTS[0], 1000]),
            concat(
                moving_region(
                    "panel-front",
                    1,
                    front_panel(),
                    FRONT_SWING,
                    None,
                    [PANEL_HEIGHTS[0], 1000],
                    False,
                ),
                moving_region(
                    "panel-back",
                    1,
                    back_panel(),
                    BACK_SWING,
                    None,
                    [PANEL_HEIGHTS[0], 1000],
                    False,
                ),
            ),
        ),
        [
            armour_region(
                "court",
                2,
                [
                    [COURT[0], COURT[2]],
                    [COURT[1], COURT[2]],
                    [COURT[1], COURT[3]],
                    [COURT[0], COURT[3]],
                ],
                "shell",
                [HINGE_H, COURT_TOP],
                False,
            ),
            armour_region(
                "rotor-hatch",
                None,
                [
                    [
                        ROTOR_AT[0] + 7 * math.cos(k * math.pi / 4),
                        ROTOR_AT[1] + 7 * math.sin(k * math.pi / 4),
                    ]
                    for k in range(8)
                ],
                "ring",
                None,
                False,
                "keep-rotor",
            ),
        ],
    ),
)
