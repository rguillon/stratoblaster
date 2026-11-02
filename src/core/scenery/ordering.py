# Copyright (c) 2026 Renaud Guillon
"""Stable sorts for the scenery, as JavaScript's `Array.prototype.sort` with a comparator gives.

Transcrypt's `sort` takes a key without keeping the order of equal keys, and it cannot take a
comparator, so the scenery sorts with this merge sort (ENG-159).
"""

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable, Sequence

# __pragma__ ("noskip")


def stable_sort_by[T](items: Sequence[T], key: Callable[[T], float]) -> list[T]:
    """Return a new list of `items` in increasing `key`, equal keys in their original order."""
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
