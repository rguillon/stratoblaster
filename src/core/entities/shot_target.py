"""Something shots can hit: a circle with health

Positions are in logical pixels, Y up.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Sequence  # noqa: E402
from typing import Protocol  # noqa: E402


class ShotTarget(Protocol):
    """A target shots can hit (a circle with health). Enemies and boss pieces satisfy it."""

    @property
    def id(self) -> int: ...

    @property
    def x(self) -> float: ...

    @property
    def y(self) -> float: ...

    @property
    def radius(self) -> float: ...

    health: float

    @property
    def max_health(self) -> float: ...


__pragma__("noskip")

INFINITY = float("Infinity")


def is_alive(target: ShotTarget) -> bool:
    """Whether the target can still be hit."""
    return target.health > 0


def damage_target(target: ShotTarget, amount: float) -> float:
    """Removes `amount` health, never below 0. Returns the damage actually dealt: 0 when the
    target ignores it (a shielded core, P07-R01).
    """
    before = target.health
    target.health = before - min(before, max(0, amount))
    return before - target.health


def closest_target(
    targets: Sequence[ShotTarget], x: float, y: float, reach: float = INFINITY
) -> ShotTarget | None:
    """The living target closest to (x, y) and within `reach`, or None if there is none."""
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
