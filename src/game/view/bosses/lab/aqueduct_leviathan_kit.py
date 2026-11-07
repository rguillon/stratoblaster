# Copyright (c) 2026 Renaud Guillon
"""Drawing helpers of the Aqueduct Leviathan (FB-AQUEDUCT-LEVIATHAN-01 to -05).

Logical pixels, nose +Z, Y up (towards the camera). Its stone, its water, and the pieces several
of its drawings share: an iron arch rib, a stretch of its water channel, a hatch and its frame.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.aqueduct_leviathan import (
    CHANNEL_FLOOR,
    CHANNEL_HALF,
    CHANNEL_TOP,
    SPRING,
    WATER,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.world_1_organic_kit import M
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["aqueduct-leviathan"]
QUARTER = math.pi / 2
# Dressed stone (pale, cool grey) and its darker courses; the water's body.
STONE = [0.2, 0.21, 0.23]
COURSE = [0.12, 0.125, 0.14]
WATER_BODY = [0.06, 0.12, 0.18]
# How many voussoirs an arch rib is made of.
VOUSSOIRS = 7


def pt(x: float, y: float, h: float) -> Vec3:
    """Return the playfield point `(x, y)` at height `h` in model space."""
    return boss_point(x, y, h)


def flat(x: float, y: float) -> list[Any]:
    """Return the playfield point `(x, y)` as a model outline point `[x, z]`."""
    return [-x, -y]


def box_outline(b: list[Any]) -> list[list[Any]]:
    """Return the model outline of the playfield box `[x0, x1, y0, y1]`."""
    return [flat(b[0], b[2]), flat(b[1], b[2]), flat(b[1], b[3]), flat(b[0], b[3])]


def block(builder: Any, b: list[Any], heights: list[Any], color: Any) -> None:
    """Add the playfield box `b` (`[x0, x1, y0, y1]`) between `heights` to `builder`."""
    at = pt((b[0] + b[1]) / 2, (b[2] + b[3]) / 2, heights[0])
    builder.box([b[1] - b[0], heights[1] - heights[0], b[3] - b[2]], color, Placement(at))


def rib(p: Any, x0: float, x1: float, y0: float, y1: float) -> None:
    """Add an iron arch rib from `x0` to `x1`, its faces at `y0`, `y1`: voussoirs on a half circle.

    A lit keystone at its crown.
    """
    c = (x0 + x1) / 2
    w = (x1 - x0) / 2
    depth = y1 - y0
    ym = (y0 + y1) / 2
    seg = math.pi * w / VOUSSOIRS * 1.08
    for k in range(VOUSSOIRS):
        t = math.pi * (k + 0.5) / VOUSSOIRS
        # Model X is the playfield's -x: the half circle from x1 over to x0.
        mx = -c + w * math.cos(t)
        h = SPRING + w * math.sin(t)
        place = Placement([mx, h, -ym], 0, 0, t + QUARTER)
        p.hull.box([seg, 2.4, depth], M.base if k % 2 == 0 else M.panel, place)
    crown = pt(c, ym, SPRING + w - 2.4)
    p.neon.box([1.6, 2.6, depth + 0.3], N, Placement(crown))


def channel(p: Any, x0: float, x1: float) -> None:
    """Add a stretch of the water channel from `x0` to `x1`: its trough, its glowing water."""
    half = CHANNEL_HALF
    block(p.hull, [x0, x1, -half, half], [CHANNEL_FLOOR, CHANNEL_FLOOR + 1], M.base)
    for side in [-1, 1]:
        wall = [x0, x1, side * half - 0.6, side * half + 0.6]
        block(p.hull, wall, [CHANNEL_FLOOR, CHANNEL_TOP], STONE)
        p.neon.box(
            [x1 - x0 - 0.6, 0.3, 0.4], N, Placement(pt((x0 + x1) / 2, side * half, CHANNEL_TOP))
        )
    block(p.hull, [x0, x1, -half + 0.6, half - 0.6], [CHANNEL_FLOOR + 1, WATER], WATER_BODY)
    p.neon.box([x1 - x0 - 0.6, 0.2, 1.2], N, Placement(pt((x0 + x1) / 2, 0, WATER)))


def hatch(at: list[Any], half: list[Any], heights: list[Any]) -> Any:
    """Return the drawing of a hatch round `at` (BOSS-58): an armoured cap, ribbed, a lit seam."""

    def draw(p: Any) -> None:
        b = [at[0] - half[0], at[0] + half[0], at[1] - half[1], at[1] + half[1]]
        top = heights[1]
        p.hull.bevel_slab(
            box_outline(b), [heights[0], top - 0.8, top], [0, 0.8], M.panel, None, M.base
        )
        c = pt(at[0], at[1], top)
        for k in [-1, 1]:
            p.bare.box(
                [0.5, 0.4, 2 * half[1] - 2],
                M.dark,
                Placement([c[0] + k * half[0] * 0.45, top, c[2]]),
            )
        p.neon.box(
            [2 * half[0] - 1.6, 0.35, 0.4], N, Placement([c[0], top - 0.5, c[2] + half[1] - 0.1])
        )

    return draw


def hatch_frame(at: list[Any], half: list[Any], h: float) -> Any:
    """Return what a hatch leaves (BOSS-44): a dark collar round the opening, a lit lip."""

    def draw(p: Any) -> None:
        c = pt(at[0], at[1], h)
        for dz in [-1, 1]:
            p.hull.box(
                [2 * half[0], 1.2, 1],
                M.base,
                Placement([c[0], h - 0.6, c[2] + dz * (half[1] - 0.5)]),
            )
        for dx in [-1, 1]:
            p.hull.box(
                [1, 1.2, 2 * half[1]],
                M.base,
                Placement([c[0] + dx * (half[0] - 0.5), h - 0.6, c[2]]),
            )
        p.neon.box([2 * half[0] - 1, 0.3, 0.3], N, Placement([c[0], h + 0.6, c[2] + half[1] - 0.5]))

    return draw
