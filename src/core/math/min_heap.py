"""Numbers taken out smallest first (a binary heap), ported from `core/math/min-heap.ts`."""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Sequence  # noqa: E402

__pragma__("noskip")


class MinHeap:
    """A binary min-heap of numbers."""

    def __init__(self, initial: Sequence[float]) -> None:
        """Starts with `initial`, which must be in increasing order."""
        self._items: list[float] = list(initial)

    @property
    def size(self) -> int:
        return len(self._items)

    def push(self, value: float) -> None:
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
        """The smallest number, taken out; None when empty."""
        items = self._items
        if len(items) == 0:
            return None
        top = items[0]
        last = items.pop()
        if len(items) > 0:
            self._sink(last)
        return top

    def _sink(self, value: float) -> None:
        """Puts `value` at the top, then moves it down below its smaller children."""
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
        """The index of the smaller child of `i`, if it has one."""
        items = self._items
        left = 2 * i + 1
        right = 2 * i + 2
        if left >= len(items):
            return None
        if right < len(items) and items[right] < items[left]:
            return right
        return left
