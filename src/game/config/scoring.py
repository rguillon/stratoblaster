"""Scoring (P11-R01, R07), ported from `config/scoring.ts`.

Each enemy kind's points are in its data (GD-50); a boss scores its points for its core, and
`bossPartShare` of them (rounded to `roundTo`) for each part the player destroys. Life and bomb
bonuses picked up at the most score `overflow` instead.
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
    """The points of one destroyed part of a boss worth `boss_points` (P11-R01)."""
    # Math.round in the TS is floor(x + 0.5) for every value, including negative halves.
    return (
        math.floor((boss_points * SCORING.bossPartShare) / SCORING.roundTo + 0.5) * SCORING.roundTo
    )
