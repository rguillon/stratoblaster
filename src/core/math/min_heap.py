# Copyright (c) 2026 Renaud Guillon
"""Numbers taken out smallest first (a binary heap)."""

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Sequence

# __pragma__ ("noskip")


class MinHeap:
    """A binary min-heap of numbers."""

    def __init__(self, initial: Sequence[float]) -> None:
        """Start with `initial`, which must be in increasing order."""
        self._items: list[float] = list(initial)

    @property
    def size(self) -> int:
        """How many numbers are in the heap."""
        return len(self._items)

    def push(self, value: float) -> None:
        """Add `value`, keeping the smallest number on top."""
        items = self._items
        i = len(items)
        items.append(value)
        while i > 0:
            parent = (i - 1) // 2
            above = items[parent]
            if above <= value:
                break
            items[i] = above
            i = parent
        items[i] = value

    def pop(self) -> float | None:
        """Return the smallest number, taken out; None when empty."""
        items = self._items
        if len(items) == 0:
            return None
        top = items[0]
        last = items.pop()
        if len(items) > 0:
            self._sink(last)
        return top

    def _sink(self, value: float) -> None:
        """Put `value` at the top, then move it down below its smaller children."""
        items = self._items
        i = 0
        child = self._smaller_child(i)
        while child is not None:
            below = items[child]
            if below >= value:
                break
            items[i] = below
            i = child
            child = self._smaller_child(i)
        items[i] = value

    def _smaller_child(self, i: int) -> int | None:
        """Return the index of the smaller child of `i`, if it has one."""
        items = self._items
        left = 2 * i + 1
        right = 2 * i + 2
        if left >= len(items):
            return None
        if right < len(items) and items[right] < items[left]:
            return right
        return left
