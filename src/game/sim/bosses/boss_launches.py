# Copyright (c) 2026 Renaud Guillon
"""The launch volleys of the bosses' parts (BOSS-25: hangars, drone bays).

The volley itself is built from its config record in `game/sim/boss_build.py`; which parts of each
boss launch is its boss file's (`specs/bosses/`).
"""

from core.entities.enemy import Enemy
from core.systems.enemy_motion import Path
from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.gnat import Gnat
from game.sim.enemies.hornet import Hornet, hornet_options

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable

# __pragma__ ("noskip")


GNATS = ENEMY_CONFIG.gnat
CARRIER = ENEMY_CONFIG.carrier


def _gnats(count: int, side: int) -> Callable[[float, float], list[Enemy]]:
    """Gnats leaving a hangar: out to its side (the side of the boss it is on), then down."""

    def launch(x: float, y: float) -> list[Enemy]:
        path = Path([[x + side * point[0], y + point[1]] for point in CARRIER.launchPath])
        return [Gnat(path, i * GNATS.groupDelay) for i in range(count)]

    return launch


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


def launch_fire(kind: str, count: int, side: int) -> Callable[[float, float], list[Enemy]]:
    """Return what a part's launch of `count` enemies of `kind` sends out from (x, y).

    `kind` is 'gnats' or 'hornets'. `side` is which side of the boss the part is on (-1 left, 1
    right), for the Gnats' way out.
    """
    if kind == "gnats":
        return _gnats(count, side or 1)
    return _hornets(count)
