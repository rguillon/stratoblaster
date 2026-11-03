# Copyright (c) 2026 Renaud Guillon
"""The launch volleys of the bosses' parts (BOSS-25: hangars, drone bays).

The volley itself is built from its config record in `game/sim/boss_build.py`; which parts of each
boss launch is its boss file's (`specs/bosses/`).
"""

from core.entities.enemy import Enemy
from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.hornet import Hornet, hornet_options

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable

# __pragma__ ("noskip")


def _hornets(count: int) -> Callable[[float, float], list[Enemy]]:
    """Hornets leaving a bay: they pause, turn to the player and dive (ENM-HORNET-08)."""

    def launch(x: float, y: float) -> list[Enemy]:
        return [
            Hornet(
                x + (i - (count - 1) / 2) * 14,
                y,
                hornet_options(ENEMY_CONFIG.hornet, None),
            )
            for i in range(count)
        ]

    return launch


def launch_fire(count: int) -> Callable[[float, float], list[Enemy]]:
    """Return what a part's launch of `count` Hornets sends out from (x, y)."""
    return _hornets(count)
