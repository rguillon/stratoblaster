# Copyright (c) 2026 Renaud Guillon
"""The blasts of the hits a step landed (GFX-FX-01, GFX-FX-03, GFX-FX-04).

On the player: a spark where a hit landed; a blast at the ship when it cost a life (GAME-LIFE-08).
Of the player's missiles: a little explosion where each one hit (D-321).
"""

from config.game_play import GAME_PLAY_CONFIG as CFG
from core.systems.enemy_world import EnemyBlast

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from core.systems.level_run_types import LandedHit
from core.systems.shot_world import ShotImpact

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


def impact_blasts(impacts: list[ShotImpact]) -> list[EnemyBlast]:
    """Return a little explosion where each of the player's missiles hit (GFX-FX-03, D-321).

    The missile's own blast (layered, small: GFX-FX-05, GFX-FX-06), the size of the area it damages
    (its `blast_radius`). Bullets and the laser hit directly (no blast radius) and keep their
    sparks.
    """
    return [
        EnemyBlast("missile", impact.x, impact.y, impact.blast_radius)
        for impact in impacts
        if impact.blast_radius > 0
    ]
