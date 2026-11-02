# Copyright (c) 2026 Renaud Guillon
"""BOSS-49 (phase 7 review: fat armour over a complex mechanism).

Chunky armour plates and the machinery seen through the gaps between them: ribbed conduits and
glowing lines. Logical pixels, nose +Z, Y up (towards the camera).
"""

from game.view.bosses.final_boss_greebles import rod
from render.geometry.outline import hypot2, hypot3

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Rgb = list[Any]
type Vec3 = list[Any]
# __pragma__ ("noskip")


# The mechanism's shades: darker than the hull, so the gaps read as deep.
MECH = {
    "metal": [0.085, 0.085, 0.1],
    "bright": [0.3, 0.29, 0.33],
}


def armour(
    builder: Any,
    outline: list[Any],
    heights: list[Any],
    color: Rgb,
    chamfer: float = 1.4,
    top: Any = None,
) -> None:
    """Add a fat armour plate whose thickness shows at its edges.

    The outline as straight walls from `y0` up to just under `y1`, then a `chamfer` wide bevel to
    its top.
    """
    y0 = heights[0]
    y1 = heights[1]
    waist = max(y0, y1 - chamfer * 0.8)
    the_top = color if top is None else top
    builder.bevel_slab(outline, [y0, waist, y1], [0, chamfer], color, None, the_top)


def conduit(builder: Any, start: Vec3, end: Vec3, spec: list[Any]) -> None:
    """Add a ribbed conduit from `start` to `end`: a pipe with `ribs` collars along it.

    `spec` is.

    `[radius, ribs]`.
    """
    radius = spec[0]
    ribs = spec[1]
    rod(builder, start, end, radius, MECH["metal"])
    for k in range(1, ribs + 1):
        t = k / (ribs + 1)
        at = [
            start[0] + (end[0] - start[0]) * t,
            start[1] + (end[1] - start[1]) * t,
            start[2] + (end[2] - start[2]) * t,
        ]
        step = 0.25 / hypot3(end[0] - start[0], end[1] - start[1], end[2] - start[2])
        stop = [
            at[0] + (end[0] - start[0]) * step * 2,
            at[1] + (end[1] - start[1]) * step * 2,
            at[2] + (end[2] - start[2]) * step * 2,
        ]
        rod(builder, at, stop, radius * 1.45, MECH["bright"])


def glow_line(builder: Any, ends: list[Any], y: float, color: Rgb) -> None:
    """Add a glowing line deep in a gap from `a` to `b` at height `y`.

    A lit conduit (neon or charge). `ends` is `[a, b]`.
    """
    a = ends[0]
    b = ends[1]
    dx = b[0] - a[0]
    dz = b[1] - a[1]
    length = hypot2(dx, dz) or 1
    nx = (-dz / length) * 0.4
    nz = (dx / length) * 0.4
    builder.slab(
        [
            [a[0] + nx, a[1] + nz],
            [b[0] + nx, b[1] + nz],
            [b[0] - nx, b[1] - nz],
            [a[0] - nx, a[1] - nz],
        ],
        [y, y + 0.5],
        color,
    )
