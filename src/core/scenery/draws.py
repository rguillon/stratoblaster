"""Weighted and range draws shared by the scenery generators"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Sequence  # noqa: E402
from typing import Protocol, TypeVar  # noqa: E402


class Weighted(Protocol):
    weight: float


class Identified(Protocol):
    id: str


WeightedT = TypeVar("WeightedT", bound=Weighted)
IdentifiedT = TypeVar("IdentifiedT", bound=Identified)
__pragma__("noskip")


def weighted(items: Sequence[WeightedT], r: float) -> WeightedT | None:  # noqa: UP047 (Transcrypt has no PEP 695)
    """The item at `r` (0..1) of `items`, each taking a share of the draw as big as its weight."""
    total = 0.0
    for item in items:
        total += item.weight
    left = r * total
    for item in items:
        left -= item.weight
        if left < 0:
            return item
    return items[len(items) - 1] if len(items) > 0 else None


def allowed(items: Sequence[IdentifiedT], ids: Sequence[str] | None = None) -> list[IdentifiedT]:  # noqa: UP047 (Transcrypt has no PEP 695)
    """The `items` whose id is in `ids` (all of them when `ids` is None)."""
    if ids is None:
        return list(items)
    return [item for item in items if item.id in ids]


def between(bounds: Sequence[float], r: float) -> float:
    """A value in `bounds` = [min, max] for a draw `r` in [0, 1)."""
    low = bounds[0]
    high = bounds[1]
    return low + (high - low) * r
