"""P07-R05 (phase 7 review: more detail, some asymmetry): surface details of the World 1 mini
bosses, ported from `bosses/mini-boss-greebles.ts`. Logical pixels, nose +Z, Y up. Details are
flat-shaded hull pieces a little proud of the surface, so they read from above under the ~35°
camera.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.view.bosses.mini_boss_shapes import SHADE, H  # noqa: E402
from render.geometry.outline import hypot2  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Rgb = list[Any]
type Vec3 = list[Any]
__pragma__("noskip")


def rect(w: float, d: float) -> list[Any]:
    """A rectangle `w` wide (X) and `d` deep (Z) around the origin."""
    return [
        [-w / 2, -d / 2],
        [w / 2, -d / 2],
        [w / 2, d / 2],
        [-w / 2, d / 2],
    ]


def plate(
    hull: Any,
    outline: list[Any],
    heights: list[Any],
    color: Rgb,
    place: Any = None,
) -> None:
    """A plate: `outline` raised `thick` above the surface at height `y`, its top edge chamfered.
    `heights` is `[y, thick]`."""
    y = heights[0]
    thick = heights[1]
    hull.bevel_slab(outline, [y - 0.4, y, y + thick], [0, min(thick, 0.7)], color, place)


def seam(
    hull: Any,
    a: list[Any],
    b: list[Any],
    sizes: list[Any],
    color: Rgb = H.dark,
) -> None:
    """A thin raised strip on the surface at height `y`, from `a` to `b`: a seam, a cable, a rail.
    `sizes` is `[y, width, height]`."""
    dx = b[0] - a[0]
    dz = b[1] - a[1]
    hull.box(
        [sizes[1], sizes[2], hypot2(dx, dz)],
        color,
        Placement([(a[0] + b[0]) / 2, sizes[0], (a[1] + b[1]) / 2], math.atan2(dx, dz)),
    )


def cable(
    hull: Any,
    path: list[Any],
    y: float,
    width: float,
    color: Rgb = H.dark,
) -> None:
    """Strips along a path of points at height `y`, `width` wide: a cable run, a pipe."""
    for i in range(len(path) - 1):
        seam(hull, path[i], path[i + 1], [y, width, width * 0.8], color)


def vent(hull: Any, at: Vec3, size: list[Any], slats: int, yaw: float = 0) -> None:
    """A vent at `at` (its top surface), `w` by `d`, turned by `yaw`: a dark recess, `slats`
    slats."""
    w = size[0]
    d = size[1]
    hull.box([w, 0.3, d], H.dark, Placement(at, yaw))
    pitch = d / slats
    for i in range(slats):
        along = (i + 0.5) * pitch - d / 2
        sx = math.sin(yaw) * along
        sz = math.cos(yaw) * along
        hull.box(
            [w * 0.86, 0.7, pitch * 0.4],
            H.panel,
            Placement([at[0] + sx, at[1], at[2] + sz], yaw),
        )


def hazard(hull: Any, at: Vec3, size: list[Any], count: int, yaw: float = 0) -> None:
    """Hazard stripes on a `w` by `d` patch at `at`: `count` bands across, paint and dark metal."""
    w = size[0]
    d = size[1]
    band = w / count
    for i in range(count):
        across = (i + 0.5) * band - w / 2
        sx = math.cos(yaw) * across
        sz = -math.sin(yaw) * across
        color = SHADE["hazard"] if i % 2 == 0 else H.dark
        hull.box(
            [band, 0.4, d],
            color,
            Placement([at[0] + sx, at[1], at[2] + sz], yaw),
        )


def mast(parts: Any, at: Vec3, height: float, color: Rgb) -> None:
    """An antenna mast standing at `at`, `height` tall, a light of `color` on its tip."""
    parts.hull.cylinder(0.9, 1.2, 6, H.panel, Placement(at))
    parts.hull.cylinder(0.45, height, 4, H.dark, Placement(at), 0.3)
    parts.hull.box(
        [3.2, 0.5, 0.5],
        H.panel,
        Placement([at[0], at[1] + height * 0.65, at[2]]),
    )
    parts.neon.box([0.9, 0.9, 0.9], color, Placement([at[0], at[1] + height, at[2]]))


def dish(hull: Any, at: Vec3, radius: float, tilt: float, yaw: float = 0) -> None:
    """A radar dish at `at`, `radius` wide, tipped back by `tilt` and turned by `yaw`."""
    hull.cylinder(0.8, 2, 4, H.dark, Placement(at))
    bowl = [
        [0.3, 0],
        [radius, radius * 0.35],
        [radius * 0.8, radius * 0.45],
        [0, radius * 0.2],
    ]
    hull.lathe(
        bowl,
        8,
        SHADE["edge"],
        Placement([at[0], at[1] + 2, at[2]], yaw, tilt),
    )


def lamps(neon: Any, points: list[Vec3], size: float, color: Rgb) -> None:
    """Small lights of `color` at each point, `size` across."""
    for at in points:
        neon.box([size, size * 0.6, size], color, Placement(at))
