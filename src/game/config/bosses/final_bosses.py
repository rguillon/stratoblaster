"""The World 1 final bosses (P07-R05)

4 to 6 destroyable parts each. Offsets in px from the boss's centre, X right and Y up (its nose
points down, at -Y). Stage patterns as for the mini bosses (see `mini_bosses.py`); the core of a
final boss always drops a bonus (P07-R07).
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import bullet, cells, mirror, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, slide, swing
from game.config.record import concat, merge, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


def fpart(part_id: str, at: list[Any], radius: float, health: float, options: Any = None) -> Any:
    """A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`)."""
    extra = {} if options == None else options  # noqa: E711
    return part(part_id, at, radius, health, merge({"drop": 0.6}, extra))


RED = bullet("red", 190)
MAGENTA = bullet("magenta", 185)
GREEN = bullet("green", 180)
ORANGE = bullet("orange", 175)
BLUE = bullet("blue", 190)
PURPLE = bullet("purple", 195)

# The guns' muzzles (phase 7 review): the tips of the barrels their models draw, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).

# The Refinery Titan's right rotary turret's three barrels.
ROTARY = [
    [32, -46.6, 18.8],
    [34.2, -46.6, 15.8],
    [29.8, -46.6, 15.8],
]

# 1-1: a seaplane bomber; wing gun pods (they shield the core), a tail missile rack, a belly plate.
_STORM_PETREL = record(
    {
        "id": "storm-petrel",
        # Angry after each destroyed part (phase 7 review).
        "rage": rage.flower(0.5, "magenta", "red"),
        "stats": stats(
            {
                "id": "storm-petrel",
                "name": "Storm Petrel",
                "size": 4.5,
                "coreRadius": 20,
                "coreHealth": 2010,
                "points": 8000,
                "groundSpeed": 1.5,
                "coreDrop": 1,
                "parts": [
                    fpart("pod-left", [-56, 4], 15, 1010),
                    fpart("pod-right", [56, 4], 15, 1010),
                    fpart("missile-rack", [0, 40], 14, 820, {"shields": False}),
                    fpart("belly-plate", [0, -32], 15, 920, {"shields": False}),
                ],
            }
        ),
        "stopFraction": 0.72,
        "sway": {"amplitude": 45, "period": 8},
        "bob": {"amplitude": 10, "period": 4},
        "guns": {
            "core": {"gun": twin(1.6, -19.3, 16.8), "turret": [0, -5]},
            "pod-left": {"gun": twin(-56, -18.8, 14.3, 2.5)},
            "pod-right": {"gun": twin(56, -18.8, 14.3, 2.5)},
            "missile-rack": {"missile": cells([-6.2, 0, 6.2], [36.9, 43.1], 17.3)},
        },
        "stages": stages(
            [
                volley.fan("pod-left", 2, 3, 15, MAGENTA, 0.8),
                volley.fan("pod-right", 2, 3, 15, MAGENTA, 1.8),
                volley.missiles("missile-rack", 5.5, 2, 30, 3),
            ],
            [
                [volley.aimed("core", 3, 1, 0, RED, 1.6)],
                [volley.aimed("core", 2.4, 3, 12, RED, 0.8)],
                [volley.burst("core", 2.4, 4, 0.14, RED, 0.6)],
                [volley.fan("core", 2.2, 7, 12, MAGENTA, 0.6)],
                [volley.ring("core", 1.5, 12, 8, RED, 0.4)],
            ],
        ),
    }
)

# 1-2: a wide carrier; two hangar bays launch Gnats, two flak turrets; all four shield the core.
_GULL_MOTHERSHIP = record(
    {
        "id": "gull-mothership",
        # Angry after each destroyed part (phase 7 review).
        "rage": rage.vortex(1.5, "green", "orange"),
        "stats": stats(
            {
                "id": "gull-mothership",
                "name": "Gull Mothership",
                "size": 5,
                "coreRadius": 20,
                "coreHealth": 2280,
                "points": 9000,
                "groundSpeed": 0.6,
                "coreDrop": 1,
                "parts": [
                    fpart("hangar-left", [-62, 6], 18, 1050),
                    fpart("hangar-right", [62, 6], 18, 1050),
                    fpart("flak-left", [-28, -32], 12, 790),
                    fpart("flak-right", [28, -32], 12, 790),
                ],
            }
        ),
        "stopFraction": 0.74,
        "sway": {"amplitude": 40, "period": 9},
        "bob": {"amplitude": 8, "period": 4.5},
        "launches": [
            {"from": "hangar-left", "kind": "gnats", "count": 3, "every": 7, "first": 2.5},
            {"from": "hangar-right", "kind": "gnats", "count": 3, "every": 7, "first": 6},
        ],
        "guns": {
            "core": {"gun": [[0, -69.9, 7]], "laser": [[0, -69.9, 7]]},
            "flak-left": {"gun": twin(-28, -46.3, 8.8, 1.6), "turret": [-28, -32]},
            "flak-right": {"gun": twin(28, -46.3, 8.8, 1.6), "turret": [28, -32]},
        },
        "stages": stages(
            [
                volley.aimed("flak-left", 1.9, 2, 8, GREEN, 0.9),
                volley.aimed("flak-right", 1.9, 2, 8, GREEN, 1.85),
            ],
            [
                [volley.laser("core", 7, 1.5, 4)],
                [volley.laser("core", 6, 1.5, 2), volley.aimed("core", 2.6, 1, 0, ORANGE, 1)],
                [volley.laser("core", 5.5, 1.5, 2), volley.fan("core", 2.6, 5, 14, ORANGE, 1)],
                [volley.laser("core", 5, 1.5, 2), volley.ring("core", 2.2, 8, 0, ORANGE, 1)],
                [volley.laser("core", 4.5, 1.6, 1.5), volley.ring("core", 1.5, 12, 9, GREEN, 0.4)],
            ],
        ),
    }
)

# 1-3: a flying fortress; two laser lances and two missile silos shield the core.
_MESA_FORTRESS = record(
    {
        "id": "mesa-fortress",
        # Angry after each destroyed part (phase 7 review).
        "rage": rage.curtain(2.5, "red", "orange"),
        "stats": stats(
            {
                "id": "mesa-fortress",
                "name": "Mesa Fortress",
                "size": 5,
                "coreRadius": 22,
                "coreHealth": 3000,
                "points": 10000,
                "groundSpeed": 0,
                "coreDrop": 1,
                "parts": [
                    fpart("lance-left", [-58, -12], 15, 1050),
                    fpart("lance-right", [58, -12], 15, 1050),
                    fpart("silo-left", [-28, 32], 13, 1500),
                    fpart("silo-right", [28, 32], 13, 1500),
                ],
            }
        ),
        "stopFraction": 0.74,
        "sway": {"amplitude": 35, "period": 10},
        "bob": {"amplitude": 6, "period": 5},
        "guns": {
            "core": {
                "gun": [
                    [8, -42.7, 17.6],
                    [4.1, -44.4, 17.6],
                    [0, -45, 17.6],
                    [-4.1, -44.4, 17.6],
                    [-8, -42.7, 17.6],
                ],
                "turret": [0, -30],
            },
            "lance-left": {"laser": [[-58, -51.3, 6]]},
            "lance-right": {"laser": [[58, -51.3, 6]]},
            "silo-left": {"missile": cells([-30.8, -25.2], [29.2, 34.8], 17.3)},
            "silo-right": {"missile": cells([25.2, 30.8], [29.2, 34.8], 17.3)},
        },
        "stages": stages(
            [
                volley.laser("lance-left", 6, 1.4, 2),
                volley.laser("lance-right", 6, 1.4, 5),
                volley.missiles("silo-left", 5, 1, 0, 3.5),
                volley.missiles("silo-right", 5, 1, 0, 6),
            ],
            [
                [volley.fan("core", 3, 3, 16, RED, 1.5)],
                [volley.fan("core", 2.6, 5, 14, RED, 0.8)],
                [
                    volley.fan("core", 2.6, 5, 14, RED, 0.8),
                    volley.aimed("core", 2.2, 1, 0, ORANGE, 1.4),
                ],
                [volley.fan("core", 2.2, 7, 12, RED, 0.6)],
                [
                    volley.ring("core", 1.5, 14, 12, ORANGE, 0.4),
                    volley.fan("core", 2.6, 5, 14, RED, 1.2),
                ],
            ],
        ),
    }
)

# 1-4: a heavy tanker-gunship; fuel tanks burst into bullet rings, rotary turrets spiral.
_REFINERY_TITAN = record(
    {
        "id": "refinery-titan",
        # Angry after each destroyed part (phase 7 review).
        "rage": rage.spirals(3.5, "orange", "green"),
        "stats": stats(
            {
                "id": "refinery-titan",
                "name": "Refinery Titan",
                "size": 5.5,
                "coreRadius": 22,
                "coreHealth": 4740,
                "points": 12000,
                "groundSpeed": 0.3,
                "coreDrop": 1,
                "parts": [
                    fpart("tank-left", [-66, 18], 17, 1400, {"shields": False}),
                    fpart("tank-right", [66, 18], 17, 1400, {"shields": False}),
                    fpart("turret-left", [-32, -24], 14, 1810),
                    fpart("turret-right", [32, -24], 14, 1810),
                    fpart("missile-battery", [0, 38], 14, 1530, {"shields": False}),
                ],
            }
        ),
        "stopFraction": 0.74,
        "sway": {"amplitude": 30, "period": 10},
        "bob": {"amplitude": 6, "period": 5},
        "breakRings": {
            "tank-left": {"count": 12, "bullet": ORANGE},
            "tank-right": {"count": 12, "bullet": ORANGE},
        },
        "guns": {
            "core": {"gun": twin(4.5, -35.8, 19)},
            "turret-left": {"gun": mirror(ROTARY), "turret": [-32, -24]},
            "turret-right": {"gun": ROTARY, "turret": [32, -24]},
            "missile-battery": {"missile": cells([-5.5, 5.5], [30.5, 38, 45.5], 21.1)},
        },
        "stages": stages(
            [
                volley.ring("turret-left", 0.7, 3, 19, ORANGE, 0.5),
                volley.ring("turret-right", 0.7, 3, -19, ORANGE, 0.85),
                volley.missiles("missile-battery", 5.5, 2, 30, 3),
            ],
            [
                [volley.aimed("core", 3, 1, 0, BLUE, 1.6)],
                [volley.aimed("core", 2.6, 3, 12, BLUE, 0.8)],
                [volley.burst("core", 2.4, 4, 0.14, BLUE, 0.6)],
                [volley.fan("core", 2.4, 5, 14, BLUE, 0.6)],
                [
                    volley.fan("core", 2.2, 7, 12, BLUE, 0.6),
                    volley.aimed("core", 2.6, 1, 0, ORANGE, 1.2),
                ],
                [
                    volley.ring("core", 1.3, 14, 9, BLUE, 0.4),
                    volley.burst("core", 2.8, 3, 0.14, ORANGE, 1),
                ],
            ],
        ),
    }
)

# 1-5: a city-ship; wing lasers, missile batteries, and two shield generators guard the core.
_OVERLORD = record(
    {
        "id": "overlord",
        # Angry after each destroyed part (phase 7 review).
        "rage": concat(
            rage.spirals(4.5, "purple", "blue", 0.6), rage.flower(4.5, "magenta", "purple", 0.4)
        ),
        "stats": stats(
            {
                "id": "overlord",
                "name": "Overlord",
                "size": 6,
                "coreRadius": 24,
                "coreHealth": 5540,
                "points": 15000,
                "groundSpeed": 0.25,
                "coreDrop": 1,
                "parts": [
                    fpart("laser-left", [-78, -6], 15, 1660, {"shields": False}),
                    fpart("laser-right", [78, -6], 15, 1660, {"shields": False}),
                    fpart("battery-left", [-46, 30], 14, 1520, {"shields": False}),
                    fpart("battery-right", [46, 30], 14, 1520, {"shields": False}),
                    fpart("generator-left", [-34, -36], 13, 1940),
                    fpart("generator-right", [34, -36], 13, 1940),
                ],
            }
        ),
        "stopFraction": 0.75,
        "sway": {"amplitude": 25, "period": 11},
        "bob": {"amplitude": 6, "period": 5},
        "guns": {
            "core": {
                "gun": twin(7, -39.6, 15.5),
                "ring": [[0, 0, 33.6]],
                "laser": [[0, -38, 14.5]],
                "missile": cells([-6, 6], [30, 38], 10.1),
            },
            "laser-left": {"laser": [[-78, -34.6, 4]]},
            "laser-right": {"laser": [[78, -34.6, 4]]},
            "battery-left": {"missile": cells([-51, -41], [22.5, 30, 37.5], 14.1)},
            "battery-right": {"missile": cells([41, 51], [22.5, 30, 37.5], 14.1)},
        },
        "stages": stages(
            [
                volley.laser("laser-left", 6.5, 1.4, 2),
                volley.laser("laser-right", 6.5, 1.4, 5.25),
                volley.missiles("battery-left", 5.5, 2, 24, 3.5),
                volley.missiles("battery-right", 5.5, 2, 24, 6.25),
            ],
            [
                [volley.aimed("core", 2.8, 1, 0, PURPLE, 1.4)],
                [volley.aimed("core", 2.4, 3, 12, PURPLE, 0.8)],
                [volley.burst("core", 2.4, 4, 0.13, PURPLE, 0.6)],
                [volley.fan("core", 2.4, 5, 14, PURPLE, 0.6)],
                [volley.ring("core", 2, 10, 6, PURPLE, 0.6)],
                [
                    volley.fan("core", 2.2, 7, 12, PURPLE, 0.6),
                    volley.burst("core", 2.6, 3, 0.13, RED, 1),
                ],
                [
                    volley.ring("core", 1.2, 14, 9, PURPLE, 0.4),
                    volley.laser("core", 5, 1.4, 2),
                    volley.missiles("core", 6, 2, 30, 3),
                ],
            ],
        ),
    }
)

# Its transformations (D-230): once both wing pods are gone its outer wings swing 30 degrees
# forward about their leading edges' roots, a gun battery riding each; once its rack and plate are
# gone its tail plating bursts off for a heavy cannon and its wing roots' for a pair of sweepers.
STORM_PETREL = with_weapons(
    merge(
        _STORM_PETREL,
        {"transformParts": [["pod-left", "pod-right"], ["missile-rack", "belly-plate"]]},
    ),
    [
        hidden_weapon("battery-left", "battery", [-52, -13], 8, 810, 1, "magenta", 1.2, 13),
        hidden_weapon("battery-right", "battery", [52, -13], 8, 810, 1, "magenta", 2.0, 13),
        hidden_weapon("cannon", "cannon", [0, 32], 11, 1010, 2, "red", 1.4, 14.5),
        hidden_weapon("sweeper-left", "sweeper", [-19, -12], 6, 1010, 2, "magenta", 2.2, 12.9),
        hidden_weapon("sweeper-right", "sweeper", [19, -12], 6, 1010, 2, "magenta", 4.6, 12.9),
    ],
    concat(
        moving_region(
            "outer-wings",
            1,
            [[31, -24], [84, -24], [84, 20], [31, 20]],
            swing([31, -13.4, 8], "up", [0, -30]),
            None,
            [4, 1000],
        ),
        [
            armour_region(
                "tail", 2, [[-14, 18], [14, 18], [14, 48], [-14, 48]], "shell", [9, 1000], False
            ),
            armour_region(
                "wing-roots", 2, [[13, -24], [26, -24], [26, 2], [13, 2]], "wing", [4.6, 1000]
            ),
        ],
    ),
)

# Its hidden weapons (boss transformations, D-224): at transformation 1 its flank armour bursts off,
# baring a dark metal frame, and a pair of laser lances unfold; at transformation 2 its wing armour
# bursts off, baring a dark metal frame, and a pair of ring emitters unfold.
GULL_MOTHERSHIP = with_weapons(
    _GULL_MOTHERSHIP,
    [
        hidden_weapon("pike-left", "lance", [-35, 23], 9, 840, 1, "green", 1.2, 9.6),
        hidden_weapon("pike-right", "lance", [35, 23], 9, 840, 1, "green", 2.0, 9.6),
        hidden_weapon("orb-left", "orb", [-37, -9], 7, 1050, 2, "green", 1.2, 7.6),
        hidden_weapon("orb-right", "orb", [37, -9], 7, 1050, 2, "green", 2.0, 7.6),
    ],
    [
        armour_region("flanks", 1, [[18, 6], [49, 6], [49, 54], [18, 54]], "wing", [1.9, 1000]),
        armour_region("wings", 2, [[22, -38], [49, -38], [49, 6], [22, 6]], "wing", [-0.3, 1000]),
    ],
)

# Its transformations (D-230): once both lances are gone its wing fronts burst off for a pair of
# gun batteries; once both silos are gone its keep splits along its ridge, the two halves of its
# roof sliding apart over a dark metal lattice as a heavy cannon rises between them, and its flank
# armour bursts off for a pair of sweepers.
MESA_FORTRESS = with_weapons(
    merge(
        _MESA_FORTRESS,
        {"transformParts": [["lance-left", "lance-right"], ["silo-left", "silo-right"]]},
    ),
    [
        hidden_weapon("battery-left", "battery", [-44, -26], 10, 1200, 1, "red", 1.2, 14),
        hidden_weapon("battery-right", "battery", [44, -26], 10, 1200, 1, "red", 2.2, 14),
        hidden_weapon("cannon", "cannon", [0, 14], 14, 1500, 2, "orange", 1.4, 22),
        hidden_weapon("sweeper-left", "sweeper", [-60, 22], 8, 1500, 2, "red", 2.4, 14),
        hidden_weapon("sweeper-right", "sweeper", [60, 22], 8, 1500, 2, "red", 6.4, 14),
    ],
    concat(
        [
            armour_region(
                "wings", 1, [[16, -51], [88, -51], [88, -3.5], [16, -3.5]], "wing", [4.3, 1000]
            ),
        ],
        moving_region(
            "roof",
            2,
            [[0, -6], [23, -6], [23, 46], [0, 46]],
            slide([[0, 0, 0], [16, 0, 0]]),
            "shell",
            [16, 1000],
        ),
        [
            armour_region(
                "flanks", 2, [[34, -3.5], [88, -3.5], [88, 50], [34, 50]], "wing", [2.2, 1000]
            ),
        ],
    ),
)

# Its hidden weapons (boss transformations, D-224): at transformation 1 its back plating bursts off,
# baring a dark metal frame, and a pair of gatling turrets unfold; at transformation 2 its spine
# plating bursts off, baring a dark metal frame, and a pair of ring emitters unfold.
REFINERY_TITAN = with_weapons(
    _REFINERY_TITAN,
    [
        hidden_weapon("gatling-left", "gatling", [-9, -13], 7, 1450, 1, "orange", 1.2, 25.7),
        hidden_weapon("gatling-right", "gatling", [9, -13], 7, 1450, 1, "orange", 2.0, 25.7),
        hidden_weapon("orb-left", "orb", [-9, -35], 7, 1810, 2, "orange", 1.2, 18.9),
        hidden_weapon("orb-right", "orb", [9, -35], 7, 1810, 2, "orange", 2.0, 18.9),
    ],
    [
        armour_region(
            "back", 1, [[-24, -24], [24, -24], [24, 14], [-24, 14]], "shell", [7.3, 1000], False
        ),
        armour_region(
            "spine", 2, [[-24, -62], [24, -62], [24, -24], [-24, -24]], "shell", [4.3, 1000], False
        ),
    ],
)

# Its hidden weapons (boss transformations, D-224): at transformation 1 its flank armour bursts off,
# baring a dark metal frame, and a pair of laser lances unfold; at transformation 2 its spine
# plating bursts off, baring a dark metal frame, and a pair of flak mortars unfold.
OVERLORD = with_weapons(
    _OVERLORD,
    [
        hidden_weapon("pike-left", "lance", [-47, -1], 11, 1550, 1, "purple", 1.2, 41.1),
        hidden_weapon("pike-right", "lance", [47, -1], 11, 1550, 1, "purple", 2.0, 41.1),
        hidden_weapon("mortar-left", "mortar", [-13, -55], 11, 1940, 2, "purple", 1.2, 14.1),
        hidden_weapon("mortar-right", "mortar", [13, -55], 11, 1940, 2, "purple", 2.0, 14.1),
    ],
    [
        armour_region(
            "flanks", 1, [[32, -34], [106, -34], [106, 32], [32, 32]], "wing", [15.2, 1000]
        ),
        armour_region(
            "spine", 2, [[-32, -66], [32, -66], [32, -24], [-32, -24]], "shell", [2.8, 1000], False
        ),
    ],
)
