"""P07-R05 (phase 7 review: fat armour over a complex mechanism): chunky armour plates and the
machinery seen through the gaps between them: cogs, rams, cable bundles, ribbed conduits Logical
pixels, nose +Z, Y up (towards the camera).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.view.bosses.final_boss_greebles import rod  # noqa: E402
from render.geometry.outline import hypot2, hypot3  # noqa: E402
from render.geometry.solids import Placement, place_at  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Rgb = list[Any]
type Vec3 = list[Any]
__pragma__("noskip")

# The mechanism's shades: darker than the hull, so the gaps read as deep.
MECH = {
    "deep": [0.03, 0.03, 0.036],
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
    """A fat armour plate: the outline as straight walls from `y0` up to just under `y1`, then a
    `chamfer` wide bevel to its top, so its thickness shows at its edges."""
    y0 = heights[0]
    y1 = heights[1]
    waist = max(y0, y1 - chamfer * 0.8)
    the_top = color if top is None else top  # noqa: E711
    builder.bevel_slab(outline, [y0, waist, y1], [0, chamfer], color, None, the_top)


def _with_at(place: Any, at: Vec3) -> Any:
    """`{...place, at}`: `place` moved to `at` (an empty placement when `place` is left out)."""
    return place_at(Placement() if place == None else place, at)  # noqa: E711


def cog(
    builder: Any,
    at: Vec3,
    sizes: list[Any],
    teeth: int,
    place: Any = None,
) -> None:
    """A cog lying flat at `at`: a toothed disc `radius` wide (`teeth` teeth), `thick` thick,
    turned `yaw`; a lighter hub on it. `sizes` is `[radius, thick]`."""
    radius = sizes[0]
    thick = sizes[1]
    points = teeth * 4
    outline: list[Any] = []
    for k in range(points):
        a = (2 * math.pi * k) / points
        r = radius if k % 4 < 2 else radius * 0.8  # noqa: PLR2004
        outline.append([math.sin(a) * r, math.cos(a) * r])
    builder.slab(outline, [0, thick], MECH["metal"], _with_at(place, at), MECH["bright"])
    builder.cylinder(radius * 0.35, thick + 0.4, 6, MECH["bright"], _with_at(place, at))


def ram(builder: Any, start: Vec3, end: Vec3, radius: float) -> None:
    """A hydraulic ram from `start` to `end`: a fat dark cylinder, then its bright rod."""
    mid = [
        start[0] + (end[0] - start[0]) * 0.55,
        start[1] + (end[1] - start[1]) * 0.55,
        start[2] + (end[2] - start[2]) * 0.55,
    ]
    rod(builder, start, mid, radius, MECH["metal"])
    rod(builder, mid, end, radius * 0.55, MECH["bright"])
    builder.box([radius * 2.6, radius * 2, radius * 2.6], MECH["deep"], Placement(start))


def cables(builder: Any, start: Vec3, end: Vec3, spec: list[Any]) -> None:
    """`count` cables side by side (across X, `gap` apart) from `start` to `end`: a cable bundle.
    `spec` is `[count, gap, radius]`."""
    count = spec[0]
    gap = spec[1]
    radius = spec[2]
    for i in range(count):
        dx = (i - (count - 1) / 2) * gap
        color = MECH["metal"] if i % 2 == 0 else MECH["deep"]
        rod(
            builder,
            [start[0] + dx, start[1], start[2]],
            [end[0] + dx, end[1], end[2]],
            radius,
            color,
        )


def conduit(builder: Any, start: Vec3, end: Vec3, spec: list[Any]) -> None:
    """A ribbed conduit from `start` to `end`: a pipe with `ribs` collars along it. `spec` is
    `[radius, ribs]`."""
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
    """A glowing line deep in a gap from `a` to `b` at height `y`: a lit conduit (neon or
    charge). `ends` is `[a, b]`."""
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


def well(builder: Any, outline: list[Any], y: float) -> None:
    """A dark recess floor `outline` at height `y`: the bottom of a gap the mechanism sits in."""
    builder.slab(outline, [y - 0.4, y], MECH["deep"])
