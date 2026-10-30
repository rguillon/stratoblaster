"""Glow shapes of the shots (discs, swirls, streaks and bars)

Each builder returns a `ColoredGeometry`: positions, indices and vertex colours (RGBA) that the
render layer turns into a mesh. Colours are `[r, g, b]` lists in 0..1.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.geometry.gradient_shapes import ColoredGeometry

__pragma__("jsmod")

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Sequence  # noqa: E402
from typing import Any  # noqa: E402

Rgb = Sequence[float]
__pragma__("noskip")

# The guards of the builders: a ring needs 3 sides, a streak 2 colours and 2 rows.
MIN_SEGMENTS = 3
MIN_COLOURS = 2
MIN_ROWS = 2


def _range_error(message: str) -> None:
    """Throws a JavaScript RangeError."""
    __pragma__("js", "{}", "throw new RangeError(message);")


def _empty_geometry() -> ColoredGeometry:
    """A geometry with no vertices yet."""
    return ColoredGeometry()


def _mirrored_columns(count: int) -> list[int]:
    """Colour indices `count-1 .. 0` then `1 .. count-1` (the reversed keys, then the keys after
    the first)."""
    columns: list[int] = []
    for i in range(count - 1, -1, -1):
        columns.append(i)
    for i in range(1, count):
        columns.append(i)
    return columns


def build_glow_disc(segments: int, colors: Sequence[Rgb]) -> ColoredGeometry:
    """A disc of radius 1 in the XY plane, made of `rings` rings of `segments` sides: `colors[0]`
    at the centre, `colors[i]` on ring `i`. Drawn with additive blending, a black outer ring
    fades out, which gives the blob its soft edge."""
    return build_swirl(segments, colors, {"lobes": 0, "depth": 0, "twist": 0})


def build_swirl(segments: int, colors: Sequence[Rgb], shape: dict[str, float]) -> ColoredGeometry:
    """A `build_glow_disc` bent into curled arms, like a spiral galaxy: each ring's radius swells
    on the arms and shrinks between them, and each ring is turned by `twist` × its radius, so the
    arms curl outwards. Spun, it churns like plasma.

    `shape` holds `lobes` (number of arms, 0: a round disc), `depth` (0..1: how far the gaps
    between the arms reach, relative to the radius) and `twist` (radians each arm turns by, from
    the centre out to the rim)."""
    if segments < MIN_SEGMENTS or len(colors) < MIN_COLOURS:
        _range_error("Need 3 segments and 2 colours")
    lobes = shape["lobes"]
    depth = shape["depth"]
    twist = shape["twist"]
    geo = _empty_geometry()
    center = colors[0]
    geo.positions.extend([0, 0, 0])
    geo.colors.extend(center)
    geo.colors.append(1)
    rings = len(colors) - 1
    for ring in range(1, rings + 1):
        radius = ring / rings
        rgb = colors[ring]
        for i in range(segments):
            angle = (2 * math.pi * i) / segments
            r = radius * (1 - depth * (0.5 - 0.5 * math.cos(lobes * angle)))
            turned = angle + twist * radius
            geo.positions.extend([math.cos(turned) * r, math.sin(turned) * r, 0])
            geo.colors.extend(rgb)
            geo.colors.append(1)
    for i in range(segments):
        nxt = (i + 1) % segments
        geo.indices.extend([0, 1 + i, 1 + nxt])
    for ring in range(1, rings):
        inner = 1 + (ring - 1) * segments
        outer = inner + segments
        for i in range(segments):
            nxt = (i + 1) % segments
            geo.indices.extend(
                [inner + i, outer + i, outer + nxt, inner + i, outer + nxt, inner + nxt]
            )
    return geo


def build_tracer(colors: Sequence[Rgb], rows: Sequence[dict[str, Any]]) -> ColoredGeometry:
    """A streak along Y, X in [-0.5, 0.5]: across its width `colors` go from the centre line to
    both edges (like `build_glow_bar`); along it, each row at Y = `at` multiplies them by `tint`.
    With additive blending, a black row fades the streak out there."""
    if len(colors) < MIN_COLOURS or len(rows) < MIN_ROWS:
        _range_error("Need 2 colours and 2 rows")
    geo = _empty_geometry()
    steps = len(colors) - 1
    columns = _mirrored_columns(len(colors))
    for row, spec in enumerate(rows):
        at = spec["at"]
        tint = spec["tint"]
        for col, c in enumerate(columns):
            rgb = colors[c]
            geo.positions.extend([col / (2 * steps) - 0.5, at, 0])
            geo.colors.extend([rgb[0] * tint[0], rgb[1] * tint[1], rgb[2] * tint[2], 1])
            if row > 0 and col > 0:
                a = (row - 1) * len(columns) + col - 1
                b = a + len(columns)
                geo.indices.extend([a, b, b + 1, a, b + 1, a + 1])
    return geo


def build_glow_bar(colors: Sequence[Rgb]) -> ColoredGeometry:
    """A bar from Y = 0 to Y = 1, X in [-0.5, 0.5], coloured across its width: `colors[0]` on
    the centre line out to the last colour on both edges. Scaled in X and Y, it draws a beam."""
    if len(colors) < MIN_COLOURS:
        _range_error("Need 2 colours")
    geo = _empty_geometry()
    steps = len(colors) - 1
    # Columns from the left edge to the right edge, through the centre.
    columns = _mirrored_columns(len(colors))
    for col, c in enumerate(columns):
        x = col / (2 * steps) - 0.5
        rgb = colors[c]
        geo.positions.extend([x, 0, 0, x, 1, 0])
        geo.colors.extend(rgb)
        geo.colors.append(1)
        geo.colors.extend(rgb)
        geo.colors.append(1)
        if col > 0:
            a = (col - 1) * 2
            geo.indices.extend([a, a + 2, a + 3, a, a + 3, a + 1])
    return geo
