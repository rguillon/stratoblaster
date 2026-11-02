# Copyright (c) 2026 Renaud Guillon
"""3-3.

The Sky Temple, the final boss of the Lost temples level (specs/bosses/final/3-3-sky-temple.md).

Offsets in px from the boss's centre, X right and Y up (its grand stair points down, at -Y). Stage
patterns as for the World 1 and 2 final bosses (FB-SKY-TEMPLE-10): its parts fire the same while
they stand, its core fires every bullet pattern, a new one at each stage (aimed shots, spreads,
bursts, fans, rings), and twin spirals used by no earlier stage once it stands alone. Its core
always drops a bonus (FB-SKY-TEMPLE-15). Health (FB-SKY-TEMPLE-08) tuned for WLD-3-20 with the D-055
bot.
"""

from game.config.bosses.boss_kit import bullet, cells, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, slide
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


GOLD = bullet("orange", 200)
RED = bullet("red", 210)
BLUE = bullet("blue", 205)
MAGENTA = bullet("magenta", 195)
GREEN = bullet("green", 190)


def fpart(part_id: str, at: Any, radius: float, health: float, options: Any = None) -> Any:
    """Return a final boss's part.

    Drops a bonus 60 % of the time (FB-SKY-TEMPLE-15, `part_drop_chance`).
    """
    return part(part_id, at, radius, health, merge({"drop": 0.6}, options))


# Where its parts stand (FB-SKY-TEMPLE-08): an obelisk on each corner, the beacon on the summit.
TEMPLE_PARTS = record({"obelisk": [60, 62], "beacon": [0, -28]})

# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).

# The heights of the tips of the obelisks' pyramidions (their spirals), the beacon's cells.
TEMPLE_HEIGHTS = record({"obelisk": 56, "beacon": 54.1, "guns": 41, "crystal": 64})
# The beacon's four missile cells, on its lantern's roof.
TEMPLE_BEACON = cells([-3, 3], [-31, -25], TEMPLE_HEIGHTS.beacon)
# The twin cannons either side of the sanctum's door (the core's shots, spreads, bursts, fans;
# FB-SKY-TEMPLE-03).
TEMPLE_GUNS = twin(8, -11, TEMPLE_HEIGHTS.guns)
# The crystal on the sanctum's roof (the core's rings and spirals).
TEMPLE_CRYSTAL = [[0, 10, TEMPLE_HEIGHTS.crystal]]

OX = TEMPLE_PARTS.obelisk[0]
OY = TEMPLE_PARTS.obelisk[1]
# The obelisks, by part id, and where they stand (X right, Y up).
OBELISKS = record({
    "obelisk-front-left": [-OX, -OY],
    "obelisk-front-right": [OX, -OY],
    "obelisk-back-left": [-OX, OY],
    "obelisk-back-right": [OX, OY],
})


def tip(pos: Any) -> Any:
    """Return the tip of an obelisk standing at `pos`."""
    return [[pos[0], pos[1], TEMPLE_HEIGHTS.obelisk]]


# 3-3: a flying stepped pyramid, gold and cyan neon; its four corner obelisks fire spirals and
# shield the core, its summit beacon homing missiles (FB-SKY-TEMPLE-09), its core every bullet
# pattern.
_SKY_TEMPLE = record({
    "id": "sky-temple",
    # Angry after each destroyed part (phase 7 review, FB-SKY-TEMPLE-11): a vortex inside a
    # blooming flower.
    "rage": concat(rage.vortex(7, "orange", "blue", 0.5), rage.flower(7, "blue", "orange", 0.5)),
    "stats": stats(
        record({
            "id": "sky-temple",
            "name": "Sky Temple",
            "size": 5.5,
            "coreRadius": 22,
            "coreHealth": 3550,
            "points": 15000,
            "groundSpeed": 0.3,
            "coreDrop": 1,
            "parts": [
                fpart("obelisk-back-left", OBELISKS["obelisk-back-left"], 13, 1000),
                fpart("obelisk-back-right", OBELISKS["obelisk-back-right"], 13, 1000),
                fpart("obelisk-front-left", OBELISKS["obelisk-front-left"], 13, 1000),
                fpart("obelisk-front-right", OBELISKS["obelisk-front-right"], 13, 1000),
                fpart("beacon", TEMPLE_PARTS.beacon, 16, 2400, {"shields": False}),
            ],
        })
    ),
    # Where it stops and how it moves in place (FB-SKY-TEMPLE-07).
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
    # The parts' volleys, then the core's pattern per stage (FB-SKY-TEMPLE-10).
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
})

# Its transformations (D-230, FB-SKY-TEMPLE-12): once its back obelisks are gone its back corner
# wedges slide out diagonally, a gun battery riding each, and its back terrace bursts off for a
# mortar (FB-SKY-TEMPLE-13); once its front obelisks are gone its front corner wedges slide out, a
# heavy cannon riding each (FB-SKY-TEMPLE-14).
SKY_TEMPLE = with_weapons(
    merge(
        _SKY_TEMPLE,
        {
            "transformParts": [
                ["obelisk-back-left", "obelisk-back-right"],
                ["obelisk-front-left", "obelisk-front-right"],
            ]
        },
    ),
    [
        hidden_weapon("mortar", "mortar", [0, 36], 13, 1920, 1, "orange", 1.6, 41.0),
        hidden_weapon("battery-left", "battery", [-70, 50], 10, 1920, 1, "orange", 1.2, 24),
        hidden_weapon("battery-right", "battery", [70, 50], 10, 1920, 1, "orange", 2.0, 24),
        hidden_weapon("cannon-left", "cannon", [-66, -52], 10, 2400, 2, "orange", 1.2, 24),
        hidden_weapon("cannon-right", "cannon", [66, -52], 10, 2400, 2, "orange", 2.4, 24),
    ],
    concat(
        moving_region(
            "back-corners",
            1,
            [[34, 20], [88, 20], [88, 72], [34, 72]],
            slide([[0, 0, 0], [15, 15, 0]]),
            "wing",
            [-8, 1000],
        ),
        [
            armour_region(
                "back", 1, [[-32, 2], [32, 2], [32, 64], [-32, 64]], "shell", [1.2, 1000], False
            ),
        ],
        moving_region(
            "front-corners",
            2,
            [[34, -72], [88, -72], [88, -20], [34, -20]],
            slide([[0, 0, 0], [14, -14, 0]]),
            "wing",
            [-8, 1000],
        ),
    ),
)
