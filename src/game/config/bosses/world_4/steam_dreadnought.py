"""P10-R11, 4-1: the Steam Dreadnought, the Black sands' final boss (ported from
`config/bosses/world-4/steam-dreadnought.ts`).

Offsets in px from the boss's centre, X right and Y up (its bow points down the screen, at -Y). The
stage patterns are the agent's design (P07-R04): the parts fire the same while they stand, the core
fires its bow laser at every stage with something new beside it, and its last stage (only the core
left) adds spirals used by no earlier stage. Health tuned with the D-055 bot for P10-R12.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import bullet, cells, mirror, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.record import merge, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


def fpart(part_id: str, at: Any, radius: float, health: float, options: Any = None) -> Any:
    """A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`)."""
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
# smokestacks puffing steam (P10-R11). The smokestacks fire rings of bullets and the two broadside
# turrets aimed bursts; the four shield the core. The missile rack on the stern fires homing
# missiles; the bow fires its laser after a warning line. The ground slows (x0.6).
STEAM_DREADNOUGHT = record(
    {
        "id": "steam-dreadnought",
        # Angry after each destroyed part (D-063), heat 10: World 4 goes on from World 3's 9, up to
        # 14.
        "rage": rage.flower(10, "red", "orange"),
        "stats": stats(
            record(
                {
                    "id": "steam-dreadnought",
                    "name": "Steam Dreadnought",
                    "size": 5,
                    "coreRadius": 18,
                    "coreHealth": 3600,
                    "points": 21000,
                    "groundSpeed": 0.6,
                    "coreDrop": 1,
                    "parts": [
                        fpart("stack-left", [STACK_X, STACK_Y], 10, 850),
                        fpart("stack-right", [-STACK_X, STACK_Y], 10, 850),
                        fpart("turret-left", [TURRET_X, TURRET_Y], 10, 950),
                        fpart("turret-right", [-TURRET_X, TURRET_Y], 10, 950),
                        fpart("rack", list(DREAD_PARTS.rack), 10, 600, {"shields": False}),
                    ],
                }
            )
        ),
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
    }
)
