# Copyright (c) 2026 Renaud Guillon
"""Stepping enemies of the sim tests the way the world does: `age` advances, then `update` runs.

Also the spawn area the kinds of `game/sim/enemy_kinds.py` are given. CPython only.
"""

from typing import Any

from core.entities.enemy import EnemyEntry, EnemySpawnArea
from core.math.rng import create_rng

STEP = 1 / 60


def area(
    width: float = 400.0,
    height: float = 600.0,
    side: str | None = None,
    position: float = 0.5,
    seed: int = 1,
    top_range: tuple[float, float] | None = None,
) -> EnemySpawnArea:
    """Return a spawn area of `width` x `height`.

    With `side`, a wave entry at `position` on that side.
    """
    entry = None if side is None else EnemyEntry(side, position)
    return EnemySpawnArea(width, height, create_rng(seed), entry, top_range)


def run(enemy: Any, ctx: Any, seconds: float, step: float = STEP) -> None:
    """Step `enemy` for `seconds`, advancing its age before each update (as the world does)."""
    steps = round(seconds / step)
    for _ in range(steps):
        enemy.age += step
        enemy.update(ctx, step)


def run_until(enemy: Any, ctx: Any, done: Any, limit: float = 60.0, step: float = STEP) -> float:
    """Step `enemy` until `done()` holds (at most `limit` seconds); return the seconds run."""
    elapsed = 0.0
    while not done() and elapsed < limit:
        enemy.age += step
        enemy.update(ctx, step)
        elapsed += step
    return elapsed
