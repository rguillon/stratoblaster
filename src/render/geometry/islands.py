"""Which pieces of a model hold together (docs/superpowers/specs/2026-10-31-boss-armour-shedding-
design.md, D-227: a boss stays one object).

Pure: no Babylon. Triangles are lists of three `shatter.Vertex`. Two triangles are in the same
piece when they share a corner position; two pieces hold together when their surfaces come within
about `cell` of each other (sampled into cubes of `cell` px), as solids standing on or sunk into
each other do. Bounds alone would not do: a hull's bounds hold the whole model.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


def _find(parent: list[int], a: int) -> int:
    while parent[a] != a:
        parent[a] = parent[parent[a]]
        a = parent[a]
    return a


def _join(parent: list[int], a: int, b: int) -> None:
    ra = _find(parent, a)
    rb = _find(parent, b)
    if ra != rb:
        parent[ra] = rb


def _key(p: list[float]) -> str:
    return str(round(p[0] * 50)) + ":" + str(round(p[1] * 50)) + ":" + str(round(p[2] * 50))


def bounds_of(tris: list[Any]) -> list[float]:
    """The bounds of `tris`: `[x0, y0, z0, x1, y1, z1]`."""
    b = [math.inf, math.inf, math.inf, -math.inf, -math.inf, -math.inf]
    for tri in tris:
        for v in tri:
            p = v.position
            for a in range(3):
                b[a] = min(b[a], p[a])
                b[a + 3] = max(b[a + 3], p[a])
    return b


def touch(a: list[float], b: list[float], tolerance: float) -> bool:
    """Whether the bounds `a` and `b` touch, within `tolerance`."""
    apart = [a[k] - tolerance > b[k + 3] or b[k] - tolerance > a[k + 3] for k in range(3)]
    return not (apart[0] or apart[1] or apart[2])


def pieces(tris: list[Any]) -> list[list[int]]:
    """The indices of `tris` by piece: triangles sharing a corner position are one piece."""
    parent = [i for i in range(len(tris))]
    first: dict[str, int] = {}
    for i in range(len(tris)):
        for v in tris[i]:
            key = _key(v.position)
            if key in first:
                _join(parent, i, first[key])
            else:
                first[key] = i
    # Each root's group number (-1: none yet), in order of first triangle.
    number = [-1 for _ in tris]
    result: list[list[int]] = []
    for i in range(len(tris)):
        r = _find(parent, i)
        if number[r] < 0:
            number[r] = len(result)
            result.append([])
        result[number[r]].append(i)
    return result


def _by_left(boxes: list[list[float]], indices: list[int]) -> list[int]:
    """`indices` sorted by the left edge (X) of their box (a merge sort)."""
    if len(indices) <= 1:
        return indices
    half = len(indices) // 2
    a = _by_left(boxes, indices[:half])
    b = _by_left(boxes, indices[half:])
    result: list[int] = []
    i = 0
    j = 0
    while i < len(a) and j < len(b):
        if boxes[a[i]][0] <= boxes[b[j]][0]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    result.extend(a[i:])
    result.extend(b[j:])
    return result


def holding(boxes: list[list[float]], tolerance: float) -> list[int]:
    """The group of each of `boxes`: boxes that touch (directly or through others) share one.
    Groups are numbered from 0 in order of their first box."""
    parent = [i for i in range(len(boxes))]
    # Sweep along X: only boxes whose X spans meet are compared.
    order = _by_left(boxes, [i for i in range(len(boxes))])
    for a in range(len(order)):
        i = order[a]
        reach = boxes[i][3] + tolerance
        b = a + 1
        while b < len(order) and boxes[order[b]][0] <= reach:
            j = order[b]
            if _find(parent, i) != _find(parent, j) and touch(boxes[i], boxes[j], tolerance):
                _join(parent, i, j)
            b += 1
    number = [-1 for _ in boxes]
    count = 0
    result: list[int] = []
    for i in range(len(boxes)):
        r = _find(parent, i)
        if number[r] < 0:
            number[r] = count
            count += 1
        result.append(number[r])
    return result


def _samples(tri: Any, step: float) -> list[list[float]]:
    """Points spread over a triangle, about `step` apart (its corners included)."""
    a = tri[0].position
    b = tri[1].position
    c = tri[2].position
    longest = max(
        math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]),
        math.hypot(c[0] - b[0], c[1] - b[1], c[2] - b[2]),
        math.hypot(a[0] - c[0], a[1] - c[1], a[2] - c[2]),
    )
    n = max(1, math.ceil(longest / step))
    result: list[list[float]] = []
    for i in range(n + 1):
        for j in range(n + 1 - i):
            u = i / n
            v = j / n
            w = 1 - u - v
            result.append(
                [
                    a[0] * w + b[0] * u + c[0] * v,
                    a[1] * w + b[1] * u + c[1] * v,
                    a[2] * w + b[2] * u + c[2] * v,
                ]
            )
    return result


def _cell_key(i: int, j: int, k: int) -> str:
    return str(i) + ":" + str(j) + ":" + str(k)


def holding_surfaces(tris: list[Any], groups: list[list[int]], cell: float) -> list[int]:
    """The object each piece (`groups`, indices of `tris`) belongs to: pieces whose surfaces fall
    in the same or neighbouring cubes of `cell` hold together. Objects numbered from 0."""
    parent = [g for g in range(len(groups))]
    owner: dict[str, int] = {}
    for g in range(len(groups)):
        for t in groups[g]:
            for p in _samples(tris[t], cell * 0.8):
                key = _cell_key(
                    math.floor(p[0] / cell), math.floor(p[1] / cell), math.floor(p[2] / cell)
                )
                if key in owner:
                    _join(parent, g, owner[key])
                else:
                    owner[key] = g
    # Neighbouring cubes: a surface just over another one.
    for key in list(owner.keys()):
        parts = key.split(":")
        i = int(parts[0])
        j = int(parts[1])
        k = int(parts[2])
        for d in [[1, 0, 0], [0, 1, 0], [0, 0, 1]]:
            other = _cell_key(i + d[0], j + d[1], k + d[2])
            if other in owner:
                _join(parent, owner[key], owner[other])
    number = [-1 for _ in groups]
    count = 0
    result: list[int] = []
    for g in range(len(groups)):
        r = _find(parent, g)
        if number[r] < 0:
            number[r] = count
            count += 1
        result.append(number[r])
    return result


# How near the model's centre (px, seen from above) the main object must reach.
CENTRE = 12.0


def main_object(tris: list[Any], groups: list[list[int]], held: list[int]) -> int:
    """The main object: of those reaching within `CENTRE` of the model's centre seen from above
    (a boss's core is there), the one with the most triangles; else the biggest."""
    sizes = [0 for _ in groups]
    near = [False for _ in groups]
    for k in range(len(groups)):
        sizes[held[k]] += len(groups[k])
        if near[held[k]]:
            continue
        for i in groups[k]:
            for v in tris[i]:
                if v.position[0] * v.position[0] + v.position[2] * v.position[2] <= CENTRE * CENTRE:
                    near[held[k]] = True
    best = -1
    for h in range(len(groups)):
        if sizes[h] == 0:
            continue
        better = best < 0 or (near[h] and not near[best])
        if best >= 0 and near[h] == near[best]:
            better = sizes[h] > sizes[best]
        if better:
            best = h
    return best


def loose_triangles(tris: list[Any], cell: float) -> list[bool]:
    """Which of `tris` are not held to the main object they make (see `main_object`)."""
    groups = pieces(tris)
    if len(groups) == 0:
        return []
    held = holding_surfaces(tris, groups, cell)
    main = main_object(tris, groups, held)
    result = [False for _ in tris]
    for k in range(len(groups)):
        if held[k] != main:
            for i in groups[k]:
                result[i] = True
    return result
