"""Stable sorts for the scenery, as JavaScript's `Array.prototype.sort` with a comparator gives.

Transcrypt's `sort` takes a key without keeping the order of equal keys, and it cannot take a
comparator, so the scenery sorts with this merge sort (not part of the TypeScript sources).
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402
from typing import TypeVar  # noqa: E402

T = TypeVar("T")
__pragma__("noskip")


def stable_sort_by(items: Sequence[T], key: Callable[[T], float]) -> list[T]:  # noqa: UP047 (Transcrypt has no PEP 695)
    """A new list of `items` in increasing `key`, equal keys in their original order."""
    if len(items) <= 1:
        return list(items)
    middle = len(items) // 2
    left = stable_sort_by(items[:middle], key)
    right = stable_sort_by(items[middle:], key)
    result: list[T] = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if key(right[j]) < key(left[i]):
            result.append(right[j])
            j += 1
        else:
            result.append(left[i])
            i += 1
    while i < len(left):
        result.append(left[i])
        i += 1
    while j < len(right):
        result.append(right[j])
        j += 1
    return result
