# Copyright (c) 2026 Renaud Guillon
"""The blasts of the hits a step landed on the player (GFX-FX-01, GFX-FX-04).

A spark where a hit landed; a blast at the ship when it cost a life (GAME-LIFE-08).
"""

from config.game_play import GAME_PLAY_CONFIG as CFG
from core.systems.enemy_world import EnemyBlast

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from core.systems.level_run_types import LandedHit

# __pragma__ ("noskip")


def hit_blasts(hits: list[LandedHit], ship: Any) -> list[EnemyBlast]:
    """One blast per landed hit: a spark where it landed.

    Or a blast at `ship` (which has `x` and `y`) when the hit cost a life.
    """
    hit_spark = CFG.damage.hit_spark
    ship_blast = CFG.damage.ship_blast
    return [
        EnemyBlast("missile", hit.x, hit.y, hit_spark)
        if hit.event == "hit"
        else EnemyBlast("enemy", ship.x, ship.y, ship_blast)
        for hit in hits
    ]
