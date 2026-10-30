"""P10-R11, 4-4's final boss: the Foundry Ark, fought over the forge belt ().

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y). Stage
patterns as for the World 3 final bosses (P07-R04, D-055): its parts fire the same while they
stand, its blast furnace (the core) fires something new at every stage (slag blobs bursting into
rings among them), and spirals and rings of its own, used by no earlier stage, once it stands
alone. Its core always drops a bonus (P07-R07). Health tuned for P10-R12.
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


RED = bullet("red", 215)
ORANGE = bullet("orange", 210)
MAGENTA = bullet("magenta", 205)
PURPLE = bullet("purple", 200)
# A glob of slag poured from the furnace: slow and big, it bursts into a ring on its way down.
SLAG = bursting("orange", 115, 7, [1.1, 9, bullet("red", 195)])
# The molten metal a destroyed crucible spills: a ring of bullets (as the Dam Breaker's tanks).
SPILL = bullet("orange", 185)

# Where its parts stand (P10-R11): the rail cannons on the outriggers, the chimney row on the
# foredeck, the missile battery on the bow, the crucibles aft either side of the furnace.
ARK_PARTS = record(
    {"rail": [72, -12], "chimneys": [0, -50], "battery": [0, -82], "crucible": [60, 42]}
)

# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), turrets at rest.

# The right rail cannon's emitter, between the tips of its two rails.
ARK_RAIL = [[ARK_PARTS.rail[0], -52, 8]]
# The missile battery's four cells, 2 columns by 2 rows.
ARK_CELLS = cells([-5.5, 5.5], [-87, -77], 9.1)
# The furnace's twin tap guns, low on its front.
ARK_TAPS = twin(9, -33, 7)
# The furnace's throat, at the top of its stack (the core's rings and spirals).
ARK_THROAT = [0, 0, 36]

RX = ARK_PARTS.rail[0]
RY = ARK_PARTS.rail[1]
CX = ARK_PARTS.crucible[0]
CY = ARK_PARTS.crucible[1]

# 4-4: a huge flying foundry of sooty iron under orange neon, molten seams glowing between its
# plates; two rail cannons on turrets aim lasers and, with the chimney row, shield the blast furnace
# at its heart; a missile battery on the bow; two glowing crucibles aft that spill into rings of
# bullets when destroyed. The battery hangs in front of the chimneys and the crucibles stand clear
# of the furnace, so every part can be shot.
FOUNDRY_ARK = record(
    {
        "id": "foundry-ark",
        # Angry after each destroyed part (phase 7 review): heat 13, on from World 3.
        "rage": concat(
            rage.curtain(13, "orange", "red", 0.5), rage.spirals(13, "red", "orange", 0.5)
        ),
        "stats": stats(
            record(
                {
                    "id": "foundry-ark",
                    "name": "Foundry Ark",
                    "size": 6,
                    "coreRadius": 28,
                    "coreHealth": 5600,
                    "points": 20000,
                    "groundSpeed": 0.3,
                    "coreDrop": 1,
                    "parts": [
                        fpart("rail-left", [-RX, RY], 19, 1500),
                        fpart("rail-right", [RX, RY], 19, 1500),
                        fpart("chimneys", list(ARK_PARTS.chimneys), 16, 2400),
                        fpart("battery", list(ARK_PARTS.battery), 13, 900, {"shields": False}),
                        fpart("crucible-left", [-CX, CY], 15, 1450, {"shields": False}),
                        fpart("crucible-right", [CX, CY], 15, 1450, {"shields": False}),
                    ],
                }
            )
        ),
        "stopFraction": 0.75,
        "sway": {"amplitude": 28, "period": 12},
        "bob": {"amplitude": 5, "period": 5.5},
        "breakRings": {
            "crucible-left": {"count": 14, "bullet": SPILL},
            "crucible-right": {"count": 14, "bullet": SPILL},
        },
        "guns": {
            "core": {"gun": ARK_TAPS, "ring": [ARK_THROAT]},
            "rail-left": {"laser": mirror(ARK_RAIL), "turret": [-RX, RY], "turretLaser": True},
            "rail-right": {"laser": ARK_RAIL, "turret": [RX, RY], "turretLaser": True},
            "battery": {"missile": ARK_CELLS},
        },
        "stages": stages(
            [
                volley.laser("rail-left", 6.5, 1.6, 2),
                volley.laser("rail-right", 6.5, 1.6, 5.2),
                volley.missiles("battery", 5.5, 2, 26, 3.5),
            ],
            [
                [volley.burst("core", 2.4, 4, 0.12, RED, 1.4)],
                [volley.fan("core", 2.3, 5, 13, ORANGE, 0.8)],
                [
                    volley.aimed("core", 3, 1, 0, SLAG, 0.8),
                    volley.aimed("core", 2.2, 3, 10, MAGENTA, 1.9),
                ],
                [
                    volley.ring("core", 1.9, 12, 7, ORANGE, 0.6),
                    volley.burst("core", 2.6, 3, 0.12, RED, 1.2),
                ],
                [
                    volley.fan("core", 2.4, 7, 11, MAGENTA, 0.6),
                    volley.ring("core", 0.55, 4, 19, RED, 0.4),
                ],
                [
                    volley.ring("core", 0.5, 5, 17, ORANGE, 0.4),
                    volley.ring("core", 0.5, 5, -19, PURPLE, 0.65),
                ],
                [
                    volley.ring("core", 1.1, 16, 9, ORANGE, 0.4),
                    volley.ring("core", 1.1, 16, -11, RED, 0.95),
                    volley.fan("core", 3.2, 3, 30, SLAG, 1.4),
                    volley.burst("core", 2.6, 4, 0.11, MAGENTA, 1.8),
                ],
            ],
        ),
    }
)
