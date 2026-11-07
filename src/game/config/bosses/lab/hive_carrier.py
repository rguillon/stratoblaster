# Copyright (c) 2026 Renaud Guillon
"""The Hive Carrier (the Lab's L-2 final boss, specs/bosses/lab/L-2-hive-carrier.md).

A fat hexagonal hive-ship: a honeycomb of hexagonal cells over a waxy shell held by metal ribs. Its
two front cell-bays launch Hornets, its two rear ones lob big spores that burst into rings, and its
ram's queen gland fans bullets straight down: area denial and swarms rather than precise aim
(FB-HIVE-CARRIER-08). Offsets in px from the boss's centre, X right and Y up (its nose points
down, at -Y). Lab boss: in the dev viewer only, no level brings it in.
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, bursting, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


def fpart(part_id: str, at: list[Any], radius: float, health: float) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    return part(part_id, at, radius, health, {"drop": 0.6})


ORANGE = bullet("orange", 175)
RED = bullet("red", 185)
# The rear bays' spores: big and slow, bursting into a ring of six after 1.3 s (FB-HIVE-CARRIER-08).
SPORE = bursting("orange", 95, 8, [1.3, 6, bullet("orange", 150)])

# The hull: a hexagon its corners at (±66, 0) and (±36, ±54); its deck's height, which the
# honeycomb cells stand on (FB-HIVE-CARRIER-01).
DECK_TOP = 6
# The cell-bays' centres, at its four slanted corners (the right ones; the left ones mirror them).
BAY_X = 36
BAY_Y = 42

# The rear bays' spore cannons: one fat barrel on a turret, sweeping its fans of two
# (FB-HIVE-CARRIER-03).
SPORE_GUN = {"size": 5.5, "barrels": 1, "bore": 2.6, "length": 6}

_HIVE_CARRIER = record({
    "id": "hive-carrier",
    # Its points, its core's drop and its parts' drops (FB-HIVE-CARRIER-13).
    "stats": stats({
        "id": "hive-carrier",
        "name": "Hive Carrier",
        "size": 4,
        "coreRadius": 22,
        "coreHealth": 1900,
        "points": 9000,
        "groundSpeed": 0.4,
        "coreDrop": 1,
        "parts": [
            fpart("bay-front-left", [-BAY_X, -BAY_Y], 14, 720),
            fpart("bay-front-right", [BAY_X, -BAY_Y], 14, 720),
            fpart("bay-rear-left", [-BAY_X, BAY_Y], 14, 720),
            fpart("bay-rear-right", [BAY_X, BAY_Y], 14, 720),
            fpart("ram", [0, -60], 13, 880),
        ],
    }),
    # Where it stops and how it moves in place (FB-HIVE-CARRIER-06).
    "stopFraction": 0.74,
    "sway": {"amplitude": 35, "period": 10},
    "bob": {"amplitude": 6, "period": 5},
    # The front bays' Hornets (BOSS-25): two at a time, side by side, diving at the player.
    "launches": [
        {"from": "bay-front-left", "kind": "hornets", "count": 2, "every": 6.5, "first": 2.5},
        {"from": "bay-front-right", "kind": "hornets", "count": 2, "every": 6.5, "first": 5.75},
    ],
    "guns": {},
    # Its gun mounts (BOSS-58, FB-HIVE-CARRIER-03): a spore cannon in each rear bay's middle cell,
    # the queen gland's five-barrelled turret on the ram, and the core's on its queen chamber: the
    # crown turret on its front (its aimed shots, bursts and fans) and the rotor on its top (its
    # last ring), under a hatch until then. The front bays launch Hornets and have no gun.
    "mounts": [
        gun_mount("bay-rear-left", "bay-rear-left", [-BAY_X, BAY_Y], 15, SPORE_GUN),
        gun_mount("bay-rear-right", "bay-rear-right", [BAY_X, BAY_Y], 15, SPORE_GUN),
        gun_mount(
            "ram",
            "ram",
            [0, -60],
            11,
            {"size": 6, "barrels": 5, "gap": 2.6, "bore": 1, "length": 7},
        ),
        gun_mount(
            "crown",
            "core",
            [0, -13],
            17,
            {"size": 6, "barrels": 5, "gap": 2.6, "bore": 1, "length": 8},
        ),
        gun_mount(
            "hive-rotor",
            "core",
            [0, 6],
            19.6,
            {"size": 5, "barrels": 14, "layout": "ring", "bore": 0.7, "length": 3.4},
        ),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-HIVE-CARRIER-08): the ram fans
    # straight down, the rear bays lob spores in fans of two; the core's fans 12° apart (BOSS-58).
    "stages": stages(
        [
            volley.fan("ram", 2.6, 5, 15, RED, 1.2),
            volley.fan("bay-rear-left", 4, 2, 24, SPORE, 2),
            volley.fan("bay-rear-right", 4, 2, 24, SPORE, 4),
        ],
        [
            [volley.aimed("core", 2.8, 1, 0, ORANGE, 1.5)],
            [volley.aimed("core", 2.6, 3, 12, ORANGE, 0.8)],
            [volley.burst("core", 2.4, 4, 0.14, ORANGE, 0.6)],
            [volley.fan("core", 2.4, 5, 12, ORANGE, 0.6)],
            [
                volley.fan("core", 2.2, 7, 12, ORANGE, 0.6),
                volley.aimed("core", 2.6, 1, 0, RED, 1.2),
            ],
            [
                volley.ring("core", 1.3, 14, 9, ORANGE, 0.4),
                merge(volley.burst("core", 2.8, 3, 0.14, RED, 1), {"mount": "crown"}),
            ],
        ],
    ),
})

# Its armour (FB-HIVE-CARRIER-05): the honeycomb over its side corners (the right one; the left one
# mirrors it), shed first; the honeycomb either side of the queen chamber's front and the one over
# its rear, shed second.
SIDE_COMB = [[38, -16], [56, -16], [65, 0], [56, 16], [38, 16]]
FRONT_COMB = [[5, -42], [22, -42], [22, -33], [15, -21], [5, -21]]
REAR_COMB = [[-12, 19], [12, 19], [12, 42], [-12, 42]]
# The hatch over the hive rotor: a hexagon round its pivot on the queen chamber's top.
HATCH = [[6.5 * math.cos(k * math.pi / 3), 6 + 6.5 * math.sin(k * math.pi / 3)] for k in range(6)]

# Its transformations (D-224, FB-HIVE-CARRIER-10, FB-HIVE-CARRIER-11): once two parts are gone its
# side combs burst off for a pair of mortars; once four are gone its front combs burst off for a
# pair of sweepers and its rear comb for a hangar on its centre line.
HIVE_CARRIER = with_weapons(
    _HIVE_CARRIER,
    [
        hidden_weapon("mortar-left", "mortar", [-48, 0], 10, 700, 1, "orange", 1.2, 10),
        hidden_weapon("mortar-right", "mortar", [48, 0], 10, 700, 1, "orange", 2.0, 10),
        hidden_weapon("sweeper-left", "sweeper", [-13, -32], 7, 880, 2, "orange", 1.4, 10),
        hidden_weapon("sweeper-right", "sweeper", [13, -32], 7, 880, 2, "orange", 4.4, 10),
        hidden_weapon("hangar", "hangar", [0, 30], 10, 880, 2, "orange", 2.2, 10),
    ],
    [
        armour_region("side-combs", 1, SIDE_COMB, "shell"),
        armour_region("front-combs", 2, FRONT_COMB, "shell"),
        armour_region("rear-comb", 2, REAR_COMB, "shell", None, False),
        # The hatch over the hive rotor (BOSS-58): it bursts as the rotor comes into use, in its
        # last stage, and the rotor rises out of it.
        armour_region(
            "rotor-hatch",
            None,
            HATCH,
            "ring",
            None,
            False,
            "hive-rotor",
        ),
    ],
)
