# Copyright (c) 2026 Renaud Guillon
"""FB-THRONE-OF-STORMS-05: the Throne of Storms' moving towers and the armour it sheds.

Its four corner towers, moving pieces of their own (BOSS-45): round drum towers on the curtain
wall's corners, sliding out on their rails at its first transformation; the front ones carry the
towers' crowns (the parts), the rear ones a flat roof the cannons ride out on. Its ward's plating
and curtain wall in sectors (BOSS-42), bursting off at its second; the hatch over the spire
rotor. Logical pixels, nose +Z, Y up (towards the camera); shapes are given in config coordinates (X
right, Y up the screen) and turned into model space here.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.throne_of_storms import (
    KEEP_R,
    KEEP_TOP,
    ROCK_TOP,
    ROTOR_AT,
    TOWER_AT,
    TOWER_R,
    TOWER_TOP,
    WALL_IN,
    WALL_OUT,
    WALL_TOP,
    WARD_TOP,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.final_boss_greebles import SHADE
from game.view.bosses.final_boss_shapes import edge_strips
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["throne-of-storms"]
DEG = math.pi / 180
# Stone: the castle's walls and towers, a cold blue-grey (it keeps a little colour, BOSS-50).
STONE = [0.34, 0.37, 0.42]
STONE_DARK = [0.2, 0.22, 0.26]
STONE_LIGHT = [0.46, 0.5, 0.55]
# How far below a front tower's top its drum ends (its crown, the part, stands on it).
CROWN = 2.6


def pt(x: float, y: float, h: float) -> Vec3:
    """Return the config point `(x, y)` at height `h` in model space."""
    return boss_point(x, y, h)


def polar(r: float, deg: float) -> list[float]:
    """Return the config point `r` px out on the bearing `deg` (degrees from +X, anticlockwise)."""
    return [r * math.cos(deg * DEG), r * math.sin(deg * DEG)]


def arc(r_in: float, r_out: float, degs: list[float], step: float) -> list[Any]:
    """Return an annular sector's outline in model space (`[x, z]` points), `step` degrees apart."""
    count = max(1, math.ceil((degs[1] - degs[0]) / step))
    outer: list[Any] = []
    inner: list[Any] = []
    for k in range(count + 1):
        a = degs[0] + (degs[1] - degs[0]) * k / count
        o = polar(r_out, a)
        i = polar(r_in, a)
        outer.append([-o[0], -o[1]])
        inner.append([-i[0], -i[1]])
    outer.extend([inner[len(inner) - 1 - k] for k in range(len(inner))])
    return outer


def _sector(p: Any, degs: list[float]) -> None:
    """Draw the ward's plating and the curtain wall between the bearings `degs` (FB-...-11).

    The ward: plated flagstones from the keep to the wall, a seam of light along its middle. The
    wall: a thick stone arc, a walk of light round its outer face and merlons along its top.
    """
    p.hull.bevel_slab(
        arc(KEEP_R + 1, WALL_IN + 0.5, degs, 15),
        [ROCK_TOP - 0.5, WARD_TOP - 0.8, WARD_TOP],
        [0, 0.8],
        SHADE["panel"],
        None,
        SHADE["light"],
    )
    p.hull.bevel_slab(
        arc(WALL_IN, WALL_OUT, degs, 7.5),
        [ROCK_TOP - 0.5, WALL_TOP - 1.4, WALL_TOP],
        [0, 1],
        STONE,
        None,
        STONE_LIGHT,
    )
    # The ward's seam of light, and radial plate lines across it.
    mid = (KEEP_R + WALL_IN) / 2
    p.neon.bevel_slab(
        arc(mid - 0.3, mid + 0.3, degs, 7.5), [WARD_TOP, WARD_TOP, WARD_TOP + 0.12], [0, 0], N
    )
    a = degs[0] + 5
    while a < degs[1] - 2:
        q0 = polar(KEEP_R + 2, a)
        q1 = polar(WALL_IN - 1, a)
        edge_strips(
            p.hull,
            [[-q0[0], -q0[1]], [-q1[0], -q1[1]]],
            0.5,
            [WARD_TOP, WARD_TOP + 0.15],
            SHADE["dark"],
        )
        a += 15
    # The wall's walk of light round its outer face, and its merlons.
    walk = [polar(WALL_OUT + 0.1, degs[0] + (degs[1] - degs[0]) * k / 6) for k in range(7)]
    edge_strips(p.neon, [[-q[0], -q[1]] for q in walk], 0.5, [WALL_TOP - 4, WALL_TOP - 3.3], N)
    a = degs[0] + 14
    while a < degs[1] - 12:
        q = polar((WALL_IN + WALL_OUT) / 2 + 1.2, a)
        p.hull.box(
            [2.8, 2.2, 2.8], STONE_LIGHT, Placement(pt(q[0], q[1], WALL_TOP - 0.2), -a * DEG)
        )
        a += 8


def _side(p: Any) -> None:
    for s in [-1, 1]:
        _sector(p, [-45, 45] if s > 0 else [135, 225])


def _front(p: Any) -> None:
    _sector(p, [-135, -45])


def _back(p: Any) -> None:
    _sector(p, [45, 135])


def _drum(p: Any, sx: float, sy: float, top: float) -> None:
    """Draw the tower drum of the corner `sx`, `sy` (config signs) up to `top`.

    A flared, battered foot over its rail shoes, arrow slits and a band of light under its top.
    """
    at = pt(sx * TOWER_AT, sy * TOWER_AT, 0)
    r = TOWER_R
    place = Placement(at, math.pi / 10)
    p.hull.lathe(
        [[r + 2.6, ROCK_TOP - 0.6], [r + 0.6, ROCK_TOP + 5], [r, ROCK_TOP + 6], [r, top], [0, top]],
        10,
        STONE,
        place,
    )
    p.neon.ring(r + 0.15, 0.7, 10, N, Placement([at[0], top - 4, at[2]], math.pi / 10))
    for k in range(5):
        a = k * math.pi * 2 / 5 + 0.3
        slit = [at[0] + math.cos(a) * (r - 0.2), ROCK_TOP + 9, at[2] + math.sin(a) * (r - 0.2)]
        p.hull.box([1.2, 4, 1.2], STONE_DARK, Placement(slit, -a))
    # The rail shoes under its foot, lit: they ride the rails out.
    for k in [-1, 1]:
        shoe = pt(sx * TOWER_AT + k * 4, sy * TOWER_AT - k * 4 * sx * sy, ROCK_TOP - 0.4)
        p.neon.box([2, 0.8, 2], N, Placement(shoe, math.pi / 4))


def _front_tower(sx: float) -> Any:
    """Return the drawing of the front tower on the config side `sx` (its drum, without crown)."""

    def draw(p: Any) -> None:
        _drum(p, sx, -1, TOWER_TOP - CROWN)
        # The seat its turret stands on, inside its crown.
        at = pt(sx * TOWER_AT, -TOWER_AT, TOWER_TOP - CROWN)
        p.hull.cylinder(TOWER_R - 2, CROWN, 10, STONE_DARK, Placement(at, math.pi / 10))

    return draw


def _rear_tower(sx: float) -> Any:
    """Return the drawing of the rear tower on the config side `sx`: its drum under a flat roof.

    A lit hatch in the roof, where its cannon rises; four merlons round its rim.
    """

    def draw(p: Any) -> None:
        _drum(p, sx, 1, TOWER_TOP)
        at = pt(sx * TOWER_AT, TOWER_AT, TOWER_TOP)
        p.hull.cylinder(TOWER_R + 0.8, 1, 10, STONE_LIGHT, Placement(at, math.pi / 10))
        p.neon.ring(TOWER_R - 2.4, 0.5, 10, N, Placement([at[0], TOWER_TOP + 0.9, at[2]]))
        p.hull.cylinder(TOWER_R - 2.6, 0.4, 10, SHADE["dark"], Placement(at))

    return draw


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over the spire rotor (BOSS-58): an octagonal cap, a lit seam round it."""
    at = pt(ROTOR_AT[0], ROTOR_AT[1], KEEP_TOP)
    p.hull.cylinder(6.4, 1.4, 8, SHADE["panel"], Placement(at, math.pi / 8), 5.6)
    p.hull.box([6.4, 0.5, 1.2], SHADE["dark"], Placement([at[0], KEEP_TOP + 1.3, at[2]]))
    p.neon.ring(6.1, 0.25, 8, N, Placement([at[0], KEEP_TOP + 1, at[2]], math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a lit collar round the opening the rotor rises from."""
    at = pt(ROTOR_AT[0], ROTOR_AT[1], KEEP_TOP)
    p.neon.ring(6, 0.4, 12, N, Placement(at))


def throne_armour() -> Any:
    """Return the towers' and the ward's drawings by region id (`drawing.armour`)."""
    return {
        "towers-front-right": {"whole": _front_tower(1)},
        "towers-front-left": {"whole": _front_tower(-1)},
        "towers-back-right": {"whole": _rear_tower(1)},
        "towers-back-left": {"whole": _rear_tower(-1)},
        "ward-front": {"whole": _front},
        "ward-back": {"whole": _back},
        "ward-side": {"whole": _side},
        "rotor-hatch": {"whole": _draw_hatch, "frame": _draw_hatch_frame},
    }


def tower_crown(p: Any, at: Vec3) -> None:
    """Add a front tower's crown (FB-THRONE-OF-STORMS-03): the battlements its turret stands in.

    A lit band round it and five merlons; the drum it stands on is its moving tower's.
    """
    top = TOWER_TOP
    r = TOWER_R
    p.hull.lathe(
        [[r - 1.8, top - CROWN], [r + 1, top - CROWN], [r + 1, top], [r - 1.8, top]],
        10,
        STONE_LIGHT,
        Placement([at[0], 0, at[2]], math.pi / 10),
    )
    p.neon.ring(r + 1.1, 0.7, 10, N, Placement([at[0], top - 2, at[2]], math.pi / 10))
    for k in range(5):
        a = math.pi / 5 + k * math.pi * 2 / 5
        q = [at[0] + math.cos(a) * (r - 0.2), top, at[2] + math.sin(a) * (r - 0.2)]
        p.hull.box([2.8, 2.4, 2.8], STONE, Placement(q, -a))
