"""P09-R09, 3-2: the jungle on the 3-2 bosses (the Toucan and the Canopy Spider): moss on their
plates, vines hanging along them, leaves (GD-61, World 3: dark metal with neon, plus moss, vines
and stone). Ported from `view/bosses/world-3/toucan-jungle.ts`. Logical pixels, nose +Z, Y up."""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from render.geometry.outline import OutlinePoint  # noqa: E402
from render.geometry.solids import SolidBuilder  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

# Moss: a deep green, and a lighter one where the light catches it.
MOSS = [0.13, 0.24, 0.08]
MOSS_LIT = [0.22, 0.36, 0.1]
# Vines and their leaves.
VINE = [0.1, 0.17, 0.06]
LEAF = [0.16, 0.32, 0.09]


def segment(
    builder: SolidBuilder,
    ends: list[Vec3],
    radii: list[float],
    color: Rgb,
    sides: int = 6,
) -> None:
    """A cylinder from `ends[0]` (radius `radii[0]`) to `ends[1]` (`radii[1]`), `sides` facets: a
    strut, a leg, a vine. Pitched off +Y, then yawed, so that its axis runs along the segment."""
    a = ends[0]
    b = ends[1]
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    dz = b[2] - a[2]
    length = math.hypot(dx, dy, dz)
    pitch = math.atan2(math.hypot(dx, dz), dy)
    builder.cylinder(
        radii[0],
        length,
        sides,
        color,
        Placement(a, math.atan2(dx, dz), pitch),
        radii[1],
    )


def moss(hull: SolidBuilder, at: Vec3, radius: float, seed: float = 0) -> None:
    """A patch of moss `radius` wide lying at `at` (its top a little above it): an uneven, low
    hexagon, lighter on top. `seed` turns and bends its outline so no two patches look alike."""
    outline: list[OutlinePoint] = []
    for k in range(6):
        a = (k * math.pi) / 3 + seed
        r = radius * (0.75 + 0.25 * math.sin(seed * 3.1 + k * 2.3))
        outline.append([math.cos(a) * r, math.sin(a) * r])
    hull.bevel_slab(
        outline,
        [-0.3, 0, 0.9],
        [0, radius * 0.25],
        MOSS,
        Placement(at),
        MOSS_LIT,
    )


def vine(hull: SolidBuilder, points: list[Vec3], thickness: float = 0.5) -> None:
    """A vine along `points`, a thin stem from one to the next, a leaf at every other joint (a
    small slab turned along the stem)."""
    for i in range(len(points) - 1):
        a = points[i]
        b = points[i + 1]
        segment(hull, [a, b], [thickness, thickness], VINE, 4)
        if i % 2 == 1:
            continue
        leaf: list[OutlinePoint] = [[0, 0], [1.2, 1.4], [0, 3], [-1.2, 1.4]]
        yaw = math.atan2(b[0] - a[0], b[2] - a[2]) + (1 if i % 4 == 0 else -1)
        hull.slab(leaf, [0, 0.3], LEAF, Placement(b, yaw))


def sagging(a: Vec3, b: Vec3, count: int, sag: float) -> list[Vec3]:
    """`count` points from `a` to `b`, sagging `sag` down (-Y) in the middle: a hanging vine."""
    result: list[Vec3] = []
    for i in range(count):
        t = i / (count - 1)
        drop = sag * 4 * t * (1 - t)
        result.append(
            [
                a[0] + (b[0] - a[0]) * t,
                a[1] + (b[1] - a[1]) * t - drop,
                a[2] + (b[2] - a[2]) * t,
            ]
        )
    return result
