"""The World 2 frost on the Fjord Lynx and the Harbour Kraken: snow caps, ice crust and icicles
over the dark metal Logical pixels, nose +Z,
Y up (towards the camera).
"""

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

# Packed snow on top faces: pale blue-white.
SNOW = [0.78, 0.84, 0.92]
# Ice crust and icicles: a colder, darker blue.
ICE = [0.55, 0.68, 0.82]
# A frosted panel: metal under a thin rime.
RIME = [0.36, 0.4, 0.47]


def snow_cap(
    hull: SolidBuilder,
    outline: list[OutlinePoint],
    y: float,
    place: Placement | None = None,
) -> None:
    """A snow cap: `outline` a little proud of the surface at height `y`, rounded at its edges."""
    hull.bevel_slab(outline, [y - 0.3, y, y + 0.7], [0, 0.5], SNOW, place)


def icicles(hull: SolidBuilder, points: list[Vec3], length: float) -> None:
    """Icicles hanging under the points given, `length` long at most (they vary a little)."""
    for i in range(len(points)):
        at = points[i]
        k = 0.6 + 0.4 * (((i * 7) % 5) / 4)
        hull.cylinder(0.7, length * k, 3, ICE, Placement(at, i, math.pi), 0)


def spread(a: Vec3, b: Vec3, count: int) -> list[Vec3]:
    """`count` points evenly spread from `a` to `b` (ends included)."""
    result: list[Vec3] = []
    for i in range(count):
        t = i / (count - 1) if count > 1 else 0.5
        result.append(
            [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]
        )
    return result
