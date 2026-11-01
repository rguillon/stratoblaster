# Copyright (c) 2026 Renaud Guillon
"""Stems holding a boss's loose pieces to it at rest (BOSS-52, D-227: a boss stays one object).

A piece of its core or of a part that touches nothing (a light over a hull, a blade under a wing)
gets a dark metal stem down to the surface beneath it, or a beam out to the nearest point of the
boss.

Model space of a boss: logical pixels, +Y up (towards the camera), see `boss_limbs.boss_point`.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.boss_frame import draw_bridge
from render.geometry.islands import bounds_of, loose_triangles, pieces
from render.geometry.shatter import up_facing
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


def _height_at(tri: Any, x: float, z: float) -> Any:
    """Return the height of a triangle's plane at (x, z) if (x, z) is over it, else None."""
    a = tri[0].position
    b = tri[1].position
    c = tri[2].position
    det = (b[2] - c[2]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[2] - c[2])
    if abs(det) < 1e-9:
        return None
    l0 = ((b[2] - c[2]) * (x - c[0]) + (c[0] - b[0]) * (z - c[2])) / det
    l1 = ((c[2] - a[2]) * (x - c[0]) + (a[0] - c[0]) * (z - c[2])) / det
    l2 = 1 - l0 - l1
    if l0 < 0 or l1 < 0 or l2 < 0:
        return None
    return l0 * a[1] + l1 * b[1] + l2 * c[1]


def surface_below(tris: list[Any], x: float, z: float, below: float) -> Any:
    """Return the highest up-facing surface of `tris` under (x, z) lower than `below`, else None."""
    best = None
    for tri in tris:
        if not up_facing(tri, 0.2):
            continue
        h = _height_at(tri, x, z)
        if h != None and h <= below and (best == None or h > best):
            best = h
    return best


def stems_for(tris: list[Any], lasting: list[Any] | None = None) -> list[Any]:
    """Return what holds the loose pieces of `tris` to the main object.

    `["stem", x, z, low, high, width]` up from a surface beneath, or `["beam", from, to]` out to the
    nearest point; both on `lasting` (what is never shed) when given, else on the main object.
    """
    roots = lasting if lasting is not None else []
    loose = loose_triangles(tris, BOSS_LOOK.armour.hold)
    hanging = [i for i in range(len(tris)) if loose[i]]
    if len(hanging) == 0:
        return []
    held = [tris[i] for i in range(len(tris)) if not loose[i]]
    result: list[Any] = []
    for piece in pieces([tris[i] for i in hanging]):
        b = bounds_of([tris[hanging[k]] for k in piece])
        x = (b[0] + b[3]) / 2
        z = (b[2] + b[5]) / 2
        width = max(1.2, min(4, min(b[3] - b[0], b[5] - b[2]) * 0.5))
        low = surface_below(roots, x, z, b[1] + 0.01)
        if low == None and len(roots) == 0:
            low = surface_below(held, x, z, b[1] + 0.01)
        if low != None:
            result.append(["stem", x, z, low, b[1] + (b[4] - b[1]) * 0.4, width])
            continue
        target = held if len(roots) == 0 else roots
        result.append(["beam", [x, b[1], z], _nearest(target, x, b[1], z)])
    return result


def _nearest(tris: list[Any], x: float, y: float, z: float) -> list[float]:
    """Return the corner of `tris` nearest (x, y, z)."""
    best = math.inf
    point = [x, y, z]
    for tri in tris:
        for v in tri:
            p = v.position
            d = (p[0] - x) * (p[0] - x) + (p[1] - y) * (p[1] - y) + (p[2] - z) * (p[2] - z)
            if d < best:
                best = d
                point = p
    return point


def stems_drawing(stems: list[Any], neon: Any) -> Any:
    """Return the drawing (`draw(p)`) of `stems` (see `stems_for`), in the frames' dark metal."""
    look = BOSS_LOOK.frame

    def draw(p: Any) -> None:
        for stem in stems:
            if stem[0] == "stem":
                w = stem[5]
                height = stem[4] - stem[3]
                p.hull.box([w, height, w], look.metal, Placement([stem[1], stem[3], stem[2]]))
            else:
                draw_bridge(p, [stem[1], stem[2]], neon)

    return draw
