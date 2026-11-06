# Copyright (c) 2026 Renaud Guillon
"""MB-MONOLITH-ARRAY-02, FB-STAR-ENGINE-02: the machined solids of the L-10 Lab bosses.

Logical pixels, nose +Z, Y up (towards the camera). Faceted frustums (an obelisk's shaft, a
capstone, an arm's housing) built face by face from two outlines, and neon glyphs cut into their
faces. Shared by the Monolith Array and the Star Engine (both drawn from dark metal and stone, no
creature parts: the user's request of 2026-11-06).
"""

import math

from game.config.enemy_look import ENEMY_LOOK

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
# Dark stone and metal shades, from the darkest to the palest.
STONE = [0.07, 0.075, 0.085]
BASALT = [0.05, 0.052, 0.06]
STEEL = [0.13, 0.135, 0.15]
PALE = [0.22, 0.22, 0.24]


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _dot(a: Vec3, b: Vec3) -> float:
    return float(a[0] * b[0] + a[1] * b[1] + a[2] * b[2])


def _mean(points: list[Vec3]) -> Vec3:
    n = len(points)
    sx = 0.0
    sy = 0.0
    sz = 0.0
    for q in points:
        sx += q[0]
        sy += q[1]
        sz += q[2]
    return [sx / n, sy / n, sz / n]


def outward_face(builder: Any, corners: list[Vec3], color: Any, inside: Vec3) -> list[Vec3]:
    """Add a flat convex face, its corners turned so that it faces away from `inside`.

    Returns its corners in the order drawn (counter-clockwise seen from outside).
    """
    n = _cross(_sub(corners[1], corners[0]), _sub(corners[2], corners[0]))
    if _dot(n, _sub(_mean(corners), inside)) < 0:
        corners = [corners[len(corners) - 1 - k] for k in range(len(corners))]
    builder.face(corners, color)
    return corners


def frustum(
    builder: Any,
    outlines: list[Any],
    heights: list[Any],
    color: Any,
    top: Any = None,
) -> list[list[Vec3]]:
    """Add a faceted frustum from `outlines[0]` at `heights[0]` up to `outlines[1]` at `heights[1]`.

    The two outlines (model `[x, z]` points, as many, convex) give its foot and its head; its sides
    and its top cap (in `top`, the side colour when left out) are drawn, not its foot. Returns its
    side faces as drawn (four corners, counter-clockwise seen from outside), for glyphs.
    """
    low = outlines[0]
    high = outlines[1]
    y0 = heights[0]
    y1 = heights[1]
    n = len(low)
    feet = [[q[0], y0, q[1]] for q in low]
    heads = [[q[0], y1, q[1]] for q in high]
    middle = _mean([_mean(feet), _mean(heads)])
    sides: list[list[Vec3]] = []
    for i in range(n):
        j = (i + 1) % n
        sides.append(outward_face(builder, [feet[i], feet[j], heads[j], heads[i]], color, middle))
    outward_face(builder, heads, top if top != None else color, [middle[0], y1 - 1, middle[2]])
    return sides


def chamfered(at: list[Any], half: list[Any], cut: float) -> list[list[float]]:
    """Return a rectangle `2 half` across round model `[x, z]` `at`, its corners cut by `cut`."""
    x = at[0]
    z = at[1]
    w = half[0]
    d = half[1]
    return [
        [x + w, z - d + cut],
        [x + w, z + d - cut],
        [x + w - cut, z + d],
        [x - w + cut, z + d],
        [x - w, z + d - cut],
        [x - w, z - d + cut],
        [x - w + cut, z - d],
        [x + w - cut, z - d],
    ]


def _lerp(a: Vec3, b: Vec3, t: float) -> Vec3:
    return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]


def face_point(quad: list[Vec3], u: float, v: float) -> Vec3:
    """Return the point of a four-cornered face, `u` along its first edge, `v` towards its last."""
    return _lerp(_lerp(quad[0], quad[1], u), _lerp(quad[3], quad[2], u), v)


def glyph(builder: Any, quad: list[Vec3], box: list[Any], color: Any, lift: float = 0.18) -> None:
    """Add a lit glyph stroke on a side face: the patch `box` `[u0, u1, v0, v1]` of it.

    Lifted `lift` px off the face, outward, so that it shows over it.
    """
    corners = [
        face_point(quad, box[0], box[2]),
        face_point(quad, box[1], box[2]),
        face_point(quad, box[1], box[3]),
        face_point(quad, box[0], box[3]),
    ]
    # The face's outward normal (its corners run counter-clockwise seen from outside).
    n = _cross(_sub(quad[1], quad[0]), _sub(quad[2], quad[0]))
    length = math.sqrt(_dot(n, n)) or 1
    out = [n[0] / length, n[1] / length, n[2] / length]
    lifted = [[c[0] + out[0] * lift, c[1] + out[1] * lift, c[2] + out[2] * lift] for c in corners]
    outward_face(builder, lifted, color, _sub(_mean(lifted), out))


# Glyph patterns: strokes `[u0, u1, v0, v1]` on a face, cut like an alien script (a spine down
# the middle with ticks and boxes off it), one pattern per face in turn.
GLYPHS: list[Any] = [
    [
        [0.47, 0.53, 0.12, 0.86],
        [0.3, 0.47, 0.7, 0.74],
        [0.53, 0.72, 0.52, 0.56],
        [0.3, 0.47, 0.32, 0.36],
        [0.25, 0.3, 0.2, 0.36],
    ],
    [
        [0.2, 0.26, 0.15, 0.6],
        [0.26, 0.62, 0.55, 0.6],
        [0.62, 0.68, 0.4, 0.82],
        [0.42, 0.62, 0.3, 0.34],
        [0.4, 0.46, 0.68, 0.9],
    ],
    [
        [0.35, 0.65, 0.78, 0.82],
        [0.47, 0.53, 0.2, 0.78],
        [0.53, 0.75, 0.38, 0.42],
        [0.25, 0.47, 0.5, 0.54],
        [0.7, 0.75, 0.2, 0.38],
    ],
]


def glyphs(builder: Any, quad: list[Vec3], pattern: int, color: Any) -> None:
    """Add the glyph strokes of pattern `pattern` (see `GLYPHS`) on a side face."""
    for stroke in GLYPHS[pattern % len(GLYPHS)]:
        glyph(builder, quad, stroke, color)
