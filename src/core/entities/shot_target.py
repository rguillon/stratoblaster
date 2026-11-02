# Copyright (c) 2026 Renaud Guillon
"""Something shots can hit: a circle with health (ENG-09).

Positions are in logical pixels, Y up.
"""

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Sequence
from typing import Protocol


class ShotTarget(Protocol):
    """A target shots can hit (a circle with health). Enemies and boss pieces satisfy it."""

    @property
    def id(self) -> int:
        """Unique id among the world's targets."""
        ...

    @property
    def x(self) -> float:
        """X of its centre, in logical pixels."""
        ...

    @property
    def y(self) -> float:
        """Y of its centre, in logical pixels."""
        ...

    @property
    def radius(self) -> float:
        """Radius of its hit circle."""
        ...

    health: float

    @property
    def max_health(self) -> float:
        """Health it starts with."""
        ...


# __pragma__ ("noskip")


INFINITY = float("Infinity")


def is_alive(target: ShotTarget) -> bool:
    """Whether the target can still be hit."""
    return target.health > 0


def damage_target(target: ShotTarget, amount: float) -> float:
    """Remove `amount` health, never below 0. Returns the damage actually dealt.

    0 when the target ignores it (a blocked hit, GAME-WPN-17: e.g. a shielded core, BOSS-14).
    """
    before = target.health
    target.health = before - min(before, max(0, amount))
    return before - target.health


def closest_target(
    targets: Sequence[ShotTarget], x: float, y: float, reach: float = INFINITY
) -> ShotTarget | None:
    """Return the living target closest to (x, y) and within `reach`, or None if there is none."""
    best: ShotTarget | None = None
    best_distance = reach**2
    for target in targets:
        if not is_alive(target):
            continue
        distance = (target.x - x) ** 2 + (target.y - y) ** 2
        if distance < best_distance:
            best = target
            best_distance = distance
    return best
