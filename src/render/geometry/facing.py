# Copyright (c) 2026 Renaud Guillon
"""Faces a camera above can never see, left out of a model.

A model only ever seen from above (an enemy under the playfield camera) never shows the faces that
point down: whatever its turn, and however the tilted camera looks at it, it sees them from behind.
Leaving them out halves its undersides. Pure: no Babylon; Y is up and a triangle's Babylon front
normal is `(p2 - p0) x (p1 - p0)`, as in `edge_trim.py`.
"""

import math

from render.geometry.gradient_shapes import ColoredGeometry


def faces_down(positions: list[float], a: int, b: int, c: int, limit: float) -> bool:
    """Whether the triangle `a b c` (vertex numbers) faces down: its unit normal's Y <= `limit`.

    A degenerate triangle (no area) is kept: it is not said to face down.
    """
    ax, ay, az = positions[3 * a], positions[3 * a + 1], positions[3 * a + 2]
    ux = positions[3 * c] - ax
    uy = positions[3 * c + 1] - ay
    uz = positions[3 * c + 2] - az
    vx = positions[3 * b] - ax
    vy = positions[3 * b + 1] - ay
    vz = positions[3 * b + 2] - az
    nx = uy * vz - uz * vy
    ny = uz * vx - ux * vz
    nz = ux * vy - uy * vx
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    if length < 1e-9:
        return False
    return ny / length <= limit


def seen_from_above(geo: ColoredGeometry, limit: float) -> ColoredGeometry:
    """Return `geo` without its triangles facing down (unit normal Y at most `limit`, negative).

    Only the vertices the triangles kept use are kept, renumbered in order.
    """
    positions = geo.positions
    colors = geo.colors
    indices = geo.indices
    result = ColoredGeometry()
    renumbered: dict[int, int] = {}
    for t in range(len(indices) // 3):
        corners = [indices[3 * t], indices[3 * t + 1], indices[3 * t + 2]]
        if faces_down(positions, corners[0], corners[1], corners[2], limit):
            continue
        for v in corners:
            if v not in renumbered:
                renumbered[v] = len(result.positions) // 3
                result.positions.extend([
                    positions[3 * v],
                    positions[3 * v + 1],
                    positions[3 * v + 2],
                ])
                result.colors.extend([
                    colors[4 * v],
                    colors[4 * v + 1],
                    colors[4 * v + 2],
                    colors[4 * v + 3],
                ])
            result.indices.append(renumbered[v])
    return result
