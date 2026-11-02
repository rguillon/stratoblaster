# Copyright (c) 2026 Renaud Guillon
"""The Boreal Citadel (2-5's final boss, specs/bosses/final/2-5-boreal-citadel.md).

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y). Stage
patterns as for the World 1 final bosses (`final_bosses.py`, FB-BOREAL-CITADEL-13): its parts fire
the same while they stand, its core fires every kind of attack, a new one at each stage, and all of
them at once with a spiral of its own, used by no earlier stage, once it stands alone. Its core
always drops a bonus (FB-BOREAL-CITADEL-17).
"""

from game.config.bosses.boss_kit import bullet, cells, mirror, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, swing
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


def fpart(part_id: str, at: list[Any], radius: float, health: float, options: Any = None) -> Any:
    """Return a final boss's part.

    Drops a bonus 60 % of the time (FB-BOREAL-CITADEL-17, `part_drop_chance`).
    """
    extra = {} if options == None else options
    return part(part_id, at, radius, health, merge({"drop": 0.6}, extra))


GREEN = bullet("green", 185)
PURPLE = bullet("purple", 195)
MAGENTA = bullet("magenta", 190)

# Where its parts stand (FB-BOREAL-CITADEL-10, FB-BOREAL-CITADEL-11, FB-BOREAL-CITADEL-12): aurora
# cannons on the outriggers, batteries aft, domes ahead.
BOREAL_PARTS = record({
    "cannon": [80, -8],
    "battery": [48, 34],
    "dome": [36, -40],
})

# The guns' muzzles (phase 7 review, FB-BOREAL-CITADEL-04): the tips of the barrels its model
# draws, from the boss's centre, X right, Y up, and height above the playfield (see
# `BossDesign.guns`).

# The right aurora cannon's lens, at the front of its long barrel.
BOREAL_CANNON = [[80, -40, 7]]
# The right missile battery's six cells, 2 columns by 3 rows.
BOREAL_BATTERY = cells([43, 53], [26, 34, 42], 15.1)
# The core's twin cannons on the keep's gun deck.
BOREAL_GUNS = twin(7, -46.4, 17)
# The core's ring emitter, on the keep's spire.
BOREAL_SPIRE = [0, 0, 45]
# The core's laser lens, between its twin cannons.
BOREAL_LENS = [0, -48, 15]
# The core's missile hatches, behind the keep.
BOREAL_HATCHES = cells([-6, 6], [32, 40], 12.1)

cx = BOREAL_PARTS.cannon[0]
cy = BOREAL_PARTS.cannon[1]
bx = BOREAL_PARTS.battery[0]
by = BOREAL_PARTS.battery[1]
dx = BOREAL_PARTS.dome[0]
dy = BOREAL_PARTS.dome[1]

# 2-5: the polar city's flying fortress; two aurora cannons on turrets aim lasers, two missile
# batteries, and two heated dome generators shield the core, which fires every kind of attack.
_BOREAL_CITADEL = record({
    "id": "boreal-citadel",
    # Angry after each destroyed part (phase 7 review, FB-BOREAL-CITADEL-14): the hottest
    # bullet hell so far.
    "rage": concat(
        rage.curtain(7, "green", "purple", 0.5), rage.spirals(7, "purple", "magenta", 0.5)
    ),
    "stats": stats({
        "id": "boreal-citadel",
        "name": "Boreal Citadel",
        "size": 6,
        "coreRadius": 24,
        "coreHealth": 6000,
        "points": 18000,
        "groundSpeed": 0.25,
        "coreDrop": 1,
        "parts": [
            fpart("cannon-left", [-cx, cy], 15, 1900, {"shields": False}),
            fpart("cannon-right", [cx, cy], 15, 1900, {"shields": False}),
            fpart("dome-left", [-dx, dy], 13, 2150),
            fpart("dome-right", [dx, dy], 13, 2150),
            fpart("battery-left", [-bx, by], 14, 1700, {"shields": False}),
            fpart("battery-right", [bx, by], 14, 1700, {"shields": False}),
        ],
    }),
    # Where it stops and how it moves in place (FB-BOREAL-CITADEL-09).
    "stopFraction": 0.75,
    "sway": {"amplitude": 25, "period": 11},
    "bob": {"amplitude": 6, "period": 5},
    "guns": {
        "core": {
            "gun": BOREAL_GUNS,
            "ring": [BOREAL_SPIRE],
            "laser": [BOREAL_LENS],
            "missile": BOREAL_HATCHES,
        },
        "cannon-left": {
            "laser": mirror(BOREAL_CANNON),
            "turret": [-cx, cy],
            "turretLaser": True,
        },
        "cannon-right": {"laser": BOREAL_CANNON, "turret": [cx, cy], "turretLaser": True},
        "battery-left": {"missile": mirror(BOREAL_BATTERY)},
        "battery-right": {"missile": BOREAL_BATTERY},
    },
    # The parts' volleys, then the core's pattern per stage (FB-BOREAL-CITADEL-13).
    "stages": stages(
        [
            volley.laser("cannon-left", 6.5, 1.6, 2),
            volley.laser("cannon-right", 6.5, 1.6, 5.25),
            volley.missiles("battery-left", 5.5, 2, 24, 3.5),
            volley.missiles("battery-right", 5.5, 2, 24, 6.25),
        ],
        [
            [volley.aimed("core", 2.6, 3, 10, PURPLE, 1.4)],
            [volley.fan("core", 2.4, 5, 14, GREEN, 0.8)],
            [volley.burst("core", 2.3, 4, 0.12, PURPLE, 0.6)],
            [
                volley.missiles("core", 5, 2, 30, 1.5),
                volley.aimed("core", 2.2, 1, 0, MAGENTA, 1),
            ],
            [volley.laser("core", 5.5, 1.4, 1.5), volley.fan("core", 2.4, 7, 12, GREEN, 0.6)],
            [
                volley.ring("core", 2, 10, 0, GREEN, 0.6),
                volley.burst("core", 2.6, 3, 0.12, MAGENTA, 1),
            ],
            [
                volley.ring("core", 1.2, 16, 9, PURPLE, 0.4),
                volley.laser("core", 5, 1.4, 2),
                volley.missiles("core", 6, 2, 30, 3),
                volley.fan("core", 2.8, 5, 14, GREEN, 1.4),
            ],
        ],
    ),
})

# Its transformations (D-230): once both domes are gone its bow doors swing open sideways on their
# rear hinges, showing a drone hangar and two mortars in the dark metal of its hold
# (FB-BOREAL-CITADEL-15); once both batteries are gone its wing armour bursts off for a pair of
# heavy cannons (FB-BOREAL-CITADEL-16). Its change of shape: FB-BOREAL-CITADEL-08.
BOREAL_CITADEL = with_weapons(
    merge(
        _BOREAL_CITADEL,
        {"transformParts": [["dome-left", "dome-right"], ["battery-left", "battery-right"]]},
    ),
    [
        hidden_weapon("hangar", "hangar", [0, -68], 13, 1720, 1, "green", 3.0, 9),
        hidden_weapon("mortar-left", "mortar", [-20, -48], 8, 1720, 1, "green", 1.2, 11),
        hidden_weapon("mortar-right", "mortar", [20, -48], 8, 1720, 1, "green", 2.8, 11),
        hidden_weapon("heavy-left", "cannon", [-47, -7], 12, 2150, 2, "green", 1.2, 16.4),
        hidden_weapon("heavy-right", "cannon", [47, -7], 12, 2150, 2, "green", 2.0, 16.4),
    ],
    concat(
        moving_region(
            "bow-doors",
            1,
            [[0, -90], [32, -90], [32, -40], [0, -40]],
            swing([32, -40, 10], "up", [0, 75]),
            "shell",
            [4, 1000],
        ),
        [
            armour_region(
                "wings", 2, [[32, -40], [102, -40], [102, 26], [32, 26]], "wing", [8.0, 1000]
            ),
        ],
    ),
)
