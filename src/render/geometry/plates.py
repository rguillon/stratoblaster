# Copyright (c) 2026 Renaud Guillon
"""Cracks a flat outline into plates: the broken pieces of a boss's armour (BOSS-43, D-254).

Pure: no Babylon. The outline is a simple polygon of `[x, z]` points; each plate is a simple polygon
inside it, the plates together covering the outline. The outline is triangulated, its triangles cut
down to about `cell` across, their inner corners nudged (so the cracks are not straight lines), and
the triangles grown into at most `most` connected groups; a plate is the boundary of a group.
"""

import math

from render.geometry.triangulate import triangulate_polygon

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
type OutlinePoint = list[float]
type Triangle = list[OutlinePoint]
# __pragma__ ("noskip")


def _key(p: OutlinePoint) -> str:
    """Return a corner's key: its position to a thousandth."""
    return str(round(p[0] * 1000)) + ":" + str(round(p[1] * 1000))


def _edge_key(a: OutlinePoint, b: OutlinePoint) -> str:
    """Return an edge's key, the same either way round."""
    ka = _key(a)
    kb = _key(b)
    return ka + "|" + kb if ka < kb else kb + "|" + ka


def _double_area(ring: list[OutlinePoint]) -> float:
    total = 0.0
    n = len(ring)
    for i in range(n):
        a = ring[i]
        b = ring[(i + 1) % n]
        total += a[0] * b[1] - b[0] * a[1]
    return total


def _counter_clockwise(outline: list[OutlinePoint]) -> list[OutlinePoint]:
    ring = [[p[0], p[1]] for p in outline]
    if _double_area(ring) < 0:
        ring.reverse()
    return ring


def _longest_edge(tri: Triangle) -> float:
    longest = 0.0
    for i in range(3):
        a = tri[i]
        b = tri[(i + 1) % 3]
        longest = max(longest, math.hypot(b[0] - a[0], b[1] - a[1]))
    return longest


def _mid(a: OutlinePoint, b: OutlinePoint) -> OutlinePoint:
    return [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]


def subdivide(tris: list[Triangle], cell: float) -> list[Triangle]:
    """Return `tris` with every triangle longer than `cell` split in four, until none is.

    Neighbours split along a shared edge meet at the same midpoint.
    """
    result = list(tris)
    while True:
        split: list[Triangle] = []
        again = False
        for tri in result:
            if _longest_edge(tri) <= cell:
                split.append(tri)
                continue
            again = True
            a = tri[0]
            b = tri[1]
            c = tri[2]
            ab = _mid(a, b)
            bc = _mid(b, c)
            ca = _mid(c, a)
            split.extend([[a, ab, ca], [ab, b, bc], [ca, bc, c], [ab, bc, ca]])
        result = split
        if not again:
            return result


def _edge_counts(tris: list[Triangle]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for tri in tris:
        for i in range(3):
            k = _edge_key(tri[i], tri[(i + 1) % 3])
            counts[k] = counts[k] + 1 if k in counts else 1
    return counts


def _noise(p: OutlinePoint, seed: float) -> float:
    """Return a fixed pseudo-random in -0.5..0.5 for a point."""
    h = math.sin(p[0] * 12.9898 + p[1] * 78.233 + seed) * 43758.5453
    return h - math.floor(h) - 0.5


def _height(tri: Triangle, i: int) -> float:
    """Return how far corner `i` of `tri` is from the edge facing it."""
    a = tri[(i + 1) % 3]
    b = tri[(i + 2) % 3]
    edge = math.hypot(b[0] - a[0], b[1] - a[1])
    if edge == 0:
        return 0
    p = tri[i]
    return abs((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])) / edge


def _fixed_corners(tris: list[Triangle]) -> dict[str, bool]:
    """Return the corners on the outline of `tris` (on an edge no two triangles share)."""
    counts = _edge_counts(tris)
    fixed: dict[str, bool] = {}
    for tri in tris:
        for i in range(3):
            a = tri[i]
            b = tri[(i + 1) % 3]
            if counts[_edge_key(a, b)] == 1:
                fixed[_key(a)] = True
                fixed[_key(b)] = True
    return fixed


def _room(tris: list[Triangle]) -> dict[str, float]:
    """Return, by corner, how far it may move without flipping a triangle round it."""
    room: dict[str, float] = {}
    for tri in tris:
        for i in range(3):
            k = _key(tri[i])
            h = _height(tri, i) * 0.4
            if k not in room or h < room[k]:
                room[k] = h
    return room


def roughen(tris: list[Triangle], amount: float) -> list[Triangle]:
    """Return `tris` with their inner corners (not on the outline) nudged by up to `amount`.

    The same corner moves the same way in every triangle, so they still meet, and no further than
    the triangles round it allow, so none flips over.
    """
    fixed = _fixed_corners(tris)
    room = _room(tris)
    moved: dict[str, OutlinePoint] = {}
    result: list[Triangle] = []
    for tri in tris:
        corners: Triangle = []
        for p in tri:
            k = _key(p)
            if k in fixed:
                corners.append(p)
                continue
            if k not in moved:
                reach = min(amount, room[k])
                moved[k] = [p[0] + _noise(p, 1) * reach, p[1] + _noise(p, 7) * reach]
            corners.append(moved[k])
        result.append(corners)
    return result


def _neighbours(tris: list[Triangle]) -> list[list[int]]:
    """Return, for each triangle, the triangles sharing an edge with it."""
    owners: dict[str, list[int]] = {}
    for t in range(len(tris)):
        tri = tris[t]
        for i in range(3):
            k = _edge_key(tri[i], tri[(i + 1) % 3])
            if k not in owners:
                owners[k] = []
            owners[k].append(t)
    result: list[list[int]] = [[] for _ in tris]
    for shared in owners.values():
        for a in shared:
            for b in shared:
                if a != b:
                    result[a].append(b)
    return result


def _centre(tri: Triangle) -> OutlinePoint:
    return [
        (tri[0][0] + tri[1][0] + tri[2][0]) / 3,
        (tri[0][1] + tri[1][1] + tri[2][1]) / 3,
    ]


def _first_free(centres: list[OutlinePoint], group: list[int]) -> int:
    """Return the triangle not in a group yet with the smallest centre (X first), -1 when none."""
    best = -1
    for t in range(len(group)):
        if group[t] >= 0:
            continue
        if best < 0:
            best = t
            continue
        c = centres[t]
        b = centres[best]
        if c[0] < b[0] or (c[0] == b[0] and c[1] < b[1]):
            best = t
    return best


def _grow(tris: list[Triangle], neighbours: list[list[int]], size: int) -> list[int]:
    """Grow `tris` into connected groups of about `size`: returns each triangle's group.

    The groups are numbered from 0, in the order of their seeds (the free triangle lowest in X).
    """
    centres = [_centre(tri) for tri in tris]
    group = [-1 for _ in tris]
    count = 0
    while True:
        seed = _first_free(centres, group)
        if seed < 0:
            return group
        queue = [seed]
        group[seed] = count
        members = 1
        while len(queue) > 0 and members < size:
            t = queue.pop(0)
            for n in neighbours[t]:
                if group[n] < 0 and members < size:
                    group[n] = count
                    members += 1
                    queue.append(n)
        count += 1


def _sizes(group: list[int]) -> list[int]:
    """Return how many triangles each group has, by group number (0 for a group merged away)."""
    count = 0
    for g in group:
        count = max(count, g + 1)
    sizes = [0 for _ in range(count)]
    for g in group:
        sizes[g] += 1
    return sizes


def _smallest(sizes: list[int], least: int, skip: list[bool]) -> int:
    """Return the smallest group under `least` triangles not in `skip`, -1 when there is none."""
    small = -1
    for g in range(len(sizes)):
        if sizes[g] == 0 or skip[g]:
            continue
        if sizes[g] < least and (small < 0 or sizes[g] < sizes[small]):
            small = g
    return small


def _group_beside(group: list[int], neighbours: list[list[int]], g: int) -> int:
    """Return a group sharing an edge with group `g`, -1 when it is an island of its own."""
    target = -1
    for t in range(len(group)):
        if group[t] != g:
            continue
        for n in neighbours[t]:
            if group[n] != g:
                target = group[n]
    return target


def _merge(group: list[int], source: int, target: int) -> None:
    for t in range(len(group)):
        if group[t] == source:
            group[t] = target


def _merge_small(group: list[int], neighbours: list[list[int]], least: int) -> list[int]:
    """Merge every group under `least` triangles into a neighbouring group, while one is.

    An island (a group beside no other) is left alone.
    """
    islands = [False for _ in _sizes(group)]
    while True:
        small = _smallest(_sizes(group), least, islands)
        if small < 0:
            return group
        target = _group_beside(group, neighbours, small)
        if target < 0:
            islands[small] = True
            continue
        _merge(group, small, target)


def _merge_down(group: list[int], neighbours: list[list[int]], most: int) -> list[int]:
    """Merge the smallest groups into their neighbours until there are at most `most`.

    An island (a group beside no other) is left alone.
    """
    islands = [False for _ in _sizes(group)]
    while True:
        sizes = _sizes(group)
        left = 0
        for g in range(len(sizes)):
            if sizes[g] > 0 and not islands[g]:
                left += 1
        if left <= most:
            return group
        small = _smallest(sizes, len(group) + 1, islands)
        target = _group_beside(group, neighbours, small)
        if target < 0:
            islands[small] = True
            continue
        _merge(group, small, target)


def _turn(d_in: OutlinePoint, d_out: OutlinePoint) -> float:
    """Return the signed turn from direction `d_in` to `d_out` (negative: to the right)."""
    return math.atan2(
        d_in[0] * d_out[1] - d_in[1] * d_out[0], d_in[0] * d_out[0] + d_in[1] * d_out[1]
    )


def _leftmost(edges: list[list[OutlinePoint]], d_in: OutlinePoint) -> int:
    """Return the edge of `edges` (all leaving one corner) turning most to the left of `d_in`."""
    best = 0
    for i in range(1, len(edges)):
        e = edges[i]
        d = [e[1][0] - e[0][0], e[1][1] - e[0][1]]
        f = edges[best]
        if _turn(d_in, d) > _turn(d_in, [f[1][0] - f[0][0], f[1][1] - f[0][1]]):
            best = i
    return best


def _without_collinear(loop: list[OutlinePoint]) -> list[OutlinePoint]:
    """Return `loop` without the corners lying on the line between their neighbours."""
    result: list[OutlinePoint] = []
    n = len(loop)
    for i in range(n):
        a = loop[(i + n - 1) % n]
        b = loop[i]
        c = loop[(i + 1) % n]
        if abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])) > 1e-6:
            result.append(b)
    return result


def _loops(tris: list[Triangle]) -> list[list[OutlinePoint]]:
    """Return the boundary loops of a group of counter-clockwise triangles (holes dropped).

    Where the boundary passes a corner twice, the loop takes the edge turning most to the left (the
    group's inside stays on its left), so each loop is a simple polygon.
    """
    counts = _edge_counts(tris)
    out: dict[str, list[list[OutlinePoint]]] = {}
    left = 0
    for tri in tris:
        for i in range(3):
            a = tri[i]
            b = tri[(i + 1) % 3]
            if counts[_edge_key(a, b)] == 1:
                k = _key(a)
                if k not in out:
                    out[k] = []
                out[k].append([a, b])
                left += 1
    result: list[list[OutlinePoint]] = []
    while left > 0:
        start = ""
        for k, edges in out.items():
            if len(edges) > 0 and (start == "" or k < start):
                start = k
        loop = _without_collinear(_trace(out, start))
        left -= len(loop) if len(loop) > 0 else 1
        if len(loop) >= 3 and _double_area(loop) > 0:
            result.append(loop)
    return result


def _trace(out: dict[str, list[list[OutlinePoint]]], start: str) -> list[OutlinePoint]:
    """Follow the boundary edges `out` (by their start corner) from `start` back round to it.

    The edges followed are taken out of `out`.
    """
    loop: list[OutlinePoint] = []
    k = start
    d_in = [1.0, 0.0]
    while k in out and len(out[k]) > 0:
        edge = out[k].pop(_leftmost(out[k], d_in))
        loop.append(edge[0])
        d_in = [edge[1][0] - edge[0][0], edge[1][1] - edge[0][1]]
        k = _key(edge[1])
        if k == start:
            break
    return loop


def _plates_of(tris: list[Triangle], group: list[int]) -> list[list[OutlinePoint]]:
    """Return the plates of `tris` grouped by `group`: the boundary loops of each group."""
    groups: list[list[Triangle]] = [[] for _ in _sizes(group)]
    for t in range(len(tris)):
        groups[group[t]].append(tris[t])
    result: list[list[OutlinePoint]] = []
    for members in groups:
        if len(members) > 0:
            result.extend(_loops(members))
    return result


def crack(outline: list[OutlinePoint], cell: float, most: int) -> list[list[OutlinePoint]]:
    """Return `outline` cracked into at most `most` plates of about `cell` across.

    Each plate is a simple polygon; together they cover the outline.
    """
    ring = _counter_clockwise(outline)
    tris: list[Triangle] = [[ring[a], ring[b], ring[c]] for a, b, c in triangulate_polygon(ring)]
    tris = roughen(subdivide(tris, cell), cell * 0.3)
    neighbours = _neighbours(tris)
    size = max(1, math.ceil(len(tris) / max(1, most)))
    group = _merge_small(_grow(tris, neighbours, size), neighbours, max(1, size // 2))
    cap = max(1, most)
    group = _merge_down(group, neighbours, cap)
    result = _plates_of(tris, group)
    # A group whose boundary pinches makes two plates: merge groups down until the cap holds.
    while len(result) > cap > 1:
        cap -= 1
        group = _merge_down(group, neighbours, cap)
        result = _plates_of(tris, group)
    return result
