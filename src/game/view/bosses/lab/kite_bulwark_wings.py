# Copyright (c) 2026 Renaud Guillon
"""MB-KITE-BULWARK-05: the Kite Bulwark's wings, moving pieces of their own (BOSS-45).

Each a very wide box-kite wing: a leading and a trailing spar of dark metal from its root out to
its tip, ribs across, two cells of pale fabric stretched between them (an open gap between the
cells, as on a box kite), the cells' tall fabric sides standing along the spars, bracing wires
across the fabric, an armoured root plate, the cradle its wingtip pod stands on and the hardpoint
its sweeper rides out on. Drawn spread open, at rest; the engine swings them back about their
trailing roots as it transforms. Logical pixels, nose +Z, Y up (towards the camera); shapes are
given in config coordinates (X right, Y up the screen) and turned into model space here.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.kite_bulwark import POD_AT, POD_TOP, SWEEPER_SPOT, WING, WING_Y
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.final_boss_greebles import SHADE, rod
from game.view.bosses.final_boss_shapes import edge_strips
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["kite-bulwark"]
# The fabric: a pale, weathered sailcloth (blue-grey, so it keeps a little colour, BOSS-50), and its
# darker sides.
FABRIC = [0.5, 0.58, 0.64]
FABRIC_SIDE = [0.34, 0.4, 0.45]
# The spars' height (their axis) and radius, the fabric's bottom and top, and its cells' sides' top.
SPAR_H = WING_Y[0] + 1.4
SPAR_R = 1.3
CLOTH = [WING_Y[1] - 0.7, WING_Y[1]]
SIDE_TOP = WING_Y[1] + 4.5
# The cells, `[x0, x1]` along the wing (config), and the ribs' x.
CELLS = [[12, 37], [43, 61]]
RIBS = [12, 24.5, 37, 43, 52, 61]


def pt(x: float, y: float, h: float) -> Vec3:
    """Return the config point `(x, y)` at height `h` in model space."""
    return boss_point(x, y, h)


def _lead(x: float) -> float:
    """Return the leading edge's y (config) at `x` along the right wing."""
    return _edge(x, [WING[0], WING[1], WING[2]])


def _trail(x: float) -> float:
    """Return the trailing edge's y (config) at `x` along the right wing."""
    return _edge(x, [WING[6], WING[5], WING[4]])


def _edge(x: float, points: list[Any]) -> float:
    """Return the y of the polyline `points` (x going up) at `x`."""
    # The segment `x` is on: the last one past its end.
    k = 0
    while k < len(points) - 2 and x > points[k + 1][0]:
        k += 1
    a = points[k]
    b = points[k + 1]
    t = (x - a[0]) / (b[0] - a[0])
    y: float = a[1] + (b[1] - a[1]) * t
    return y


def _cell(p: Any, s: float, x0: float, x1: float) -> None:
    """Draw a box-kite cell from `x0` to `x1` on the side `s`: its fabric, sides and wires."""
    inset = 1.6
    outline = [
        [s * x0, _lead(x0) + inset],
        [s * x1, _lead(x1) + inset],
        [s * x1, _trail(x1) - inset],
        [s * x0, _trail(x0) - inset],
    ]
    p.hull.slab([[-q[0], -q[1]] for q in outline], CLOTH, FABRIC_SIDE, None, FABRIC)
    # Its tall fabric sides along the spars (the box kite's walls), dark-hemmed on top.
    for edge in [0, 1]:
        y0 = _lead(x0) + 0.6 if edge == 0 else _trail(x0) - 0.6
        y1 = _lead(x1) + 0.6 if edge == 0 else _trail(x1) - 0.6
        a = pt(s * x0, y0, 0)
        b = pt(s * x1, y1, 0)
        edge_strips(p.hull, [[a[0], a[2]], [b[0], b[2]]], 0.7, [SPAR_H, SIDE_TOP], FABRIC_SIDE)
        edge_strips(
            p.hull, [[a[0], a[2]], [b[0], b[2]]], 0.9, [SIDE_TOP, SIDE_TOP + 0.5], SHADE["base"]
        )
    # Its bracing wires, crossed over the fabric.
    for k in [0, 1]:
        a = pt(s * x0, _lead(x0) + 1, CLOTH[1] + 0.3)
        b = pt(s * x1, _trail(x1) - 1, CLOTH[1] + 0.3)
        if k == 1:
            a = pt(s * x0, _trail(x0) - 1, CLOTH[1] + 0.3)
            b = pt(s * x1, _lead(x1) + 1, CLOTH[1] + 0.3)
        rod(p.hull, a, b, 0.22, SHADE["dark"])
    # A seam of light down the fabric's middle.
    mid0 = (_lead(x0) + _trail(x0)) / 2
    mid1 = (_lead(x1) + _trail(x1)) / 2
    m0 = pt(s * (x0 + 1), mid0, 0)
    m1 = pt(s * (x1 - 1), mid1, 0)
    edge_strips(p.neon, [[m0[0], m0[2]], [m1[0], m1[2]]], 0.35, [CLOTH[1], CLOTH[1] + 0.12], N)


def _spars(p: Any, s: float) -> None:
    """Draw the right (`s` 1) or left wing's frame: its spars, tip spar and ribs."""
    tip = [WING[2], WING[3], WING[4]]
    lead = [WING[0], WING[1], WING[2]]
    trail = [WING[6], WING[5], WING[4]]
    for line in [lead, trail, tip]:
        for k in range(len(line) - 1):
            a = line[k]
            b = line[k + 1]
            rod(
                p.hull, pt(s * a[0], a[1], SPAR_H), pt(s * b[0], b[1], SPAR_H), SPAR_R, SHADE["mid"]
            )
    for x in RIBS:
        a = pt(s * x, _lead(x), SPAR_H)
        b = pt(s * x, _trail(x), SPAR_H)
        rod(p.hull, a, b, 0.8, SHADE["base"])
        # A collar where the rib meets each spar.
        for q in [a, b]:
            p.hull.box([2.2, 2.2, 2.2], SHADE["dark"], Placement([q[0], SPAR_H - 1.1, q[2]]))
    # The leading edge's light line, root to tip.
    points = [pt(s * q[0], q[1] - 1.2, 0) for q in lead]
    edge_strips(
        p.neon, [[q[0], q[2]] for q in points], 0.5, [SPAR_H + SPAR_R - 0.2, SPAR_H + SPAR_R], N
    )
    # The tip's lamp.
    at = pt(s * WING[3][0], WING[3][1], SPAR_H + SPAR_R)
    p.neon.box([1.6, 0.8, 1.6], N, Placement(at))


def _root(p: Any, s: float) -> None:
    """Draw the wing's armoured root plate, from its leading root back to its hinge."""
    outline = [[s * 9, -12], [s * 14, -11.4], [s * 14, 11.8], [s * 9, 12]]
    p.hull.bevel_slab(
        [[-q[0], -q[1]] for q in outline],
        [WING_Y[0] - 1, WING_Y[1] + 0.6, WING_Y[1] + 1.6],
        [0, 0.9],
        SHADE["panel"],
        None,
        SHADE["light"],
    )
    edge_strips(
        p.neon,
        [[-s * 13.2, 9], [-s * 13.2, -9]],
        0.4,
        [WING_Y[1] + 1.55, WING_Y[1] + 1.7],
        N,
    )


def _cradle(p: Any, s: float) -> None:
    """Draw the cradle the wingtip pod stands on, and the sweeper's hardpoint on the inner cell."""
    at = pt(s * POD_AT[0], POD_AT[1], 0)
    p.hull.box([8, POD_TOP - 0.6 - SPAR_H, 9], SHADE["dark"], Placement([at[0], SPAR_H, at[2]]))
    hard = pt(s * SWEEPER_SPOT[0], SWEEPER_SPOT[1], CLOTH[1] - 0.2)
    p.hull.cylinder(4.6, 0.6, 8, SHADE["light"], Placement(hard, math.pi / 8))
    p.neon.ring(4.7, 0.25, 8, N, Placement([hard[0], CLOTH[1] + 0.1, hard[2]], math.pi / 8))
    for k in range(4):
        bolt = [
            hard[0] + 3.2 * math.cos(k * math.pi / 2),
            CLOTH[1] + 0.4,
            hard[2] + 3.2 * math.sin(k * math.pi / 2),
        ]
        p.hull.box([0.9, 0.4, 0.9], SHADE["dark"], Placement(bolt))


def _wing(s: float) -> Any:
    """Return the drawing of the wing on the config side `s`."""

    def draw(p: Any) -> None:
        _spars(p, s)
        for cell in CELLS:
            _cell(p, s, cell[0], cell[1])
        _root(p, s)
        _cradle(p, s)

    return draw


def kite_wings() -> Any:
    """Return the wings' drawings by region id (`drawing.armour`); config right is +X."""
    return {
        "wings-right": {"whole": _wing(1)},
        "wings-left": {"whole": _wing(-1)},
    }
