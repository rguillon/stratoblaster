# Copyright (c) 2026 Renaud Guillon
"""FB-OVERLORD-02: the Overlord's city: shared shapes.

Rectangles and symmetric outlines for its deck, neon edges. Model space: logical pixels, nose +Z
(down the screen), Y up towards the camera; +X is the screen's left.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.view.enemies.enemy_shapes import flip_x

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Rgb = list[Any]
type Vec3 = list[Any]
# __pragma__ ("noskip")


# Purple: the boss's neon (BOSS-50, FB-OVERLORD-04).
OVERLORD_NEON = BOSS_LOOK.neon["overlord"]
# Heights of the deck's top and of the raised boulevard along its middle.
OVERLORD_DECK = {"top": 6, "boulevard": 10}


def box2d(w: float, d: float, at: Any = None) -> list[Any]:
    """Return a rectangle `w` wide and `d` long around (x, z)."""
    x = 0 if at == None else at[0]
    z = 0 if at == None else at[1]
    return [
        [x - w / 2, z - d / 2],
        [x + w / 2, z - d / 2],
        [x + w / 2, z + d / 2],
        [x - w / 2, z + d / 2],
    ]


def symmetric(half: list[Any], nose: Any = None) -> list[Any]:
    """Return a symmetric outline from its right half (x > 0, from the front to the tail).

    Closed across the nose at `nose` on the axis.
    """
    result: list[Any] = []
    if nose != None:
        result.append([0, nose])
    result.extend(half)
    mirror = flip_x(half)
    result.extend([mirror[i] for i in range(len(mirror) - 1, -1, -1)])
    return result


def _area(outline: list[Any]) -> float:
    """Twice the signed area of an outline in (x, z)."""
    total = 0.0
    n = len(outline)
    for i in range(n):
        p = outline[i]
        q = outline[(i + 1) % n]
        total = total + p[0] * q[1] - q[0] * p[1]
    return total


def _lifted(p: Any, y: float, nx: float, nz: float) -> Vec3:
    """Return the point `p` at height `y`, moved by `[nx, nz]`."""
    return [p[0] + nx, y, p[1] + nz]


def edge_lights(
    neon: Any,
    outline: list[Any],
    edges: list[int],
    heights: list[Any],
    color: Rgb,
    lift: float = 0.35,
) -> None:
    """Add neon walls along the edges `edges` of `outline` (edge i from point i to the next).

    They run from `heights[0]` to `heights[1]`, stood `lift` outside the outline: lit edges with
    nothing hidden inside the hull.
    """
    y0 = heights[0]
    y1 = heights[1]
    area = _area(outline)
    # Counter-clockwise in (x, z), the outside is on the right of each edge, (dz, -dx).
    out = 1 if area > 0 else -1
    n = len(outline)
    for i in edges:
        p = outline[i]
        q = outline[(i + 1) % n]
        px = p[0]
        pz = p[1]
        qx = q[0]
        qz = q[1]
        length = math.hypot(qx - px, qz - pz) or 1
        nx = (out * lift * (qz - pz)) / length
        nz = (-out * lift * (qx - px)) / length
        if out > 0:
            a = [px, pz]
            b = [qx, qz]
        else:
            a = [qx, qz]
            b = [px, pz]
        neon.face(
            [
                _lifted(a, y0, nx, nz),
                _lifted(a, y1, nx, nz),
                _lifted(b, y1, nx, nz),
                _lifted(b, y0, nx, nz),
            ],
            color,
        )
