# Copyright (c) 2026 Renaud Guillon
"""The Siege Crawler, the Lab's L-4 final boss (specs/bosses/lab/L-4-siege-crawler.md).

A Lab boss, in the dev viewer only: no level brings it in. Offsets in px from the boss's centre,
X right and Y up (its nose points down, at -Y). 5 destroyable parts (BOSS-13): a heavy cannon
turret on its head shield, two mortars and two missile blocks on its flanks. Heavy artillery: few,
big, slow shells, flak that bursts into rings after a delay, and homing missiles; its bullet hell is
made of their bursts (FB-SIEGE-CRAWLER-08).
"""

import math

from game.config.bosses.boss_guns import gun_mount, missile_mount
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


RED = bullet("red", 180)
ORANGE = bullet("orange", 170)
# Its big, slow shells: the front cannon's and the core's keep gun's.
SHELL = bullet("red", 135, 7)
HEAVY = bullet("orange", 120, 8)
# Its flak: a slow, big shell bursting into a ring of small bullets after a set time.
MORTAR_FLAK = bursting("orange", 100, 8, [1.3, 10, bullet("orange", 150)])
CORE_FLAK = bursting("red", 95, 9, [1.5, 12, bullet("red", 145)])

# The front cannon's turret: three heavy barrels side by side, sweeping its aimed spreads.
CANNON = {"size": 8, "barrels": 3, "gap": 4, "bore": 1.6, "length": 13}
# A mortar's single short, fat barrel in a cradle on a turntable (as the Breakwater's).
MORTAR = {"size": 7.5, "barrels": 1, "bore": 3.8, "length": 4.5, "style": "mortar", "axis": 0.8}

# Where the core's two late guns lie, each under a hatch (BOSS-58).
FLAK_AT = [0, 27]
ROTOR_AT = [0, 10]

# L-4 final: a very wide, flat, low armoured crawler, plated like a tank, rows of legs along its
# flanks (FB-SIEGE-CRAWLER-07).
_SIEGE_CRAWLER = record({
    "id": "siege-crawler",
    # Its points, its core's drop and its parts' drops (FB-SIEGE-CRAWLER-12).
    "stats": stats({
        "id": "siege-crawler",
        "name": "Siege Crawler",
        "size": 4.5,
        "coreRadius": 22,
        "coreHealth": 5200,
        "points": 12000,
        "groundSpeed": 0.35,
        "coreDrop": 1,
        "parts": [
            fpart("mortar-left", [-34, -4], 13, 1450),
            fpart("mortar-right", [34, -4], 13, 1450),
            fpart("missile-left", [-55, 17], 12, 1400),
            fpart("missile-right", [55, 17], 12, 1400),
            fpart("cannon", [0, -30], 15, 1800),
        ],
    }),
    # Where it stops and how it moves in place (FB-SIEGE-CRAWLER-06).
    "stopFraction": 0.75,
    "sway": {"amplitude": 30, "period": 11},
    "bob": {"amplitude": 4, "period": 5},
    "guns": {},
    # It transforms once both mortars are gone, then once both missile blocks are (D-228,
    # FB-SIEGE-CRAWLER-10, FB-SIEGE-CRAWLER-11).
    "transformParts": [["mortar-left", "mortar-right"], ["missile-left", "missile-right"]],
    # Its gun mounts (BOSS-58, FB-SIEGE-CRAWLER-03): the cannon's turret on its head shield, a
    # mortar in each flank cradle, a block of four ports on each rear flank, and the core's: the
    # keep gun on its axial ridge (its shells), a flak mortar on its tail shield and a rotor between
    # them (its last ring), the two late ones under hatches.
    "mounts": [
        gun_mount("mortar-left", "mortar-left", [-34, -4], 7, MORTAR),
        gun_mount("mortar-right", "mortar-right", [34, -4], 7, MORTAR),
        missile_mount("missile-left", "missile-left", [-55, 17], 8, 4),
        missile_mount("missile-right", "missile-right", [55, 17], 8, 4),
        gun_mount("cannon", "cannon", [0, -30], 9, CANNON),
        gun_mount(
            "keep",
            "core",
            [0, -9],
            11,
            {"size": 5.5, "barrels": 2, "gap": 3.6, "bore": 1.4, "length": 9},
        ),
        gun_mount(
            "flak",
            "core",
            FLAK_AT,
            7.2,
            {"size": 5.5, "barrels": 1, "bore": 3.2, "length": 4, "style": "mortar", "axis": 0.8},
        ),
        gun_mount(
            "tail-rotor",
            "core",
            ROTOR_AT,
            9.8,
            {"size": 5, "barrels": 12, "layout": "ring", "bore": 0.9, "length": 3.5},
        ),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-SIEGE-CRAWLER-08). The cannon's
    # spreads are 12° apart; the core's flak leaves its own mortar, its shells the keep gun.
    "stages": stages(
        [
            volley.aimed("cannon", 2.8, 3, 12, SHELL, 1.4),
            volley.aimed("mortar-left", 3.6, 1, 0, MORTAR_FLAK, 1),
            volley.aimed("mortar-right", 3.6, 1, 0, MORTAR_FLAK, 2.8),
            volley.missiles("missile-left", 6.5, 2, 30, 3.5),
            volley.missiles("missile-right", 6.5, 2, 30, 6.75),
        ],
        [
            [volley.aimed("core", 3.2, 1, 0, HEAVY, 2)],
            [merge(volley.aimed("core", 3.4, 1, 0, CORE_FLAK, 1), {"mount": "flak"})],
            [volley.aimed("core", 3, 2, 10, HEAVY, 0.8)],
            [
                merge(volley.aimed("core", 3.2, 1, 0, CORE_FLAK, 1), {"mount": "flak"}),
                volley.burst("core", 3, 3, 0.25, HEAVY, 1.8),
            ],
            [
                merge(volley.aimed("core", 2.6, 1, 0, CORE_FLAK, 0.8), {"mount": "flak"}),
                volley.aimed("core", 2.6, 3, 10, HEAVY, 1.4),
            ],
            [
                volley.ring("core", 1.6, 12, 9, RED, 0.4),
                merge(volley.aimed("core", 3, 1, 0, CORE_FLAK, 1.2), {"mount": "flak"}),
            ],
        ],
    ),
})

# Its middle deck plates' right half (FB-SIEGE-CRAWLER-05): on the thorax's side lobe between the
# axial ridge and the mortar's cradle, the lances under it; mirrored across the centre line.
DECK_PLATES = [[9, -2], [22, -2], [25, 4], [25, 24], [20, 28], [9, 28]]
# Its head shield's right cheek (FB-SIEGE-CRAWLER-05): from the cannon's collar out to the genal
# spine, the racks under it; mirrored.
CHEEK_PLATES = [[18, -18], [38, -18], [58, -22], [64, -30], [50, -36], [30, -40], [18, -36]]


def _hatch(region_id: str, at: list[Any], r: float, mount: str) -> Any:
    """Return an octagonal hatch of radius `r` over the core's mount `mount` at `at` (BOSS-58)."""
    corners = [
        [at[0] + r * math.cos(k * math.pi / 4), at[1] + r * math.sin(k * math.pi / 4)]
        for k in range(8)
    ]
    return armour_region(region_id, None, corners, "ring", None, False, mount)


# Its transformations (D-224; FB-SIEGE-CRAWLER-10, FB-SIEGE-CRAWLER-11): once both mortars are gone
# its middle deck plates burst off for a pair of laser lances; once both missile blocks are gone its
# head shield's cheeks burst off for a pair of missile racks.
SIEGE_CRAWLER = with_weapons(
    _SIEGE_CRAWLER,
    [
        hidden_weapon("lance-left", "lance", [-16, 12], 9, 1440, 1, "red", 1.2, 6.5),
        hidden_weapon("lance-right", "lance", [16, 12], 9, 1440, 1, "red", 2.0, 6.5),
        hidden_weapon("rack-left", "rack", [-42, -28], 9, 1800, 2, "red", 1.2, 6),
        hidden_weapon("rack-right", "rack", [42, -28], 9, 1800, 2, "red", 2.4, 6),
    ],
    [
        armour_region("deck", 1, DECK_PLATES, "shell"),
        armour_region("cheeks", 2, CHEEK_PLATES, "wing"),
        _hatch("rotor-hatch", ROTOR_AT, 6.5, "tail-rotor"),
        _hatch("flak-hatch", FLAK_AT, 7, "flak"),
    ],
)
