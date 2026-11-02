# Copyright (c) 2026 Renaud Guillon
"""4-1: the Steam Dreadnought, the Black sands' final boss.

Specified in specs/bosses/final/4-1-steam-dreadnought.md.

Offsets in px from the boss's centre, X right and Y up (its bow points down the screen, at -Y). The
stage patterns are the agent's design (FB-STEAM-DREADNOUGHT-12): the parts fire the same while they
stand, the core fires its bow laser at every stage with something new beside it, and its last stage
(only the core left) adds spirals used by no earlier stage. Health (FB-STEAM-DREADNOUGHT-08) tuned
with the D-055 bot for WLD-4-22.
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


def fpart(part_id: str, at: Any, radius: float, health: float, options: Any = None) -> Any:
    """Return a final boss's part (FB-STEAM-DREADNOUGHT-19).

    It drops a bonus 60 % of the time (`part_drop_chance`).
    """
    return part(part_id, at, radius, health, merge({"drop": 0.6}, options))


RED = bullet("red", 205)
ORANGE = bullet("orange", 195)
MAGENTA = bullet("magenta", 210)
PURPLE = bullet("purple", 200)
BLUE = bullet("blue", 200)

# Where the parts sit (the left ones, at -X; the right ones mirror them).
DREAD_PARTS = record({"stack": [-30, 16], "turret": [-56, -20], "rack": [0, 54]})

# Heights of its decks and of the smokestacks' mouths (model units over the playfield).
DREAD_HEIGHTS = record({"deck": 9, "stack": 34, "rack": 15})

# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).

# The left smokestack's mouth: its rings pour out of it with the steam.
DREAD_STACK = [[DREAD_PARTS.stack[0], DREAD_PARTS.stack[1], DREAD_HEIGHTS.stack]]
# The left broadside turret's twin barrels, at rest (pointing down the screen).
DREAD_TURRET_GUNS = twin(DREAD_PARTS.turret[0], -37, 12.5, 2.4)
# The missile rack's cells, two by two, on the stern.
DREAD_RACK = cells([-5, 5], [49, 59], DREAD_HEIGHTS.rack)
# The bow laser's lens, at the stem.
DREAD_LENS = [[0, -87, 6]]
# The twin guns either side of the bow (the core's aimed shots and fans).
DREAD_BOW_GUNS = twin(9, -70, 11)
# The beacon on top of the bridge tower (the core's rings and spirals).
DREAD_BEACON = [[0, -7, 38]]

STACK_X = DREAD_PARTS.stack[0]
STACK_Y = DREAD_PARTS.stack[1]
TURRET_X = DREAD_PARTS.turret[0]
TURRET_Y = DREAD_PARTS.turret[1]

# 4-1: a flying battleship 5 L long, soot-black armour with red neon and glowing seams, two
# smokestacks puffing steam (FB-STEAM-DREADNOUGHT-01). The smokestacks fire rings of bullets and
# the two broadside turrets aimed bursts; the four shield the core. The missile rack on the stern
# fires homing missiles; the bow fires its laser after a warning line. The ground slows (x0.6).
_STEAM_DREADNOUGHT = record({
    "id": "steam-dreadnought",
    # Angry after each destroyed part (D-063, FB-STEAM-DREADNOUGHT-14), heat 10: World 4 goes
    # on from World 3's 9, up to 14.
    "rage": rage.flower(10, "red", "orange"),
    # Its core and parts, their health, and its points (FB-STEAM-DREADNOUGHT-08).
    "stats": stats(
        record({
            "id": "steam-dreadnought",
            "name": "Steam Dreadnought",
            "size": 5,
            "coreRadius": 18,
            "coreHealth": 3600,
            "points": 21000,
            "groundSpeed": 0.6,
            "coreDrop": 1,
            "parts": [
                fpart("turret-left", [TURRET_X, TURRET_Y], 10, 950),
                fpart("turret-right", [-TURRET_X, TURRET_Y], 10, 950),
                fpart("stack-left", [STACK_X, STACK_Y], 10, 850),
                fpart("stack-right", [-STACK_X, STACK_Y], 10, 850),
                fpart("rack", list(DREAD_PARTS.rack), 10, 600, {"shields": False}),
            ],
        })
    ),
    # Where it stops and how it moves in place (FB-STEAM-DREADNOUGHT-07).
    "stopFraction": 0.74,
    "sway": {"amplitude": 40, "period": 10},
    "bob": {"amplitude": 5, "period": 5},
    "guns": {
        "core": {"gun": DREAD_BOW_GUNS, "laser": DREAD_LENS, "ring": DREAD_BEACON},
        "stack-left": {"gun": DREAD_STACK},
        "stack-right": {"gun": mirror(DREAD_STACK)},
        "turret-left": {"gun": DREAD_TURRET_GUNS, "turret": [TURRET_X, TURRET_Y]},
        "turret-right": {"gun": mirror(DREAD_TURRET_GUNS), "turret": [-TURRET_X, TURRET_Y]},
        "rack": {"missile": DREAD_RACK},
    },
    # In every stage the stacks' rings (FB-STEAM-DREADNOUGHT-09), the turrets' bursts
    # (FB-STEAM-DREADNOUGHT-10) and the rack's missiles (FB-STEAM-DREADNOUGHT-11); then the
    # core's laser and pattern per stage (FB-STEAM-DREADNOUGHT-12).
    "stages": stages(
        [
            volley.ring("stack-left", 3.6, 10, 9, ORANGE, 1.2),
            volley.ring("stack-right", 3.6, 10, -9, ORANGE, 3),
            volley.burst("turret-left", 3.2, 4, 0.12, RED, 0.8),
            volley.burst("turret-right", 3.2, 4, 0.12, RED, 2.4),
            volley.missiles("rack", 6.5, 2, 30, 3.5),
        ],
        [
            [volley.laser("core", 7, 1.5, 4)],
            [
                volley.laser("core", 6.5, 1.5, 2),
                volley.aimed("core", 2.8, 3, 12, MAGENTA, 1),
            ],
            [
                volley.laser("core", 6.5, 1.5, 2),
                volley.fan("core", 2.6, 5, 14, MAGENTA, 0.8),
            ],
            [
                volley.laser("core", 6, 1.6, 2),
                volley.ring("core", 2.4, 12, 11, PURPLE, 0.7),
            ],
            [
                volley.laser("core", 5.5, 1.6, 2),
                volley.fan("core", 2.4, 7, 12, MAGENTA, 0.6),
                volley.aimed("core", 2.4, 1, 0, RED, 1.8),
            ],
            # Alone: two spirals turning opposite ways from the bridge, under the laser.
            [
                volley.laser("core", 5, 1.6, 1.5),
                volley.ring("core", 0.5, 4, 19, BLUE, 0.4),
                volley.ring("core", 0.5, 4, -23, PURPLE, 0.65),
            ],
        ],
    ),
})

# Its transformations (D-230): once both its turrets are gone its front side decks fan out forward
# on hinges at their bows (FB-STEAM-DREADNOUGHT-15), a gun battery riding each
# (FB-STEAM-DREADNOUGHT-16), dark metal showing in the wedges they open; once both its stacks are
# gone its stern and spine plating burst off (FB-STEAM-DREADNOUGHT-17) for two mortars and a ring
# emitter (FB-STEAM-DREADNOUGHT-18).
STEAM_DREADNOUGHT = with_weapons(
    merge(
        _STEAM_DREADNOUGHT,
        {"transformParts": [["turret-left", "turret-right"], ["stack-left", "stack-right"]]},
    ),
    [
        hidden_weapon("battery-left", "battery", [-57, -45], 9, 760, 1, "red", 1.2, 16),
        hidden_weapon("battery-right", "battery", [57, -45], 9, 760, 1, "red", 2.0, 16),
        hidden_weapon("mortar-left", "mortar", [-30, 47], 8, 950, 2, "orange", 1.2, 12.6),
        hidden_weapon("mortar-right", "mortar", [30, 47], 8, 950, 2, "orange", 2.6, 12.6),
        hidden_weapon("orb", "orb", [0, 29], 11, 950, 2, "red", 1.6, 15.6),
    ],
    concat(
        moving_region(
            "decks",
            1,
            [[20, -54], [74, -54], [74, 2], [20, 2]],
            swing([20, -54, 0], "up", [0, -25]),
            "wing",
            [-8, 1000],
        ),
        [
            armour_region(
                "flanks", 2, [[18, 17], [72, 17], [72, 77], [18, 77]], "wing", [2.1, 1000]
            ),
            armour_region(
                "spine", 2, [[-18, 1], [18, 1], [18, 57], [-18, 57]], "shell", [6.4, 1000], False
            ),
        ],
    ),
)
