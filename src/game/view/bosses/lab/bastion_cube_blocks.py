# Copyright (c) 2026 Renaud Guillon
"""MB-BASTION-CUBE-05: the Bastion Cube's corner blocks, moving pieces of their own (BOSS-45).

Each a square bastion block filling a corner notch of the plinth, crenellated along its outer
walls, a drum tower standing on it: the front ones carry the towers' crowns (the parts), the rear
ones a capped roof the gatlings ride out on. Drawn at rest; the engine slides them out diagonally
as it transforms. Logical pixels, nose +Z, Y up (towards the camera); shapes are given in config
coordinates (X right, Y up the screen) and turned into model space here.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.bastion_cube import (
    CORNER_TOP,
    HALF,
    NOTCH,
    TOWER_AT,
    TOWER_RADIUS,
    TOWER_TOP,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.final_boss_greebles import SHADE, plate
from game.view.bosses.final_boss_shapes import edge_strips
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["bastion-cube"]
# A merlon on the battlements: its width, height and depth.
MERLON = [2.8, 2.2, 2.8]
# How far below a front tower's top its drum ends (its crown, the part, stands on it).
CROWN = 2.6


def pt(x: float, y: float, h: float) -> Vec3:
    """Return the config point `(x, y)` at height `h` in model space."""
    return boss_point(x, y, h)


def model_outline(outline: list[Any]) -> list[Any]:
    """Return a config outline as a model outline (`[x, z]` points)."""
    return [[-q[0], -q[1]] for q in outline]


def square(centre: list[Any], half: float) -> list[Any]:
    """Return a square `half` px either side of `centre` (config)."""
    x = centre[0]
    y = centre[1]
    return [[x - half, y - half], [x + half, y - half], [x + half, y + half], [x - half, y + half]]


def merlons(p: Any, ends: list[Any], count: int, h: float, dx: float, dy: float) -> None:
    """Add `count` merlons from `ends[0]` to `ends[1]` (config) on a wall top at height `h`.

    Moved `dx`, `dy` px (config) towards the wall's outer face.
    """
    a = ends[0]
    b = ends[1]
    for k in range(count):
        t = k / (count - 1) if count > 1 else 0.5
        x = a[0] + (b[0] - a[0]) * t + dx
        y = a[1] + (b[1] - a[1]) * t + dy
        p.hull.box(MERLON, SHADE["mid"], Placement(pt(x, y, h - 0.2)), SHADE["light"])


def _block(p: Any, sx: float, sy: float) -> None:
    """Draw the block of the corner `sx`, `sy` (config signs): its slab, plates and battlements."""
    inner = NOTCH - 0.6
    outline = [
        [sx * inner, sy * inner],
        [sx * HALF, sy * inner],
        [sx * HALF, sy * HALF],
        [sx * inner, sy * HALF],
    ]
    p.hull.bevel_slab(
        model_outline(outline), [0, CORNER_TOP - 1.4, CORNER_TOP], [0, 1.1], SHADE["dark"]
    )
    mid = (NOTCH + HALF) / 2
    for q in [[NOTCH + 3.4, HALF - 3.4], [HALF - 3.4, NOTCH + 3.4]]:
        corner = [sx * q[0], sy * q[1]]
        tile = [corner, [corner[0], sy * mid], [sx * mid, sy * mid], [sx * mid, corner[1]]]
        plate(p.hull, model_outline(tile), CORNER_TOP, SHADE["panel"], 0.4)
    # Battlements along its two outer walls, and the lit line under them.
    wall = HALF - 1.5
    merlons(p, [[sx * wall, sy * (NOTCH + 2)], [sx * wall, sy * (HALF - 2)]], 3, CORNER_TOP, 0, 0)
    merlons(p, [[sx * (NOTCH + 2), sy * wall], [sx * (HALF - 6), sy * wall]], 2, CORNER_TOP, 0, 0)
    lit = [
        [-sx * (HALF + 0.1), -sy * (NOTCH + 0.5)],
        [-sx * (HALF + 0.1), -sy * (HALF + 0.1)],
        [-sx * (NOTCH + 0.5), -sy * (HALF + 0.1)],
    ]
    edge_strips(p.neon, lit, 0.5, [CORNER_TOP - 4.6, CORNER_TOP - 3.8], N)
    # The slide's shoes at its inner corner, lit: they ride the notch's rails.
    p.neon.box(
        [1.6, 0.6, 1.6], N, Placement(pt(sx * (NOTCH + 1.6), sy * (NOTCH + 1.6), CORNER_TOP))
    )


def _drum(p: Any, sx: float, sy: float, top: float) -> None:
    """Draw a corner block's drum tower up to `top`: a flared foot, arrow slits, a lit band."""
    at = pt(sx * TOWER_AT[0], -sy * TOWER_AT[1], 0)
    r = TOWER_RADIUS
    place = Placement(at, math.pi / 8)
    p.hull.lathe(
        [
            [r + 2.2, CORNER_TOP - 0.4],
            [r + 0.4, CORNER_TOP + 2.2],
            [r, CORNER_TOP + 2.6],
            [r, top],
            [0, top],
        ],
        8,
        SHADE["base"],
        place,
    )
    p.neon.ring(r + 0.15, 0.6, 8, N, Placement([at[0], top - 3.2, at[2]], math.pi / 8))
    for k in range(4):
        a = k * math.pi / 2
        slit = [at[0] + math.cos(a) * (r - 0.2), CORNER_TOP + 3.6, at[2] + math.sin(a) * (r - 0.2)]
        p.hull.box([1.2, 2.4, 1.2], SHADE["dark"], Placement(slit, a))


def _front(sx: float) -> Any:
    """Return the drawing of the front block on the config side `sx` (its drum, without crown)."""

    def draw(p: Any) -> None:
        _block(p, sx, -1)
        _drum(p, sx, -1, TOWER_TOP - CROWN)
        # The seat the tower's turret stands on, inside its crown.
        at = pt(sx * TOWER_AT[0], TOWER_AT[1], TOWER_TOP - CROWN)
        p.hull.cylinder(TOWER_RADIUS - 1.8, CROWN, 8, SHADE["dark"], Placement(at, math.pi / 8))

    return draw


def _rear(sx: float) -> Any:
    """Return the drawing of the rear block on the config side `sx`: its drum under a capped roof.

    The roof's lit hatch is where its gatling rises.
    """

    def draw(p: Any) -> None:
        _block(p, sx, 1)
        _drum(p, sx, 1, TOWER_TOP)
        at = pt(sx * TOWER_AT[0], -TOWER_AT[1], TOWER_TOP)
        p.hull.cylinder(TOWER_RADIUS + 0.8, 1, 8, SHADE["mid"], Placement(at, math.pi / 8))
        p.neon.ring(TOWER_RADIUS - 2.6, 0.5, 8, N, Placement([at[0], TOWER_TOP + 0.9, at[2]]))
        p.hull.cylinder(TOWER_RADIUS - 2.8, 0.4, 8, SHADE["dark"], Placement(at))

    return draw


def cube_blocks() -> Any:
    """Return the corner blocks' drawings by region id (`drawing.armour`); config right is +X."""
    return {
        "front-blocks-right": {"whole": _front(1)},
        "front-blocks-left": {"whole": _front(-1)},
        "rear-blocks-right": {"whole": _rear(1)},
        "rear-blocks-left": {"whole": _rear(-1)},
    }
