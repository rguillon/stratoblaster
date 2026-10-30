"""The badges of the bonuses (P11-R07), ported from `bonuses/bonus-geometry.ts`.

Each badge is radius 1 in the XY plane, facing -Z, built as coloured flat polygons.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from render.geometry.gradient_shapes import ColoredGeometry  # noqa: E402


def _new_geometry() -> ColoredGeometry:
    """An empty geometry: positions, indices and colours, all flat arrays."""
    return ColoredGeometry()


def _polygon(geo: Any, points: list[list[float]], z: float, color: list[float]) -> None:
    """Adds a flat convex polygon (XY plane, at `z`) of one colour to `geo`."""
    base = len(geo.positions) // 3
    for p in points:
        geo.positions.append(p[0])
        geo.positions.append(p[1])
        geo.positions.append(z)
        geo.colors.append(color[0])
        geo.colors.append(color[1])
        geo.colors.append(color[2])
        geo.colors.append(1)
    for i in range(1, len(points) - 1):
        geo.indices.append(base)
        geo.indices.append(base + i)
        geo.indices.append(base + i + 1)


def _hexagon(r: float) -> list[list[float]]:
    """The corners of a hexagon of radius `r`, flat side down."""
    return [[math.cos((math.pi / 3) * i) * r, math.sin((math.pi / 3) * i) * r] for i in range(6)]


def _chevron(top: float, thick: float) -> list[list[list[float]]]:
    """One chevron pointing up, its tip at (0, `top`), arms `thick` thick."""
    w = 0.45
    drop = 0.42
    return [
        [
            [-w, top - drop],
            [0, top],
            [0, top - thick],
            [-w, top - drop - thick],
        ],
        [
            [0, top],
            [w, top - drop],
            [w, top - drop - thick],
            [0, top - thick],
        ],
    ]


def build_bonus_badge(colors: Any) -> ColoredGeometry:
    """The badge of a weapon bonus: a dark hexagon in a coloured frame (inner edge at `inset`),
    with two chevrons pointing up in front of it."""
    geo = _new_geometry()
    outer = _hexagon(1)
    inner = _hexagon(colors.inset)
    _polygon(geo, inner, 0, colors.face)
    for i, corner in enumerate(outer):
        nxt = (i + 1) % 6
        quad = [corner, outer[nxt], inner[nxt], inner[i]]
        _polygon(geo, quad, 0, colors.frame)
    for top in [0.48, 0.08]:
        for arm in _chevron(top, 0.2):
            _polygon(geo, arm, -0.02, colors.chevrons)
    return geo


def _circle(cx: float, cy: float, r: float, sides: int = 14) -> list[list[float]]:
    """The corners of a regular polygon of `sides` around (`cx`, `cy`), radius `r`."""
    return [
        [
            cx + math.cos(((2 * math.pi) / sides) * i) * r,
            cy + math.sin(((2 * math.pi) / sides) * i) * r,
        ]
        for i in range(sides)
    ]


def _heart(geo: Any, s: float, z: float, color: list[float]) -> None:
    """Adds a heart of size `s` (two lobes over a point, within radius `s`) at depth `z`."""
    lobe = 0.36 * s
    _polygon(geo, _circle(-0.34 * s, 0.24 * s, lobe), z, color)
    _polygon(geo, _circle(0.34 * s, 0.24 * s, lobe), z, color)
    _polygon(
        geo,
        [
            [-0.68 * s, 0.16 * s],
            [0, -0.8 * s],
            [0.68 * s, 0.16 * s],
            [0, 0.3 * s],
        ],
        z,
        color,
    )


def build_life_badge(colors: Any) -> ColoredGeometry:
    """The badge of a life bonus (P11-R07): a heart in a coloured rim, a lighter heart in front of
    it. A heart, so it reads without colour."""
    geo = _new_geometry()
    _heart(geo, 1, 0, colors.rim)
    _heart(geo, colors.inset, -0.02, colors.heart)
    return geo


def _rect(x0: float, y0: float, x1: float, y1: float) -> list[list[float]]:
    """Axis-aligned rectangle from (`x0`, `y0`) to (`x1`, `y1`)."""
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _letter_b(h: float) -> list[list[list[float]]]:
    """The blocky strokes of a letter B, `h` high, centred on the origin."""
    w = 0.62 * h
    t = 0.2 * h
    left = -w / 2
    right = w / 2
    top = h / 2
    bottom = -h / 2
    return [
        _rect(left, bottom, left + t, top),
        _rect(left, top - t, right - t, top),
        _rect(left, -t / 2, right - t, t / 2),
        _rect(left, bottom, right - t, bottom + t),
        _rect(right - t, t / 2, right, top - t),
        _rect(right - t, bottom + t, right, -t / 2),
    ]


def build_bomb_badge(colors: Any) -> ColoredGeometry:
    """The badge of a bomb bonus (P11-R07): a round shell with a highlight and a letter B in front.
    Round and lettered, so it reads without colour."""
    geo = _new_geometry()
    _polygon(geo, _circle(0, 0, 1, 18), 0, colors.shell)
    _polygon(geo, _circle(-0.38, 0.4, 0.26, 10), -0.01, colors.highlight)
    for stroke in _letter_b(1):
        _polygon(geo, stroke, -0.02, colors.letter)
    return geo
