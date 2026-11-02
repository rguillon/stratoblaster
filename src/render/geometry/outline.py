# Copyright (c) 2026 Renaud Guillon
"""2D planform outlines (the outlines of the shaping primitives, GFX-ART-10).

A point is a two-element list `[x, z]`, seen from above (X right, Z forward).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

OutlinePoint = list[float]
# __pragma__ ("noskip")


# Below this length the bisector of a corner is undefined: the corner stays where it is.
ALONG_EPSILON = 1e-9


def _hypot2(a: float, b: float) -> float:
    __pragma__("js", "{}", "return Math.hypot(a, b);")
    return math.hypot(a, b)  # Only reached outside Transcrypt (CPython).


def _hypot3(a: float, b: float, c: float) -> float:
    __pragma__("js", "{}", "return Math.hypot(a, b, c);")
    return math.hypot(a, b, c)  # Only reached outside Transcrypt (CPython).


def hypot2(a: float, b: float) -> float:
    """`Math.hypot(a, b)`: JavaScript's rounding."""
    return _hypot2(a, b)


def hypot3(a: float, b: float, c: float) -> float:
    """`Math.hypot(a, b, c)`."""
    return _hypot3(a, b, c)


def reversed_copy(items: list[Any]) -> list[Any]:
    """Return a reversed copy of `items` (`list(reversed(items))`).

    It is written as a loop for Transcrypt.
    """
    result: list[Any] = [items[i] for i in range(len(items) - 1, -1, -1)]
    return result


def ring_at(ring: list[Any], i: int) -> Any:
    """Element `i` of a closed ring (indices wrap around), e.g. the vertices of an outline."""
    n = len(ring)
    if n == 0:
        msg = "Empty ring"
        raise ValueError(msg)
    return ring[((i % n) + n) % n]


def inset_outline(
    outline: list[OutlinePoint],
    distance: float,
    max_miter: float = 3,
) -> list[OutlinePoint]:
    """Return the outline moved inwards by `distance`.

    It is a counter-clockwise outline in (x, z), each corner moved along its bisector.

    Sharp corners move at most `max_miter` times `distance`, so thin tips stay close to where they
    were instead of shooting through the outline.
    """
    result: list[OutlinePoint] = []
    for i in range(len(outline)):
        p = outline[i]
        a = _normal(ring_at(outline, i - 1), p)
        b = _normal(p, ring_at(outline, i + 1))
        # (a + b) / (1 + a·b) is `distance` away from both edges; |a + b|² = 2 (1 + a·b), so the
        # corner moves sqrt(2 / (1 + a·b)) times `distance`, capped at `max_miter`.
        sx = a[0] + b[0]
        sz = a[1] + b[1]
        along = hypot2(sx, sz)
        if along < ALONG_EPSILON:
            result.append([p[0], p[1]])
        else:
            miter = min(along / (1 + a[0] * b[0] + a[1] * b[1]), max_miter)
            result.append([
                p[0] + (sx / along) * miter * distance,
                p[1] + (sz / along) * miter * distance,
            ])
    return result


def _normal(p1: OutlinePoint, p2: OutlinePoint) -> list[float]:
    """Return the unit normal of the edge from `p1` to `p2`, left of it.

    It points inwards for a CCW outline.
    """
    length = hypot2(p2[0] - p1[0], p2[1] - p1[1]) or 1
    return [-(p2[1] - p1[1]) / length, (p2[0] - p1[0]) / length]
