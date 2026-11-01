"""Scoring (GAME-SCORE-02, GAME-SCORE-04)

Each enemy kind's points are in its data (GAME-SCORE-02); a boss scores its points for its core,
and `bossPartShare` of them (rounded to `roundTo`) for each part the player destroys
(GAME-SCORE-04). Life and bomb bonuses picked up at the most score `overflow` instead
(GAME-BONUS-10, dormant: this game sets no maximum).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.record import record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

SCORING = record(
    {
        "bossPartShare": 0.1,
        "roundTo": 10,
        "overflow": {"life": 5000, "bomb": 2000},
    }
)


def boss_part_points(boss_points: float) -> Any:
    """The points of one destroyed part of a boss worth `boss_points` (GAME-SCORE-04).

    The part points of the World 3 and World 4 boss files: MB-MANGROVE-CROC-15,
    FB-RIVER-LEVIATHAN-15, MB-TOUCAN-13, FB-CANOPY-SPIDER-14, MB-STONE-IDOL-13, FB-SKY-TEMPLE-15,
    MB-MOSQUITO-13, FB-DAM-BREAKER-13, MB-JAGUAR-13, FB-VERDANT-CROWN-14; MB-CINDER-CRAB-15,
    FB-STEAM-DREADNOUGHT-19, MB-ASH-WRAITH-14, FB-GEYSER-RIG-19, MB-MAGMA-SALAMANDER-16,
    FB-OBSIDIAN-GOLEM-20, MB-FURNACE-DRAKE-15, FB-FOUNDRY-ARK-20, MB-EMBER-HERALD-13,
    FB-CALDERA-THRONE-18.
    """
    # Math.round in the TS is floor(x + 0.5) for every value, including negative halves.
    return (
        math.floor((boss_points * SCORING.bossPartShare) / SCORING.roundTo + 0.5) * SCORING.roundTo
    )
