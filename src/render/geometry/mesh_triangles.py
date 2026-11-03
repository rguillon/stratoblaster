# Copyright (c) 2026 Renaud Guillon
"""Vertex-coloured geometry read and written as triangles.

Pure: no Babylon. Geometry is a `ColoredGeometry` (XYZ positions, RGBA colours, triangle indices);
a triangle is its three `Vertex` corners, in index order.
"""

import math

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


class Vertex:
    """A vertex: its position and RGBA colour."""

    def __init__(self, position: list[float], color: list[float]) -> None:
        self.position = position
        self.color = color


def _vertex(geo: Any, i: int) -> Vertex:
    p = geo.positions
    c = geo.colors
    return Vertex(
        [p[3 * i], p[3 * i + 1], p[3 * i + 2]], [c[4 * i], c[4 * i + 1], c[4 * i + 2], c[4 * i + 3]]
    )


def triangles(geo: Any) -> list[list[Vertex]]:
    """Return the triangles of `geo`, each as its three vertices (in index order)."""
    ix = geo.indices
    result: list[list[Vertex]] = [
        [
            _vertex(geo, ix[3 * t]),
            _vertex(geo, ix[3 * t + 1]),
            _vertex(geo, ix[3 * t + 2]),
        ]
        for t in range(len(ix) // 3)
    ]
    return result


def append_triangles(geo: Any, tris: list[list[Vertex]], shift: list[float] | None = None) -> None:
    """Add `tris` to `geo` (no shared vertices), each moved by `shift` if given."""
    d = shift if shift is not None else [0, 0, 0]
    for tri in tris:
        base = len(geo.positions) // 3
        for v in tri:
            p = v.position
            geo.positions.extend([p[0] + d[0], p[1] + d[1], p[2] + d[2]])
            geo.colors.extend(v.color)
        geo.indices.extend([base, base + 1, base + 2])


def centroid(tri: list[Vertex]) -> list[float]:
    """Return the centre of a triangle."""
    a = tri[0].position
    b = tri[1].position
    c = tri[2].position
    return [(a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3, (a[2] + b[2] + c[2]) / 3]


def bounds_of(tris: list[Any]) -> list[float]:
    """Return the bounds of `tris`: `[x0, y0, z0, x1, y1, z1]` (infinite when there are none)."""
    b = [math.inf, math.inf, math.inf, -math.inf, -math.inf, -math.inf]
    for tri in tris:
        for v in tri:
            p = v.position
            for a in range(3):
                b[a] = min(b[a], p[a])
                b[a + 3] = max(b[a + 3], p[a])
    return b


def mean_color(tris: list[Any], default: list[float]) -> list[float]:
    """Return the mean RGB colour of the vertices of `tris`, `default` when there are none."""
    total = [0.0, 0.0, 0.0]
    count = 0
    for tri in tris:
        for v in tri:
            c = v.color
            total = [total[0] + c[0], total[1] + c[1], total[2] + c[2]]
            count += 1
    if count == 0:
        return default
    return [total[0] / count, total[1] / count, total[2] / count]
