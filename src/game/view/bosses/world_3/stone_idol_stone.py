"""P09-R09, 3-3: the carved stone, moss, vines and neon cracks of the Lost temples' bosses (the
Stone Idol and the Sky Temple; World 3 theme: dark metal with neon, plus moss, vines and stone).
Ported from `view/bosses/world-3/stone-idol-stone.ts`. Logical pixels, nose +Z, Y up."""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.record import record
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from render.geometry.solids import SolidBuilder  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
type Flat = list[float]
__pragma__("noskip")

# Stone and jungle shades (vertex colours, multiplied into the hull's dark metal).
STONE = record(
    {
        # Weathered stone on the top faces, catching the light.
        "light": [0.34, 0.32, 0.28],
        # Carved stone.
        "base": [0.23, 0.22, 0.2],
        # Stone in shadow: recesses, the undersides.
        "dark": [0.13, 0.12, 0.11],
        # Deep cuts: sockets, doorways, the mouth.
        "deep": [0.04, 0.04, 0.045],
        # Moss, and older moss in the cracks.
        "moss": [0.14, 0.46, 0.07],
        "mossDark": [0.08, 0.3, 0.04],
        # Vines and their leaves.
        "vine": [0.07, 0.3, 0.04],
        "leaf": [0.12, 0.52, 0.06],
        # Old gilding on carved stone.
        "gilt": [0.6, 0.45, 0.14],
    }
)


def bar(builder: SolidBuilder, a: Vec3, b: Vec3, dims: list[float], color: Rgb) -> None:
    """A straight bar from `a` to `b` (3D), `dims[0]` across and `dims[1]` high: a vine, a
    cable."""
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    dz = b[2] - a[2]
    length = math.hypot(dx, dy, dz)
    if length == 0:
        return
    width = dims[0]
    thick = dims[1]
    builder.box(
        [width, thick, length],
        color,
        Placement(
            [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - thick / 2, (a[2] + b[2]) / 2],
            math.atan2(dx, dz),
            -math.asin(dy / length),
        ),
    )


def leaf(hull: SolidBuilder, at: Vec3, size: float, turn: float) -> None:
    """A leaf at `at`, `size` long, turned by its index."""
    blade: list[list[float]] = [
        [0, 0],
        [size * 0.35, size * 0.5],
        [0, size],
        [-size * 0.35, size * 0.5],
    ]
    hull.slab(blade, [0, 0.3], STONE.leaf, Placement(at, turn * 2.1 + 0.5))


def vine(hull: SolidBuilder, path: list[Vec3], width: float = 1.1) -> None:
    """A vine along `path` (3D points), with a leaf at every other joint."""
    for i in range(len(path) - 1):
        a = path[i]
        b = path[i + 1]
        bar(hull, a, b, [width, width * 0.8], STONE.vine)
        if i % 2 == 0:
            leaf(hull, a, width * 2.2, i)


def moss(hull: SolidBuilder, at: Vec3, size: float, turn: float = 0) -> None:
    """A patch of moss on a top face at `at`, `size` across: a low, faceted cushion."""
    hull.cylinder(size, size * 0.18, 6, STONE.mossDark, Placement(at, turn), size * 0.75)
    hull.cylinder(size * 0.6, size * 0.3, 5, STONE.moss, Placement(at, turn + 0.7), size * 0.35)


def crack(neon: SolidBuilder, path: list[Flat], y: float, color: Rgb, width: float = 0.6) -> None:
    """A neon crack along `path` (XZ) at height `y`: thin lit strips, `width` wide."""
    for i in range(len(path) - 1):
        a = path[i]
        b = path[i + 1]
        bar(neon, [a[0], y, a[1]], [b[0], y, b[1]], [width, 0.3], color)
