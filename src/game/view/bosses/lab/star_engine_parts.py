# Copyright (c) 2026 Renaud Guillon
"""FB-STAR-ENGINE-03, FB-STAR-ENGINE-05: the Star Engine's emitters and armour.

Logical pixels, nose +Z, Y up (towards the camera). Each emitter is a hexagonal housing at an arm's
tip, its rotor's seat on top and three blades fanning out past it (the star's points); the vanes,
the cowls and the keel are the armour it sheds (dark metal plates, neon edges).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.star_engine import (
    COWL_OUTLINE,
    KEEL_HEIGHTS,
    KEEL_OUTLINE,
    PLATE_HEIGHTS,
    TIP_ROTOR_HEIGHT,
    VANE_OUTLINE,
    star_point,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.lab.monolith_array_kit import BASALT, PALE, STEEL, STONE
from game.view.enemies.enemy_shapes import decal
from render.geometry.organic import tendril
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["star-engine"]
# An emitter's housing (a lathe profile, radius and height): a hexagonal block narrowing to the
# rotor's seat.
HOUSING = [
    [9.6, 1.5],
    [10.2, 5],
    [9.4, 10],
    [7.4, 14.5],
    [6.2, TIP_ROTOR_HEIGHT - 0.4],
    [0, TIP_ROTOR_HEIGHT - 0.4],
]


def model_xz(point: list[Any]) -> list[float]:
    """Return the model `[x, z]` of the config point `[x, y]`."""
    return [-point[0], -point[1]]


def star_model(angle: float, radius: float, height: float) -> Vec3:
    """Return the model point `radius` px out, `angle` degrees from the nose, `height` high."""
    q = star_point(angle, radius)
    return boss_point(q[0], q[1], height)


def _out(at: Vec3, distance: float, turn: float, height: float) -> Vec3:
    """Return the model point `distance` px out from `at`, away from the centre, turned `turn`."""
    r = math.hypot(at[0], at[2]) or 1
    a = math.atan2(at[0] / r, at[2] / r) + turn
    return [at[0] + math.sin(a) * distance, height, at[2] + math.cos(a) * distance]


def emitter(p: Any, at: Vec3) -> None:
    """Add an arm's emitter (FB-STAR-ENGINE-03): a hexagonal housing at the arm's tip.

    Its rotor's seat on top (its mount, BOSS-58), a ring of light round it, three blades fanning out
    past it, the long one the star's point, lit at its tip.
    """
    yaw = math.atan2(at[0], at[2])
    p.hull.lathe(HOUSING, 6, STEEL, Placement(at, yaw))
    p.neon.ring(10.05, 0.7, 6, N, Placement([at[0], 6.2, at[2]], yaw))
    p.hull.cylinder(5.2, 0.5, 8, PALE, Placement([at[0], TIP_ROTOR_HEIGHT - 0.45, at[2]]))
    p.neon.ring(5.3, 0.3, 8, N, Placement([at[0], TIP_ROTOR_HEIGHT - 0.6, at[2]]))
    tendril(p.hull, [_out(at, 7, 0, 6), _out(at, 25, 0, 4.5)], [3.4, 0], 4, STONE)
    tendril(p.neon, [_out(at, 21.5, 0, 6.6), _out(at, 25.3, 0, 5.3)], [0.7, 0], 4, N)
    for s in [-1, 1]:
        tendril(p.hull, [_out(at, 7, s * 0.7, 6), _out(at, 15, s * 0.5, 4)], [2, 0], 4, BASALT)


def _sided(outline: list[Any], s: float) -> list[list[float]]:
    """Return a config outline drawn on the right (+X) on side `s`, as model `[x, z]` points."""
    return [model_xz([s * q[0], q[1]]) for q in outline]


def _plates(p: Any, outline: list[Any], angle: float, vents: bool) -> None:
    """Add a deck sector's armour plate on both sides, centred on `angle` degrees.

    A bevelled plate, a ridge along its middle, a neon stroke on its outer edge; slatted vents on
    it when `vents`.
    """
    low = PLATE_HEIGHTS[0]
    top = PLATE_HEIGHTS[1]
    for s in [-1, 1]:
        p.hull.bevel_slab(_sided(outline, s), [low, top - 1.6, top], [0, 1.2], STEEL, None, STONE)
        a = s * angle
        tendril(
            p.hull,
            [star_model(a, 28, top - 0.2), star_model(a, 37, top - 0.6)],
            [1.3, 0.5],
            4,
            BASALT,
        )
        for k in range(3):
            d = (k - 1) * 9
            decal(p.neon, [model_xz(q) for q in _stroke(a + d, 35.2, 36.4, 3.2)], top + 0.05, N)
        if vents:
            for k in range(3):
                r = 29 + k * 2.4
                decal(
                    p.hull,
                    [model_xz(q) for q in _stroke(a - 6.5, r, r + 1.1, 4)],
                    top + 0.05,
                    BASALT,
                )
                decal(
                    p.hull,
                    [model_xz(q) for q in _stroke(a + 6.5, r, r + 1.1, 4)],
                    top + 0.05,
                    BASALT,
                )


def _stroke(angle: float, r0: float, r1: float, half: float) -> list[list[float]]:
    """Return a short band from `r0` to `r1` out, `half` degrees either side of `angle` (config)."""
    return [
        star_point(angle - half, r0),
        star_point(angle + half, r0),
        star_point(angle + half, r1),
        star_point(angle - half, r1),
    ]


def draw_vanes(p: Any) -> None:
    """Draw the vanes (FB-STAR-ENGINE-05): plates over the deck between the nose and side arms."""
    _plates(p, VANE_OUTLINE, 36, False)


def draw_cowls(p: Any) -> None:
    """Draw the cowls (FB-STAR-ENGINE-05): vented plates between the side and the back arms."""
    _plates(p, COWL_OUTLINE, 108, True)


def draw_keel(p: Any) -> None:
    """Draw the keel (FB-STAR-ENGINE-05): a ridged plate along the nose arm, chevrons of light."""
    low = KEEL_HEIGHTS[0]
    top = KEEL_HEIGHTS[1]
    p.hull.bevel_slab(
        [model_xz(q) for q in KEEL_OUTLINE], [low, top - 1.4, top], [0, 1.4], STEEL, None, STONE
    )
    tendril(
        p.hull,
        [boss_point(0, -29, top - 0.2), boss_point(0, -47, top - 0.4)],
        [1.1, 1.1],
        4,
        BASALT,
    )
    for k in range(3):
        y = -33 - k * 5
        for s in [-1, 1]:
            band = [[s * 1.6, y], [s * 5, y + 2.6], [s * 5, y + 3.6], [s * 1.6, y + 1]]
            decal(p.neon, [model_xz(q) for q in band], top + 0.05, N)


def star_armour() -> Any:
    """Return the Star Engine's armour drawings by region id (`drawing.armour`, D-254)."""
    return {
        "vanes": {"whole": draw_vanes},
        "cowls": {"whole": draw_cowls},
        "keel": {"whole": draw_keel},
    }
