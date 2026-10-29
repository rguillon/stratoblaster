"""2D planform outlines (ported from `render/geometry/outline.ts`).

A point is a two-element list `[x, z]`, seen from above (X right, Z forward).
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

OutlinePoint = list[float]
__pragma__("noskip")

# Below this length the bisector of a corner is undefined: the corner stays where it is.
ALONG_EPSILON = 1e-9


def _hypot2(a: float, b: float) -> float:
    __pragma__("js", "{}", "return Math.hypot(a, b);")
    return 0


def _hypot3(a: float, b: float, c: float) -> float:
    __pragma__("js", "{}", "return Math.hypot(a, b, c);")
    return 0


def hypot2(a: float, b: float) -> float:
    """`Math.hypot(a, b)`: JavaScript's rounding, the one the TypeScript results come from."""
    return _hypot2(a, b)


def hypot3(a: float, b: float, c: float) -> float:
    """`Math.hypot(a, b, c)`."""
    return _hypot3(a, b, c)


def reversed_copy(items: list[Any]) -> list[Any]:
    """A reversed copy of `items` (`list(reversed(items))`, written as a loop for Transcrypt)."""
    result: list[Any] = []
    for i in range(len(items) - 1, -1, -1):
        result.append(items[i])
    return result


def ring_at(ring: list[Any], i: int) -> Any:
    """Element `i` of a closed ring (indices wrap around), e.g. the vertices of an outline."""
    n = len(ring)
    if n == 0:
        raise ValueError("Empty ring")
    return ring[((i % n) + n) % n]


def inset_outline(
    outline: list[OutlinePoint],
    distance: float,
    max_miter: float = 3,
) -> list[OutlinePoint]:
    """The outline moved inwards by `distance` (a counter-clockwise outline in (x, z)), each
    corner along its bisector. Sharp corners move at most `max_miter` times `distance`, so thin
    tips stay close to where they were instead of shooting through the outline.
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
            result.append(
                [p[0] + (sx / along) * miter * distance, p[1] + (sz / along) * miter * distance]
            )
    return result


def _normal(p1: OutlinePoint, p2: OutlinePoint) -> list[float]:
    """The unit normal of the edge from `p1` to `p2`, left of it (inwards for a CCW outline)."""
    length = hypot2(p2[0] - p1[0], p2[1] - p1[1]) or 1
    return [-(p2[1] - p1[1]) / length, (p2[0] - p1[0]) / length]
