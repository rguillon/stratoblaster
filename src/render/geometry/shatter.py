# Copyright (c) 2026 Renaud Guillon
"""Carves a region out of vertex-coloured geometry and breaks it into chunks.

For a boss's armour bursting off: docs/superpowers/specs/2026-10-31-boss-armour-shedding-design.md.

Pure: no Babylon. Geometry is a `ColoredGeometry` (XYZ positions, RGBA colours, triangle indices);
the outlines are polygons in the XZ plane, `[x, z]` points. Triangles are sorted whole, by their
centroid, so big faces are first cut down (`subdivide`) to follow an outline closely.
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


def _mid(a: Vertex, b: Vertex) -> Vertex:
    pa = a.position
    pb = b.position
    ca = a.color
    cb = b.color
    return Vertex(
        [(pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2, (pa[2] + pb[2]) / 2],
        [(ca[0] + cb[0]) / 2, (ca[1] + cb[1]) / 2, (ca[2] + cb[2]) / 2, (ca[3] + cb[3]) / 2],
    )


def _length(a: Vertex, b: Vertex) -> float:
    pa = a.position
    pb = b.position
    return math.sqrt((pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2 + (pa[2] - pb[2]) ** 2)


def subdivide(tris: list[list[Vertex]], longest: float, needs: Any = None) -> list[list[Vertex]]:
    """`tris` with each triangle that `needs(tri)` (if given) halved across its longest edge.

    This goes on until no edge is over `longest`.

    The halves keep the winding (and so the facing) of the triangle they come from.
    """
    result: list[list[Vertex]] = []
    todo = list(tris)
    while len(todo) > 0:
        tri = todo.pop()
        if needs != None and not needs(tri):
            result.append(tri)
            continue
        lengths = [_length(tri[0], tri[1]), _length(tri[1], tri[2]), _length(tri[2], tri[0])]
        k = 0
        for i in range(1, 3):
            if lengths[i] > lengths[k]:
                k = i
        if lengths[k] <= longest:
            result.append(tri)
            continue
        a = tri[k]
        b = tri[(k + 1) % 3]
        c = tri[(k + 2) % 3]
        m = _mid(a, b)
        todo.append([a, m, c])
        todo.append([m, b, c])
    return result


def centroid(tri: list[Vertex]) -> list[float]:
    """Return the centroid of a triangle."""
    a = tri[0].position
    b = tri[1].position
    c = tri[2].position
    return [(a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3, (a[2] + b[2] + c[2]) / 3]


def inside(outline: list[list[float]], x: float, z: float) -> bool:
    """Whether (x, z) is inside the polygon `outline` (even-odd rule)."""
    result = False
    n = len(outline)
    j = n - 1
    for i in range(n):
        xi = outline[i][0]
        zi = outline[i][1]
        xj = outline[j][0]
        zj = outline[j][1]
        if (zi > z) != (zj > z) and x < ((xj - xi) * (z - zi)) / (zj - zi) + xi:
            result = not result
        j = i
    return result


class Carve:
    """Where a region is carved: inside any of its `outlines` (XZ), `heights` [low, high]."""

    def __init__(self, outlines: list[list[list[float]]], heights: list[float]) -> None:
        self.outlines = outlines
        self.heights = heights

    def holds(self, point: list[float]) -> bool:
        """Whether the region holds `point` (x, y, z), in a plain loop (ENG-157)."""
        if point[1] < self.heights[0] or point[1] > self.heights[1]:
            return False
        # The armour cut asks this of every corner: seconds of a level's load through `any`.
        for outline in self.outlines:
            if inside(outline, point[0], point[2]):
                return True
        return False


def straddles(tri: list[Vertex], region: Carve) -> bool:
    """Whether a triangle may cross the edge of `region`.

    Its corners or centroid are not all on the same side, or a corner of an outline lies within its
    XZ bounds.
    """
    inner = region.holds(centroid(tri))
    for v in tri:
        if region.holds(v.position) != inner:
            return True
    xs = [tri[0].position[0], tri[1].position[0], tri[2].position[0]]
    zs = [tri[0].position[2], tri[1].position[2], tri[2].position[2]]
    x0 = min(xs[0], xs[1], xs[2])
    x1 = max(xs[0], xs[1], xs[2])
    z0 = min(zs[0], zs[1], zs[2])
    z1 = max(zs[0], zs[1], zs[2])
    for outline in region.outlines:
        for point in outline:
            if x0 <= point[0] <= x1 and z0 <= point[1] <= z1:
                return True
    return False


def carve(tris: list[list[Vertex]], region: Carve) -> list[list[list[Vertex]]]:
    """`tris` split in two by their centroids: `[kept, carved]` (the carved ones in `region`)."""
    kept: list[list[Vertex]] = []
    carved: list[list[Vertex]] = []
    for tri in tris:
        if region.holds(centroid(tri)):
            carved.append(tri)
        else:
            kept.append(tri)
    return [kept, carved]


def _cell_key(i: int, j: int) -> str:
    return str(i) + ":" + str(j)


def _bins(points: list[list[float]], cell: float) -> list[list[int]]:
    """Return the indices of `points` binned on an XZ grid of `cell`, a list per occupied cell."""
    cells: dict[str, int] = {}
    result: list[list[int]] = []
    for k in range(len(points)):
        p = points[k]
        key = _cell_key(math.floor(p[0] / cell), math.floor(p[2] / cell))
        if key not in cells:
            cells[key] = len(result)
            result.append([])
        result[cells[key]].append(k)
    return result


def _centre(points: list[list[float]], members: list[int]) -> list[float]:
    """Return the mean XZ of the `members` of `points`."""
    sx = 0.0
    sz = 0.0
    for k in members:
        sx += points[k][0]
        sz += points[k][2]
    n = len(members)
    return [sx / n, sz / n]


def _nearest(points: list[list[float]], groups: list[list[int]], small: int) -> int:
    """Return the group (other than `small`) whose centre is nearest `small`'s."""
    cs = _centre(points, groups[small])
    best = -1
    best_d = 0.0
    for g in range(len(groups)):
        if g == small:
            continue
        c = _centre(points, groups[g])
        d = (c[0] - cs[0]) ** 2 + (c[1] - cs[1]) ** 2
        if best < 0 or d < best_d:
            best = g
            best_d = d
    return best


def chunk_cells(points: list[list[float]], cell: float, most: int) -> list[int]:
    """Return the chunk each of `points` (x, y, z) falls in.

    Points are binned on an XZ grid of `cell`, then the smallest chunks are merged into their
    nearest neighbour until there are at most `most`.

    Chunks are numbered from 0, with no gaps.
    """
    groups = _bins(points, cell)
    while len(groups) > max(1, most):
        small = 0
        for g in range(len(groups)):
            if len(groups[g]) < len(groups[small]):
                small = g
        best = _nearest(points, groups, small)
        groups[best].extend(groups[small])
        groups = [groups[g] for g in range(len(groups)) if g != small]
    result = [0 for _ in points]
    for n in range(len(groups)):
        for k in groups[n]:
            result[k] = n
    return result


class Chunk:
    """A piece of carved geometry: its triangles moved to be about `centre`, and `centre`."""

    def __init__(self, tris: list[list[Vertex]], centre: list[float]) -> None:
        self.tris = tris
        self.centre = centre


def shatter(tris: list[list[Vertex]], cell: float, most: int) -> list[Chunk]:
    """`tris` broken into at most `most` chunks by their centroids on an XZ grid of `cell`.

    Each chunk's triangles keep their place; its `centre` is the mean of their centroids.
    """
    centres = [centroid(t) for t in tris]
    ids = chunk_cells(centres, cell, most)
    count = 0
    for i in ids:
        count = max(count, i + 1)
    groups: list[list[list[Vertex]]] = [[] for _ in range(count)]
    sums: list[list[float]] = [[0.0, 0.0, 0.0] for _ in range(count)]
    for k in range(len(tris)):
        g = ids[k]
        groups[g].append(tris[k])
        for a in range(3):
            sums[g][a] += centres[k][a]
    result: list[Chunk] = []
    for g in range(count):
        n = len(groups[g])
        result.append(Chunk(groups[g], [sums[g][0] / n, sums[g][1] / n, sums[g][2] / n]))
    return result


def up_facing(tri: list[Vertex], least: float) -> bool:
    """Whether a triangle faces up: the Y of its unit front normal is at least `least`.

    Babylon's front normal of (a, b, c) is (c - a) x (b - a).
    """
    a = tri[0].position
    b = tri[1].position
    c = tri[2].position
    u = [c[0] - a[0], c[1] - a[1], c[2] - a[2]]
    v = [b[0] - a[0], b[1] - a[1], b[2] - a[2]]
    n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
    size = math.sqrt(n[0] * n[0] + n[1] * n[1] + n[2] * n[2])
    return size > 0 and n[1] / size >= least
