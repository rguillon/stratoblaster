"""P10-R11, 4-5's final boss: the Caldera Throne, World 4's last boss and the hardest of the game
so far (ported from `config/bosses/world-4/caldera-throne.ts`).

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y). Stage
patterns as for the earlier final bosses (P07-R04, D-055): its parts fire the same while they
stand, its core fires every kind of attack, a new one at each stage (magma bombs bursting into rings
among them), and all of them at once with a spiral of its own, used by no earlier stage, once it
stands alone. Its core always drops a bonus (P07-R07).
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import (
    bullet,
    bursting,
    cells,
    mirror,
    part,
    stages,
    stats,
    twin,
    volley,
)
from game.config.bosses.boss_rage import rage
from game.config.record import concat, merge, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


def fpart(part_id: str, at: Any, radius: float, health: float, options: Any = None) -> Any:
    """A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`)."""
    return part(part_id, at, radius, health, merge({"drop": 0.6}, options))


MAGENTA = bullet("magenta", 215)
BLUE = bullet("blue", 210)
PURPLE = bullet("purple", 205)
# A slow, big magma bomb that bursts into a ring of small bullets on its way down.
MAGMA_BOMB = bursting("magenta", 115, 7, [1.05, 9, bullet("blue", 195)])

# Where its parts stand (P10-R11): magma cannons on the side bastions, missile batteries aft,
# heat shield generators ahead of the keep.
CALDERA_PARTS = record({"magma": [88, -8], "battery": [56, 46], "shield": [34, -52]})

# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), turrets at rest.

# The right magma cannon's lens, at the front of its long barrel.
CALDERA_MAGMA = [[CALDERA_PARTS.magma[0], -46, 10]]
# The right missile battery's six cells, 2 columns by 3 rows.
CALDERA_CELLS = cells([50, 62], [36, 46, 56], 15.1)
# The core's twin cannons on the prow.
CALDERA_GUNS = twin(10, -104, 10)
# The core's laser lens, on the prow between its twin cannons.
CALDERA_LENS = [0, -108, 9]
# The core's ring emitter, the crown on top of the throne's keep.
CALDERA_CROWN = [0, 4, 50]
# The core's missile hatches, on the deck behind the keep.
CALDERA_HATCHES = cells([-8, 8], [58, 68], 10.1)

MX = CALDERA_PARTS.magma[0]
MY = CALDERA_PARTS.magma[1]
BX = CALDERA_PARTS.battery[0]
BY = CALDERA_PARTS.battery[1]
SX = CALDERA_PARTS.shield[0]
SY = CALDERA_PARTS.shield[1]

# 4-5: the enemy's war fortress rising from the magma lake, crimson and gold neon over its whole
# hull; two magma cannons on turrets aim lasers, two missile batteries fire homing missiles, two
# heat shield generators shield the core, which fires every kind of attack. The ground stops over
# the magma lake (x0).
CALDERA_THRONE = record(
    {
        "id": "caldera-throne",
        # Angry after each destroyed part (phase 7 review): the hottest bullet hell of the game.
        "rage": concat(
            rage.spirals(14, "magenta", "purple", 0.5), rage.vortex(14, "blue", "magenta", 0.5)
        ),
        "stats": stats(
            record(
                {
                    "id": "caldera-throne",
                    "name": "Caldera Throne",
                    "size": 6.5,
                    "coreRadius": 28,
                    "coreHealth": 7400,
                    "points": 26000,
                    "groundSpeed": 0,
                    "coreDrop": 1,
                    "parts": [
                        fpart("magma-left", [-MX, MY], 16, 2300, {"shields": False}),
                        fpart("magma-right", [MX, MY], 16, 2300, {"shields": False}),
                        fpart("battery-left", [-BX, BY], 15, 2000, {"shields": False}),
                        fpart("battery-right", [BX, BY], 15, 2000, {"shields": False}),
                        fpart("shield-left", [-SX, SY], 15, 2600),
                        fpart("shield-right", [SX, SY], 15, 2600),
                    ],
                }
            )
        ),
        "stopFraction": 0.75,
        "sway": {"amplitude": 22, "period": 12},
        "bob": {"amplitude": 5, "period": 5.5},
        "guns": {
            "core": {
                "gun": CALDERA_GUNS,
                "ring": [CALDERA_CROWN],
                "laser": [CALDERA_LENS],
                "missile": CALDERA_HATCHES,
            },
            "magma-left": {
                "laser": mirror(CALDERA_MAGMA),
                "turret": [-MX, MY],
                "turretLaser": True,
            },
            "magma-right": {"laser": CALDERA_MAGMA, "turret": [MX, MY], "turretLaser": True},
            "battery-left": {"missile": mirror(CALDERA_CELLS)},
            "battery-right": {"missile": CALDERA_CELLS},
        },
        "stages": stages(
            [
                volley.laser("magma-left", 5.5, 1.6, 2),
                volley.laser("magma-right", 5.5, 1.6, 4.75),
                volley.missiles("battery-left", 4.6, 2, 24, 3.2),
                volley.missiles("battery-right", 4.6, 2, 24, 5.5),
            ],
            [
                [volley.burst("core", 2.2, 4, 0.11, MAGENTA, 1.2)],
                [volley.fan("core", 2.1, 7, 12, BLUE, 0.8)],
                [
                    volley.aimed("core", 2.8, 1, 0, MAGMA_BOMB, 0.8),
                    volley.aimed("core", 2.1, 3, 10, PURPLE, 1.8),
                ],
                [
                    volley.ring("core", 1.4, 12, 9, PURPLE, 0.6),
                    volley.burst("core", 2.3, 3, 0.11, MAGENTA, 1.3),
                ],
                [
                    volley.missiles("core", 4.2, 2, 30, 1.2),
                    volley.fan("core", 2.2, 5, 14, BLUE, 0.7),
                    volley.burst("core", 2.5, 3, 0.11, MAGENTA, 1.8),
                ],
                [
                    volley.laser("core", 5, 1.5, 1.4),
                    volley.ring("core", 1.7, 14, 0, PURPLE, 0.6),
                    volley.aimed("core", 2.7, 1, 0, MAGMA_BOMB, 1.5),
                ],
                [
                    volley.ring("core", 1, 18, 10, PURPLE, 0.4),
                    volley.laser("core", 5, 1.5, 2),
                    volley.missiles("core", 5, 2, 30, 3),
                    volley.fan("core", 3.2, 3, 30, MAGMA_BOMB, 1.4),
                    volley.burst("core", 2.4, 4, 0.11, MAGENTA, 1.8),
                    volley.aimed("core", 3, 3, 12, BLUE, 2.6),
                ],
            ],
        ),
    }
)
