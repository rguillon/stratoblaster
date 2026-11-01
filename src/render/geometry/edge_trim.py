# Copyright (c) 2026 Renaud Guillon
"""Self-lit edge trim along a model's top-view silhouette.

The trim replaces the rim outline (GFX-TRIM-01, read as a built-in rim light): thin ribbons, lying
just outside the edges a model shows from above, so its silhouette stands out from the ground. Seen
from straight above, those edges are the same whatever the model's heading (enemies and bosses only
turn about the vertical axis), and the playfield camera is close enough to that.

Y is up. Triangles are index triples whose Babylon front normal is `(p2 - p0) x (p1 - p0)`. Vertices
are matched by position, so both flat-shaded solids (each face its own vertices) and meshes with
shared vertices work. Pure maths, unit-tested without Babylon (GFX-TRIM-10).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.geometry.gradient_shapes import ColoredGeometry

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
Vec3 = list[float]
Triangle = list[Vec3]
__pragma__("noskip")

# Positions closer than this are the same vertex.
_SNAP = 1000
# Below this, an edge has no length seen from above.
_FLAT = 1e-6
# Corners between edges whose outward directions are closer than this (about 20°) need no joint:
# the gap between their ribbons does not show.
_STRAIGHT = 0.94
# A corner joins the two edges that meet at it (no more: a branching point gets no joint).
_PAIR = 2
# Edges in a row turning by less than this (cosine, about 15°) are drawn as one ribbon.
_MERGE = 0.966


class TrimOptions:
    """How the trim looks: its `width` and its `offset` out from the edge, in model units.

    Edges of triangles facing less up than `min_up` (the Y of their unit normal) are not traced.
    """

    def __init__(self, width: float, offset: float, min_up: float = 0.2) -> None:
        self.width = width
        self.offset = offset
        self.min_up = min_up


class TrimEdge:
    """A silhouette edge from `a` to `b`, and `out`, the unit horizontal vector away from it."""

    def __init__(self, a: Vec3, b: Vec3, out: Vec3) -> None:
        self.a = a
        self.b = b
        self.out = out


def _point(positions: list[float], i: int) -> Vec3:
    return [positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2]]


def _up(p0: Vec3, p1: Vec3, p2: Vec3) -> float:
    """Return the Y of the unit Babylon normal of the triangle (0 for a degenerate one)."""
    u = [p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]]
    v = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]
    nx = u[1] * v[2] - u[2] * v[1]
    ny = u[2] * v[0] - u[0] * v[2]
    nz = u[0] * v[1] - u[1] * v[0]
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    if length == 0:
        return 0
    return ny / length


def up_triangles(positions: list[float], indices: list[int], min_up: float) -> list[Triangle]:
    """Return the triangles facing up (unit normal Y at least `min_up`), as lists of 3 points."""
    result: list[Triangle] = []
    for t in range(0, len(indices) - 2, 3):
        p0 = _point(positions, indices[t])
        p1 = _point(positions, indices[t + 1])
        p2 = _point(positions, indices[t + 2])
        if _up(p0, p1, p2) >= min_up:
            result.append([p0, p1, p2])
    return result


def _key(p: Vec3) -> str:
    return (
        str(math.floor(p[0] * _SNAP + 0.5))
        + ","
        + str(math.floor(p[1] * _SNAP + 0.5))
        + ","
        + str(math.floor(p[2] * _SNAP + 0.5))
    )


class _Grid:
    """The triangles of `cover` in the XZ cells their bounds touch, to find those over a point."""

    def __init__(self, cover: list[Triangle]) -> None:
        self._cover = cover
        self._cells: dict[str, list[int]] = {}
        if len(cover) == 0:
            self._size = 1.0
            return
        low_x = min([min(t[0][0], t[1][0], t[2][0]) for t in cover])
        high_x = max([max(t[0][0], t[1][0], t[2][0]) for t in cover])
        low_z = min([min(t[0][2], t[1][2], t[2][2]) for t in cover])
        high_z = max([max(t[0][2], t[1][2], t[2][2]) for t in cover])
        self._size = max(high_x - low_x, high_z - low_z, _FLAT) / 32
        for i, t in enumerate(cover):
            x0 = self._cell(min(t[0][0], t[1][0], t[2][0]))
            x1 = self._cell(max(t[0][0], t[1][0], t[2][0]))
            z0 = self._cell(min(t[0][2], t[1][2], t[2][2]))
            z1 = self._cell(max(t[0][2], t[1][2], t[2][2]))
            for cx in range(x0, x1 + 1):
                for cz in range(z0, z1 + 1):
                    key = str(cx) + "," + str(cz)
                    if key not in self._cells:
                        self._cells[key] = []
                    self._cells[key].append(i)

    def _cell(self, v: float) -> int:
        return math.floor(v / self._size)

    def covers(self, x: float, z: float) -> bool:
        """Whether some triangle of the cover lies over (or under) the point, seen from above."""
        key = str(self._cell(x)) + "," + str(self._cell(z))
        if key not in self._cells:
            return False
        return any(_inside(self._cover[i], x, z) for i in self._cells[key])


def _inside(t: Triangle, x: float, z: float) -> bool:
    """Whether (x, z) is strictly inside triangle `t` projected on XZ."""
    d0 = (t[1][0] - t[0][0]) * (z - t[0][2]) - (t[1][2] - t[0][2]) * (x - t[0][0])
    d1 = (t[2][0] - t[1][0]) * (z - t[1][2]) - (t[2][2] - t[1][2]) * (x - t[1][0])
    d2 = (t[0][0] - t[2][0]) * (z - t[2][2]) - (t[0][2] - t[2][2]) * (x - t[2][0])
    eps = 1e-12
    return (d0 > eps and d1 > eps and d2 > eps) or (d0 < -eps and d1 < -eps and d2 < -eps)


def _outward(a: Vec3, b: Vec3, inner: Vec3) -> Vec3 | None:
    """Return the unit horizontal vector square to edge `a`-`b`, away from `inner`.

    It is None for an edge with no length seen from above.
    """
    dx = b[0] - a[0]
    dz = b[2] - a[2]
    length = math.sqrt(dx * dx + dz * dz)
    if length < _FLAT:
        return None
    ox = dz / length
    oz = -dx / length
    mx = (a[0] + b[0]) / 2 - inner[0]
    mz = (a[2] + b[2]) / 2 - inner[2]
    if ox * mx + oz * mz < 0:
        ox = -ox
        oz = -oz
    return [ox, 0, oz]


def silhouette_edges(
    positions: list[float],
    indices: list[int],
    cover: list[Triangle] | None,
    min_up: float,
) -> list[TrimEdge]:
    """Return the edges of up-facing triangles bordering no other up-facing triangle.

    Up-facing as in `up_triangles`. Of those, the edges that no triangle of `cover` lies just
    outside of, seen from above (`cover`: the up-facing triangles of the whole model, those of this
    geometry when None; GFX-TRIM-02).
    """
    ups = up_triangles(positions, indices, min_up)
    grid = _Grid(cover if cover is not None else ups)
    counts: dict[str, int] = {}
    found: dict[str, list[Vec3]] = {}
    order: list[str] = []
    for t in ups:
        for k in range(3):
            a = t[k]
            b = t[(k + 1) % 3]
            ka = _key(a)
            kb = _key(b)
            if ka == kb:
                continue
            key = ka + "|" + kb if ka < kb else kb + "|" + ka
            if key in counts:
                counts[key] += 1
            else:
                counts[key] = 1
                found[key] = [a, b, t[(k + 2) % 3]]
                order.append(key)
    result: list[TrimEdge] = []
    for key in order:
        if counts[key] != 1:
            continue
        a, b, inner = found[key]
        out = _outward(a, b, inner)
        if out is None:
            continue
        dx = b[0] - a[0]
        dz = b[2] - a[2]
        probe = max(math.sqrt(dx * dx + dz * dz) * 0.01, 1e-4)
        mx = (a[0] + b[0]) / 2 + out[0] * probe
        mz = (a[2] + b[2]) / 2 + out[2] * probe
        if grid.covers(mx, mz):
            continue
        result.append(TrimEdge(a, b, out))
    return result


def _along(p: Vec3, out: Vec3, k: float) -> Vec3:
    return [p[0] + out[0] * k, p[1], p[2] + out[2] * k]


def _quad(geo: ColoredGeometry, corners: list[Vec3]) -> None:
    """Two triangles over 4 corners going round, wound to face up."""
    base = len(geo.positions) // 3
    for c in corners:
        geo.positions.extend([c[0], c[1], c[2]])
        geo.colors.extend([1, 1, 1, 1])
    p0, p1, p2 = corners[0], corners[1], corners[2]
    if _up(p0, p1, p2) >= 0:
        geo.indices.extend([base, base + 1, base + 2, base, base + 2, base + 3])
    else:
        geo.indices.extend([base, base + 2, base + 1, base, base + 3, base + 2])


def _wedge(geo: ColoredGeometry, a: Vec3, b: Vec3, c: Vec3) -> None:
    """One triangle over 3 corners, wound to face up."""
    base = len(geo.positions) // 3
    for p in [a, b, c]:
        geo.positions.extend([p[0], p[1], p[2]])
        geo.colors.extend([1, 1, 1, 1])
    if _up(a, b, c) >= 0:
        geo.indices.extend([base, base + 1, base + 2])
    else:
        geo.indices.extend([base, base + 2, base + 1])


def _other_end(edge: TrimEdge, key: str) -> str:
    return _key(edge.b) if _key(edge.a) == key else _key(edge.a)


def _far_point(edge: TrimEdge, key: str) -> Vec3:
    return edge.b if _key(edge.a) == key else edge.a


def _run_tip(
    edges: list[TrimEdge],
    ends: dict[str, list[int]],
    used: list[bool],
    i: int,
    key: str,
    tip: Vec3,
) -> Vec3:
    """Return the far end of the run of edges going on from edge `i` at its end `key` (`tip`).

    They meet two by two and turn by less than about 15° from edge `i`; marks them used.
    """
    first = edges[i]
    while key in ends and len(ends[key]) == _PAIR:
        pair = ends[key]
        j = pair[0] if pair[1] == i or used[pair[1]] else pair[1]
        if used[j]:
            break
        nxt = edges[j]
        if nxt.out[0] * first.out[0] + nxt.out[2] * first.out[2] < _MERGE:
            break
        used[j] = True
        tip = _far_point(nxt, key)
        key = _other_end(nxt, key)
    return tip


def merged_edges(edges: list[TrimEdge]) -> list[TrimEdge]:
    """Return `edges` with each nearly straight run of edges merged into one.

    Each run of edges in a row (meeting two by two) that turns by less than about 15° from its
    first edge is drawn as one, from its first point to its last: curved outlines get far fewer
    ribbons, a little inside the curve.
    """
    ends: dict[str, list[int]] = {}
    for i, edge in enumerate(edges):
        for p in [edge.a, edge.b]:
            key = _key(p)
            if key not in ends:
                ends[key] = []
            ends[key].append(i)
    used = [False for _ in edges]
    result: list[TrimEdge] = []
    for i in range(len(edges)):
        if used[i]:
            continue
        used[i] = True
        first = edges[i]
        # Grow the run both ways from edge i, while the edges meet two by two and stay straight.
        tips = [
            _run_tip(edges, ends, used, i, _key(first.a), first.a),
            _run_tip(edges, ends, used, i, _key(first.b), first.b),
        ]
        a = tips[0]
        b = tips[1]
        out = _outward(a, b, [a[0] - first.out[0], a[1], a[2] - first.out[2]])
        if out is None:
            continue
        # Keep the run's side: the chord's square points the way its first edge's did.
        mid_a = [(a[0] + b[0]) / 2 - first.out[0], 0, (a[2] + b[2]) / 2 - first.out[2]]
        out = _outward(a, b, mid_a) or out
        result.append(TrimEdge(a, b, out))
    return result


def trim_ribbons(edges: list[TrimEdge], options: TrimOptions) -> ColoredGeometry:
    """Return a flat ribbon out from each edge, at the edge's heights.

    Each runs from `offset` to `offset + width`, and a wedge fills the gap at each corner where two
    edges turn, in white vertex colours (GFX-TRIM-03).
    """
    geo = ColoredGeometry()
    edges = merged_edges(edges)
    near = options.offset
    far = options.offset + options.width
    ends: dict[str, list[TrimEdge]] = {}
    order: list[str] = []
    for edge in edges:
        _quad(
            geo,
            [
                _along(edge.a, edge.out, near),
                _along(edge.b, edge.out, near),
                _along(edge.b, edge.out, far),
                _along(edge.a, edge.out, far),
            ],
        )
        for p in [edge.a, edge.b]:
            key = _key(p)
            if key not in ends:
                ends[key] = []
                order.append(key)
            ends[key].append(edge)
    for key in order:
        meeting = ends[key]
        if len(meeting) != _PAIR:
            continue
        e1 = meeting[0]
        e2 = meeting[1]
        if e1.out[0] * e2.out[0] + e1.out[2] * e2.out[2] > _STRAIGHT:
            continue
        p = e1.a if _key(e1.a) == key else e1.b
        _wedge(geo, p, _along(p, e1.out, far), _along(p, e2.out, far))
    return geo


# -- A whole model --------------------------------------------------------------------------------
# Matrices are Babylon's: 16 numbers, row-vector convention (p' = p M, translation in 12..14).

IDENTITY = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]


def multiply(a: list[float], b: list[float]) -> list[float]:
    """Return `a x b`: apply `a`, then `b`."""
    result: list[float] = []
    for r in range(4):
        for c in range(4):
            total = 0.0
            for k in range(4):
                total += a[r * 4 + k] * b[k * 4 + c]
            result.append(total)
    return result


def inverse(m: list[float]) -> list[float]:
    """Return the inverse of an affine matrix (last column 0, 0, 0, 1)."""
    a, b, c = m[0], m[1], m[2]
    d, e, f = m[4], m[5], m[6]
    g, h, i = m[8], m[9], m[10]
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    if det == 0:
        return list(IDENTITY)
    r = [
        (e * i - f * h) / det,
        (c * h - b * i) / det,
        (b * f - c * e) / det,
        (f * g - d * i) / det,
        (a * i - c * g) / det,
        (c * d - a * f) / det,
        (d * h - e * g) / det,
        (b * g - a * h) / det,
        (a * e - b * d) / det,
    ]
    tx, ty, tz = m[12], m[13], m[14]
    return [
        r[0],
        r[1],
        r[2],
        0,
        r[3],
        r[4],
        r[5],
        0,
        r[6],
        r[7],
        r[8],
        0,
        -(tx * r[0] + ty * r[3] + tz * r[6]),
        -(tx * r[1] + ty * r[4] + tz * r[7]),
        -(tx * r[2] + ty * r[5] + tz * r[8]),
        1,
    ]


def transformed(positions: list[float], m: list[float]) -> list[float]:
    """`positions` (flat XYZ) moved by matrix `m`."""
    result: list[float] = []
    for i in range(0, len(positions) - 2, 3):
        x = positions[i]
        y = positions[i + 1]
        z = positions[i + 2]
        result.append(x * m[0] + y * m[4] + z * m[8] + m[12])
        result.append(x * m[1] + y * m[5] + z * m[9] + m[13])
        result.append(x * m[2] + y * m[6] + z * m[10] + m[14])
    return result


class TrimShape:
    """One mesh of a model: its own `positions` and `indices`, and `matrix`.

    `matrix` is from its space to the model's.
    """

    def __init__(self, positions: list[float], indices: list[int], matrix: list[float]) -> None:
        self.positions = positions
        self.indices = indices
        self.matrix = matrix


def trim_model(shapes: list[TrimShape], options: TrimOptions) -> list[ColoredGeometry]:
    """Return the trim of each mesh of a model, in that mesh's own space.

    Its silhouette edges in the model's space are left out where another of its meshes lies just
    outside them, seen from above.
    """
    placed: list[list[float]] = []
    cover: list[Triangle] = []
    for shape in shapes:
        positions = transformed(shape.positions, shape.matrix)
        placed.append(positions)
        cover.extend(up_triangles(positions, shape.indices, options.min_up))
    result: list[ColoredGeometry] = []
    for k, shape in enumerate(shapes):
        edges = silhouette_edges(placed[k], shape.indices, cover, options.min_up)
        geo = trim_ribbons(edges, options)
        geo.positions = transformed(geo.positions, inverse(shape.matrix))
        result.append(geo)
    return result
