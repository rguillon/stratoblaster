# Copyright (c) 2026 Renaud Guillon
"""Weighted and range draws shared by the scenery generators."""

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Sequence
from typing import Protocol


class Weighted(Protocol):
    """Anything with a `weight`, as the weighted draws need."""

    weight: float


class Identified(Protocol):
    """Anything with an `id`."""

    id: str


# __pragma__ ("noskip")


def weighted[WeightedT: Weighted](items: Sequence[WeightedT], r: float) -> WeightedT | None:
    """Return the item at `r` (0..1) of `items` (see `weighted_pick`); None when there is none."""
    return weighted_pick(items, r) if len(items) > 0 else None


def weighted_pick[WeightedT: Weighted](items: Sequence[WeightedT], r: float) -> WeightedT:
    """Return the item at `r` (0..1) of `items`, which has at least one.

    Each takes a share of the draw as big as its weight.
    """
    total = 0.0
    for item in items:
        total += item.weight
    left = r * total
    for item in items:
        left -= item.weight
        if left < 0:
            return item
    return items[len(items) - 1]


def allowed[IdentifiedT: Identified](
    items: Sequence[IdentifiedT], ids: Sequence[str] | None = None
) -> list[IdentifiedT]:
    """Return the `items` whose id is in `ids` (all of them when `ids` is None)."""
    if ids is None:
        return list(items)
    return [item for item in items if item.id in ids]


def between(bounds: Sequence[float], r: float) -> float:
    """Return a value in `bounds` = [min, max] for a draw `r` in [0, 1)."""
    low = bounds[0]
    high = bounds[1]
    return low + (high - low) * r
