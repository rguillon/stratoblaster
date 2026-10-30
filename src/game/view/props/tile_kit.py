"""What the models made for the grid of tiles share (P15-R07, R09)

Each one fills a plot `w` × `d` world units (its tiles less the margin), centred on the origin,
standing on Y = 0, its front towards -Z.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from core.math.rng import Random  # noqa: E402

Rgb = list[float]
__pragma__("noskip")

from core.math.rng import create_rng, pick, random_in  # noqa: E402
from game.config.prop_look import PROP_COLORS as C  # noqa: E402
from game.config.prop_look import PROP_LIGHTS as L  # noqa: E402
from game.view.props.window_facades import facade_windows  # noqa: E402
from render.geometry.solids import Placement, SolidBuilder  # noqa: E402
from render.geometry.textured import QuadBuilder  # noqa: E402
from render.scenery.scenery_look import PropGeometry  # noqa: E402


class TileKit:
    """What a model of the grid is built with (`TileKit`): two solid builders (structure and
    lights), the windows' quads (D-210), the seeded random generator, the plot (`w` wide along X,
    `d` deep along Z), the size of a tile and the model's seed (some builders pick their shape by
    it)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        s: SolidBuilder,
        lights: SolidBuilder,
        random: Random,
        w: float,
        d: float,
        tile: float,
        seed: int,
    ) -> None:
        self.s = s
        self.lights = lights
        self.windows = QuadBuilder()
        self.random = random
        self.w = w
        self.d = d
        self.tile = tile
        self.seed = seed


def tile_kit(w: float, d: float, tile: float, seed: int) -> TileKit:
    """A kit for a plot of `w` × `d`, its random generator seeded from the model's seed."""
    return TileKit(
        SolidBuilder(True),
        SolidBuilder(True),
        create_rng(seed * 7919 + math.floor(w * 31 + d * 17 + 0.5)),
        w,
        d,
        tile,
        seed,
    )


def geometry_of(k: TileKit) -> PropGeometry:
    """The geometry a kit's builders made: the structure, the lights and the windows."""
    return PropGeometry(k.s.geometry, k.lights.geometry, None, k.windows.geometry)


def r(k: TileKit, span: list[float]) -> float:
    """A random number in `span` (a [low, high] pair)."""
    return random_in(k.random, span[0], span[1])


def any_of(k: TileKit, items: list[Any]) -> Any:
    """A random item of `items`."""
    return pick(k.random, items)


def plot(k: TileKit, color: Rgb, height: float = 0.2) -> None:
    """The ground of the plot, a little above the street: lawn, paving, sand, asphalt."""
    k.s.box([k.w, height, k.d], color)


def gable(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    k: TileKit,
    size: list[float],
    y: float,
    h: float,
    color: Rgb,
    at: list[float] = [0, 0],  # noqa: B006 (read only)
    along_z: bool = False,
) -> None:
    """A gabled roof over a `w` × `d` box at height `y`, its ridge `h` higher along X (along Z
    with `along_z`), centred on `at`."""
    w = size[0]
    d = size[1]
    a = d if along_z else w
    b = w if along_z else d
    place = Placement([at[0], 0, at[1]], math.pi / 2 if along_z else 0, 0, 0)
    k.s.face(
        [
            [-a / 2, y, -b / 2],
            [-a / 2, y + h, 0],
            [a / 2, y + h, 0],
            [a / 2, y, -b / 2],
        ],
        color,
        place,
    )
    k.s.face(
        [
            [a / 2, y, b / 2],
            [a / 2, y + h, 0],
            [-a / 2, y + h, 0],
            [-a / 2, y, b / 2],
        ],
        color,
        place,
    )
    k.s.face(
        [
            [-a / 2, y, b / 2],
            [-a / 2, y + h, 0],
            [-a / 2, y, -b / 2],
        ],
        C.concreteDark,
        place,
    )
    k.s.face(
        [
            [a / 2, y, -b / 2],
            [a / 2, y + h, 0],
            [a / 2, y, b / 2],
        ],
        C.concreteDark,
        place,
    )


def windows(
    k: TileKit,
    size: list[float],
    span: list[float],
    color: Rgb,
    at: list[float] = [0, 0],  # noqa: B006 (read only)
) -> None:
    """Windows round a `w` × `d` block at (x, z), from `y0` to `y1` (D-210: one quad per wall),
    tinted by `color`."""
    facade_windows(k.windows, k.random, [at[0], at[1], size[0], size[1]], span, color)


def tree(k: TileKit, x: float, z: float, size: float) -> None:
    """A round tree: a trunk and a low-poly crown."""
    k.s.cylinder(size * 0.12, size * 0.6, 5, C.bark, Placement([x, 0, z], 0, 0, 0))
    k.s.lathe(
        [
            [size * 0.45, size * 0.5],
            [size * 0.55, size * 0.9],
            [0, size * 1.4],
        ],
        6,
        any_of(k, [C.leaf, C.leafDark, C.leafLight]),
        Placement([x, 0, z], 0, 0, 0),
    )


def front_lights(k: TileKit, w: float, z: float, y: float, neon: Rgb) -> None:
    """A door light and a neon strip on the front of a block `w` wide whose front is at `z`."""
    k.lights.box([min(2, w / 3), 1.4, 0.3], L.window, Placement([0, 0.2, z - 0.2], 0, 0, 0))
    k.lights.box([w * 0.8, 0.3, 0.3], neon, Placement([0, y, z - 0.2], 0, 0, 0))


def lamp(k: TileKit, x: float, z: float, h: float = 4) -> None:
    """A lamp post at (x, z): a pole and a light on top, so lots and yards are lit at night."""
    k.s.box([0.25, h, 0.25], C.metal, Placement([x, 0, z], 0, 0, 0))
    k.lights.box([0.6, 0.4, 0.6], L.yellowDim, Placement([x, h, z], 0, 0, 0))


NEON = [L.cyan, L.pink, L.violet, L.red]
NEON_DIM = [L.cyanDim, L.pinkDim, L.whiteDim, L.yellowDim]


def js_remainder(a: int, b: int) -> int:
    """JavaScript's `a % b` (the sign of `a`), which the seeds' silhouettes are picked with."""
    # The quotient truncates towards zero, whatever the signs of `a` and `b`.
    quotient = math.floor(a / b) if a / b >= 0 else math.ceil(a / b)
    return a - b * quotient


def js_round(x: float) -> int:
    """`Math.round` (halves up), for the counts made from sizes."""
    return math.floor(x + 0.5)
