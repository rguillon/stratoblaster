# Copyright (c) 2026 Renaud Guillon
"""What the models made for the grid of tiles share (GFX-BLDG-03, GFX-BLDG-09).

Each one fills a plot `w` x `d` world units (its tiles less the margin), centred on the origin,
standing on Y = 0, its front towards -Z.
"""

import math

from core.math.rng import create_rng, pick, random_in
from game.config.prop_look import PROP_COLORS as C
from game.config.prop_look import PROP_LIGHTS as L
from game.config.window_look import DOOR_STYLES
from game.view.props.window_facades import doorway, facade_windows, wall_windows
from render.geometry.solids import Placement, SolidBuilder
from render.geometry.textured import QuadBuilder
from render.scenery.scenery_look import PropGeometry

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Sequence
from typing import Any

from core.math.rng import Random

Rgb = list[float]
# __pragma__ ("noskip")


class TileKit:
    """What a model of the grid is built with (`TileKit`).

    Two solid builders (structure and lights), the windows' quads (D-210), the seeded random
    generator, the plot (`w` wide along X, `d` deep along Z), the size of a tile and the model's
    seed (some builders pick their shape by it).
    """

    def __init__(
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
    """Return a kit for a plot of `w` x `d`, its random generator seeded from the model's seed."""
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
    """Return the geometry a kit's builders made: the structure, the lights and the windows.

    These are the parts of a model (GFX-PROP-04).
    """
    return PropGeometry(k.s.geometry, k.lights.geometry, None, k.windows.geometry)


def r(k: TileKit, span: list[float]) -> float:
    """Return a random number in `span` (a [low, high] pair)."""
    return random_in(k.random, span[0], span[1])


def any_of(k: TileKit, items: list[Any]) -> Any:
    """Return a random item of `items`."""
    return pick(k.random, items)


def plot(k: TileKit, color: Rgb, height: float = 0.2) -> None:
    """Add the ground of the plot, a little above the street: lawn, paving, sand, asphalt."""
    k.s.box([k.w, height, k.d], color)


def gable(
    k: TileKit,
    size: list[float],
    y: float,
    h: float,
    color: Rgb,
    at: Sequence[float] = (0, 0),
    along_z: bool = False,
) -> None:
    """Add a gabled roof over a `w` x `d` box at height `y`.

    Its ridge is `h` higher along X (along Z with `along_z`), centred on `at`.
    """
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
    at: Sequence[float] = (0, 0),
    style: int | None = None,
) -> None:
    """Windows round a `w` x `d` block at (x, z), from `y0` to `y1`.

    One quad per wall (D-210), tinted by `color`, of `style` (`WINDOW_STYLES`) or one at random.
    """
    facade_windows(k.windows, k.random, [at[0], at[1], size[0], size[1]], span, color, False, style)


def front_windows(
    k: TileKit,
    face: list[float],
    size: list[float],
    style: int,
    color: Rgb,
) -> None:
    """Add the windows of one wall facing -Z or +Z.

    `face` is `[x, z, facing]`, `size` is `[width, y0, y1]`; one quad of `style` (D-215,
    GFX-BLDG-14: a glass front, a hut's window).
    """
    wall_windows(k.windows, k.random, face, size, style, color)


def door(k: TileKit, at: list[float], door_style: int, color: Rgb, facing: float = -1) -> None:
    """Add a door of `door_style` (`DOOR_STYLES`) on a wall facing -Z (or +Z).

    Its foot's middle is at `at` (`[x, y, z]`), tinted by `color` (D-215: one quad from the windows'
    atlas).
    """
    doorway(k.windows, k.random, at, facing, door_style, color)


def tree(k: TileKit, x: float, z: float, size: float) -> None:
    """Add a round tree: a trunk and a low-poly crown."""
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
    """Add a door and a neon strip on the front of a block `w` wide, whose front is at `z`.

    The door is one quad from the windows' atlas; the strip is one of the lights (D-215,
    GFX-BLDG-16).
    """
    door(k, [0, 0, z], DOOR_STYLES.door, L.window)
    k.lights.box([w * 0.8, 0.3, 0.3], neon, Placement([0, y, z - 0.2], 0, 0, 0))


def lamp(k: TileKit, x: float, z: float, h: float = 4) -> None:
    """Add a lamp post at (x, z): a pole and a light on top, so lots and yards are lit at night."""
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
