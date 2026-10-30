"""Shapes of the enemy models

The outlines are `(x, z)` pairs and the sections `(u, v)` pairs; a loft section is a list of
those pairs (`SolidBuilder.loft`).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402
from typing import Any  # noqa: E402

# A point in model space: x, y, z.
type Vec3 = list[float]
# A point of an outline on the ground plane: x, z.
type OutlinePoint = list[float]
# A point of a loft section: u (across), v (up).
type SectionPoint = list[float]
__pragma__("noskip")


def radial(angle: float, r: float, y: float) -> list[float]:
    """A point `r` from the model's centre in the direction `angle` (radians from +Z towards
    +X)."""
    return [math.sin(angle) * r, y, math.cos(angle) * r]


def around(count: int) -> list[float]:
    """`count` angles evenly spread around the circle, the first one on +Z (the nose)."""
    return [(2 * math.pi * i) / count for i in range(count)]


def shift_x(outline: Sequence[OutlinePoint], dx: float) -> list[OutlinePoint]:
    """The outline moved by `dx` across."""
    return [[p[0] + dx, p[1]] for p in outline]


def flip_x(outline: Sequence[OutlinePoint]) -> list[OutlinePoint]:
    """The outline mirrored left to right (for the other wing)."""
    return [[-p[0], p[1]] for p in outline]


# Both sides: -1 (left) and 1 (right).
SIDES = [-1, 1]  # type: list[int]

# Loft cross-sections (`SolidBuilder.loft`), counter-clockwise seen from the nose. A hull: flat
# belly and back, its widest point a chine low on the sides.
HULL_SECTION = [  # type: list[SectionPoint]
    [0.55, 0],
    [1, 0.4],
    [0.6, 1],
    [-0.6, 1],
    [-1, 0.4],
    [-0.55, 0],
]

# A fighter's fuselage: chines low on the sides, then shoulders and a ridge on its back where a
# canopy is painted (`canopy_paint`) instead of stuck on as another solid.
FIGHTER_SECTION = [  # type: list[SectionPoint]
    [0.5, 0],
    [1, 0.3],
    [0.6, 0.6],
    [0.3, 0.85],
    [0, 1],
    [-0.3, 0.85],
    [-0.6, 0.6],
    [-1, 0.3],
    [-0.5, 0],
]

# The sides of `FIGHTER_SECTION` on its back, from shoulder to shoulder.
CANOPY_SIDES = [2, 3, 4, 5]  # type: list[int]


def canopy_paint(bands: Sequence[int], color: Sequence[float]) -> Callable[[int, int], Any]:
    """Paints the back of a `FIGHTER_SECTION` loft `color` between the given stations."""

    def paint(side: int, band: int) -> Any:
        if side in CANOPY_SIDES and band in bands:
            return color
        return None

    return paint


# A round-ish pod or boom: a hexagon.
POD_SECTION = [  # type: list[SectionPoint]
    [0.5, 0],
    [1, 0.5],
    [0.5, 1],
    [-0.5, 1],
    [-1, 0.5],
    [-0.5, 0],
]

# A canopy or dorsal ridge sitting on a hull: open at the bottom (loft it with `open`).
CANOPY_SECTION = [  # type: list[SectionPoint]
    [1, 0],
    [0.7, 0.6],
    [0, 1],
    [-0.7, 0.6],
    [-1, 0],
]


def angry_eyes(
    center: Sequence[float], gap: float, size: Sequence[float], slant: float
) -> list[list[OutlinePoint]]:
    """Two eye slits on either side of `center`, `gap` apart, each `length` long and `width`
    deep, their outer ends swept back by `slant` radians: a frown seen from above."""
    cx = center[0]
    cz = center[1]
    length = size[0]
    width = size[1]
    slits: list[list[OutlinePoint]] = []
    for s in SIDES:
        inner: OutlinePoint = [cx + (s * gap) / 2, cz]
        outer: OutlinePoint = [
            inner[0] + s * length * math.cos(slant),
            cz - length * math.sin(slant),
        ]
        slits.append([inner, outer, [outer[0], outer[1] - width], [inner[0], inner[1] - width]])
    return slits


def decal(
    builder: object, outline: Sequence[OutlinePoint], y: float, color: Sequence[float]
) -> None:
    """A flat convex outline at height `y`, facing up: a light painted on a hull (2 triangles a
    quad)."""
    n = len(outline)
    area = 0.0
    for i in range(n):
        x1 = outline[i][0]
        z1 = outline[i][1]
        x2 = outline[(i + 1) % n][0]
        z2 = outline[(i + 1) % n][1]
        area += x1 * z2 - x2 * z1
    # Facing up (+Y) takes clockwise corners in (x, z).
    corners: list[OutlinePoint] = []
    if area > 0:
        for i in range(n - 1, -1, -1):
            corners.append(outline[i])
    else:
        corners = list(outline)
    builder.face([[p[0], y, p[1]] for p in corners], color)  # type: ignore[attr-defined]


def side_stripe(
    section: Sequence[SectionPoint], side: int, span: Sequence[float], lift: float = 1.04
) -> list[SectionPoint]:
    """A two-point section on side `side` of `section`, from `t0` to `t1` of its length, lifted
    `lift` times off the axis: lofted with `open`, a stripe painted along that side of a hull."""
    n = len(section)
    ua, va = section[side] if 0 <= side < n else [0, 0]
    ub, vb = section[(side + 1) % n] if 0 <= (side + 1) % n < n else [0, 0]
    t0 = span[0]
    t1 = span[1]

    def at(t: float) -> SectionPoint:
        return [(ua + (ub - ua) * t) * lift, va + (vb - va) * t]

    return [at(t0), at(t1)]


# P16-R03: a lean rounded section for the basic kinds' swollen bodies (`segmentedBody`): a flat
# belly, round flanks and a soft back, in seven facets.
LOBE_SECTION = [  # type: list[SectionPoint]
    [0.4, 0],
    [1, 0.35],
    [0.75, 0.85],
    [0, 1],
    [-0.75, 0.85],
    [-1, 0.35],
    [-0.4, 0],
]
