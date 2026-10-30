"""P09-R09, 3-3: the Sky Temple, the final boss of the Lost temples level (ported from
`config/bosses/world-3/sky-temple.ts`).

Offsets in px from the boss's centre, X right and Y up (its grand stair points down, at -Y). Stage
patterns as for the World 1 and 2 final bosses (P07-R04): its parts fire the same while they stand,
its core fires every bullet pattern, a new one at each stage (aimed shots, spreads, bursts, fans,
rings), and twin spirals used by no earlier stage once it stands alone. Its core always drops a
bonus (P07-R07). Health tuned for P09-R10 with the D-055 bot.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import bullet, cells, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.record import concat, merge, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

GOLD = bullet("orange", 200)
RED = bullet("red", 210)
BLUE = bullet("blue", 205)
MAGENTA = bullet("magenta", 195)
GREEN = bullet("green", 190)


def fpart(part_id: str, at: Any, radius: float, health: float, options: Any = None) -> Any:
    """A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`)."""
    return part(part_id, at, radius, health, merge({"drop": 0.6}, options))


# Where its parts stand (P09-R09): an obelisk on each corner, the beacon on the summit.
TEMPLE_PARTS = record({"obelisk": [60, 62], "beacon": [0, -28]})

# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).

# The heights of the tips of the obelisks' pyramidions (their spirals), the beacon's cells.
TEMPLE_HEIGHTS = record({"obelisk": 56, "beacon": 54.1, "guns": 41, "crystal": 64})
# The beacon's four missile cells, on its lantern's roof.
TEMPLE_BEACON = cells([-3, 3], [-31, -25], TEMPLE_HEIGHTS.beacon)
# The twin cannons either side of the sanctum's door (the core's shots, spreads, bursts, fans).
TEMPLE_GUNS = twin(8, -11, TEMPLE_HEIGHTS.guns)
# The crystal on the sanctum's roof (the core's rings and spirals).
TEMPLE_CRYSTAL = [[0, 10, TEMPLE_HEIGHTS.crystal]]

OX = TEMPLE_PARTS.obelisk[0]
OY = TEMPLE_PARTS.obelisk[1]
# The obelisks, by part id, and where they stand (X right, Y up).
OBELISKS = record(
    {
        "obelisk-front-left": [-OX, -OY],
        "obelisk-front-right": [OX, -OY],
        "obelisk-back-left": [-OX, OY],
        "obelisk-back-right": [OX, OY],
    }
)


def tip(pos: Any) -> Any:
    """The tip of an obelisk standing at `pos`."""
    return [[pos[0], pos[1], TEMPLE_HEIGHTS.obelisk]]


# 3-3: a flying stepped pyramid, gold and cyan neon; its four corner obelisks fire spirals and
# shield the core, its summit beacon homing missiles, its core every bullet pattern (P09-R09).
SKY_TEMPLE = record(
    {
        "id": "sky-temple",
        # Angry after each destroyed part (phase 7 review): a vortex inside a blooming flower.
        "rage": concat(
            rage.vortex(7, "orange", "blue", 0.5), rage.flower(7, "blue", "orange", 0.5)
        ),
        "stats": stats(
            record(
                {
                    "id": "sky-temple",
                    "name": "Sky Temple",
                    "size": 5.5,
                    "coreRadius": 22,
                    "coreHealth": 3550,
                    "points": 15000,
                    "groundSpeed": 0.3,
                    "coreDrop": 1,
                    "parts": [
                        fpart("obelisk-front-left", OBELISKS["obelisk-front-left"], 13, 1000),
                        fpart("obelisk-front-right", OBELISKS["obelisk-front-right"], 13, 1000),
                        fpart("obelisk-back-left", OBELISKS["obelisk-back-left"], 13, 1000),
                        fpart("obelisk-back-right", OBELISKS["obelisk-back-right"], 13, 1000),
                        fpart("beacon", TEMPLE_PARTS.beacon, 16, 2400, {"shields": False}),
                    ],
                }
            )
        ),
        "stopFraction": 0.74,
        "sway": {"amplitude": 30, "period": 11},
        "bob": {"amplitude": 6, "period": 5},
        "guns": {
            "core": {"gun": TEMPLE_GUNS, "ring": TEMPLE_CRYSTAL},
            "obelisk-front-left": {"ring": tip(OBELISKS["obelisk-front-left"])},
            "obelisk-front-right": {"ring": tip(OBELISKS["obelisk-front-right"])},
            "obelisk-back-left": {"ring": tip(OBELISKS["obelisk-back-left"])},
            "obelisk-back-right": {"ring": tip(OBELISKS["obelisk-back-right"])},
            "beacon": {"missile": TEMPLE_BEACON},
        },
        "stages": stages(
            [
                # Each obelisk turns its own spiral: front ones one way, back ones the other.
                volley.ring("obelisk-front-left", 1.6, 4, 23, GOLD, 0.6),
                volley.ring("obelisk-front-right", 1.6, 4, -23, GOLD, 1.4),
                volley.ring("obelisk-back-left", 1.6, 4, -19, GOLD, 1),
                volley.ring("obelisk-back-right", 1.6, 4, 19, GOLD, 1.8),
                volley.missiles("beacon", 5.5, 2, 30, 3),
            ],
            [
                [volley.aimed("core", 2.8, 1, 0, RED, 1.6)],
                [volley.aimed("core", 2.6, 3, 12, RED, 0.8)],
                [volley.burst("core", 2.4, 4, 0.13, MAGENTA, 0.6)],
                [volley.fan("core", 2.4, 5, 14, BLUE, 0.6)],
                [
                    volley.ring("core", 2, 12, 0, GREEN, 0.6),
                    volley.fan("core", 2.6, 7, 12, BLUE, 1.2),
                ],
                [
                    volley.ring("core", 0.6, 6, 14, GOLD, 0.4),
                    volley.ring("core", 0.6, 6, -19, BLUE, 0.7),
                    volley.burst("core", 2.6, 3, 0.12, RED, 1.2),
                ],
            ],
        ),
    }
)
