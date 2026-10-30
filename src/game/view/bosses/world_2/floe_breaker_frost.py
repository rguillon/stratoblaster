"""The frost on the 2-1 bosses (World 2 theme: dark metal with neon, plus frost, ice and snow),
ported from `bosses/world-2/floe-breaker-frost.ts`. Logical pixels, nose +Z, Y up. Pale vertex
colours on the hull's top faces.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.record import record
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from render.geometry.outline import OutlinePoint  # noqa: E402
from render.geometry.solids import SolidBuilder  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")

# Frost shades: snow caps, frosted panels, clear blue ice.
FROST = record(
    {
        # Snow and ice crust on top faces.
        "snow": [0.75, 0.82, 0.9],
        # A frosted panel: hull metal under a thin rime.
        "panel": [0.42, 0.48, 0.56],
        # Clear ice: icicles, chunks of floe stuck on the hull.
        "ice": [0.5, 0.66, 0.82],
    }
)


def icicle(hull: SolidBuilder, at: Vec3, length: float) -> None:
    """An icicle hanging from `at`, `length` long: a thin four-sided cone pointing down."""
    hull.cylinder(length * 0.22, length, 4, FROST.ice, Placement(at, 0, math.pi), 0)


def icicles(hull: SolidBuilder, outline: list[OutlinePoint], y: float, every: int) -> None:
    """Icicles under every `every`-th corner of `outline` at height `y`, of varying lengths."""
    for i in range(len(outline)):
        if i % every == 0:
            icicle(hull, [outline[i][0] * 0.97, y, outline[i][1] * 0.97], 2.5 + (i % 3))


def ice_chunk(hull: SolidBuilder, at: Vec3, size: float) -> None:
    """A chunk of floe ice stuck on the hull at `at`, `size` across: a low faceted lump."""
    lump = [
        [size, 0],
        [size * 1.1, size * 0.35],
        [size * 0.6, size * 0.8],
        [0, size * 0.9],
    ]
    hull.lathe(lump, 5, FROST.ice, Placement(at, size))
