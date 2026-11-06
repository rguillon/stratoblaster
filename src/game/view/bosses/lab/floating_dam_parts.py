# Copyright (c) 2026 Renaud Guillon
"""FB-FLOATING-DAM-03, FB-FLOATING-DAM-10 to -12: the Floating Dam's parts, gates and hatches.

Logical pixels, nose +Z, Y up (towards the camera). Its outer sluices, its gatehouses and its
turbine hall (its parts); its inner sluice gates and the leaves of its bascule bridge (moving
pieces, BOSS-45), the cover over its spillway chute and the hatches over its late guns (armour,
BOSS-42, BOSS-58). Concrete, steel and water-blue light lines: a flying dam, not a creature (the
Lab's fifth round, user request 2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.floating_dam import (
    BASIN,
    CASEMATE_AT,
    CASEMATE_HATCH,
    COVER,
    CREST,
    CREST_Y,
    GATE,
    GATEHOUSE,
    HALL,
    HATCH,
    LEAF,
    LEAF_DECK,
    MORTAR_AT,
    NOTCH,
    OUTLET_AT,
    OUTLET_HATCH,
    OUTLET_TOP,
    ROAD_GUN_AT,
    ROTOR_AT,
    SILL,
    WEIR_TOP,
    crest_y,
    face_height,
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


N = BOSS_LOOK.neon["floating-dam"]
# Its shades: pale weathered concrete, a darker course of it, steel for its gates and roofs, dark
# asphalt on its road.
CONCRETE = [0.2, 0.205, 0.21]
COURSE = [0.13, 0.135, 0.14]
STEEL = [0.12, 0.13, 0.15]
ROOF = [0.08, 0.09, 0.1]
ASPHALT = [0.05, 0.05, 0.055]


def pt(x: float, y: float) -> list[float]:
    """Return a config point `(x, y)` as a slab outline point (model X, Z)."""
    return [-x, -y]


def outline_of(points: list[Any], side: float = 1) -> list[list[float]]:
    """Return config points (their X times `side`) as a slab outline (model X, Z)."""
    return [pt(side * q[0], q[1]) for q in points]


def square(at: list[Any], half: list[Any]) -> list[list[float]]:
    """Return a rectangle (config) `half` big either way round config `at`, as a slab outline."""
    return outline_of([
        [at[0] - half[0], at[1] - half[1]],
        [at[0] + half[0], at[1] - half[1]],
        [at[0] + half[0], at[1] + half[1]],
        [at[0] - half[0], at[1] + half[1]],
    ])


def on_face(x: float, d: float, lift: float = 0) -> Vec3:
    """Return the model point on the wall's face `d` px in front of the crest's line at `x`."""
    return boss_point(x, crest_y(x) - d, face_height(d) + lift)


def lit_bar(p: Any, a: Vec3, b: Vec3, width: float, color: Any = None) -> None:
    """Add a flat bar from model `a` to model `b`, `width` wide: a light strip (neon by default)."""
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    dz = b[2] - a[2]
    flat = math.hypot(dx, dz)
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    yaw = math.atan2(dx, dz)
    pitch = -math.atan2(dy, flat)
    mid = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2]
    if color == None:
        p.neon.box([width, 0.25, length], N, Placement(mid, yaw, pitch))
    else:
        p.hull.box([width, 0.4, length], color, Placement(mid, yaw, pitch))


def sluice(p: Any, at: Vec3) -> None:
    """Draw an outer sluice (FB-FLOATING-DAM-03): piers, a hoist bridge, its gate raised.

    Two concrete piers stand out of the face either side of the outlet sill its gun stands on (the
    core's: it stays under its stump), a steel hoist bridge across their tops with its winch, the
    gate hauled up under it, lit guides down the piers' inner faces.
    """
    x = -at[0]
    y = -at[2]
    for s in [-1, 1]:
        px = x + s * (SILL[0] + 1.6)
        pier = [[px - 1.6, SILL[1] - 2], [px + 1.6, SILL[1] - 2], [px + 1.6, -6], [px - 1.6, -6]]
        p.hull.bevel_slab(outline_of(pier), [-4, 17, 19], [0, 0.6], CONCRETE)
        a = boss_point(px - s * 1.65, SILL[1] - 1.5, 19)
        b = boss_point(px - s * 1.65, SILL[1] - 1.5, SILL[3] + 0.5)
        lit_bar(p, a, b, 0.5)
        p.neon.box([0.9, 0.9, 0.9], N, Placement(boss_point(px, SILL[1] - 1.2, 19)))
    bridge = boss_point(x, y - 4, 19)
    p.hull.box([2 * SILL[0] + 6.4, 2.2, 6], STEEL, Placement(bridge), ROOF)
    p.hull.box([5, 2.4, 3.4], M.panel, Placement([bridge[0], 21.2, bridge[2] - 0.5]))
    p.neon.box([2 * SILL[0] + 6, 0.3, 0.4], N, Placement([bridge[0], 21.2, bridge[2] + 3]))
    # The gate, hauled up under the bridge: a ribbed steel panel.
    g = boss_point(x, y - 6.5, 12)
    p.hull.box([2 * SILL[0] + 0.4, 6, 1.4], STEEL, Placement(g))
    for k in range(3):
        p.bare.box([2 * SILL[0], 0.5, 1.6], ROOF, Placement([g[0], 13 + k * 1.8, g[2]]))


def gatehouse(p: Any, at: Vec3) -> None:
    """Draw a gatehouse on the crest (FB-FLOATING-DAM-03): the road runs through its arch.

    A concrete block with a hipped steel roof, a dark arch through it along the road, lit windows,
    a beacon on its roof's ridge.
    """
    x = -at[0]
    y = -at[2]
    hw = GATEHOUSE[0]
    hd = GATEHOUSE[1]
    top = GATEHOUSE[2]
    body = [[x - hw, y - hd], [x + hw, y - hd], [x + hw, y + hd], [x - hw, y + hd]]
    p.hull.bevel_slab(outline_of(body), [CREST - 0.5, top - 2, top], [0, 0.8], CONCRETE)
    roof = boss_point(x, y, top)
    p.hull.lathe(
        [[hw * 1.18, 0], [hw * 0.55, 5], [0, 6.5]],
        4,
        ROOF,
        Placement(roof, math.pi / 4),
    )
    p.hull.box([2 * hw + 0.6, 1.2, 2 * hd + 0.6], COURSE, Placement([roof[0], top - 3.5, roof[2]]))
    # The arch through it along the road, dark, lit round its mouths.
    for s in [-1, 1]:
        q = boss_point(x + s * (hw + 0.05), y, CREST)
        p.bare.box([0.3, 6, 6], M.dark, Placement(q))
        p.neon.box([0.4, 0.5, 7], N, Placement([q[0], CREST + 6.2, q[2]]))
    for k in range(3):
        wx = x - hw + 3 + k * (2 * hw - 6) / 2
        w = boss_point(wx, y - hd - 0.05, top - 6)
        p.neon.box([1.4, 2.2, 0.3], N, Placement(w))
    p.neon.cylinder(0.8, 1.6, 6, N, Placement([roof[0], top + 6.2, roof[2]]))


def hall(p: Any, at: Vec3) -> None:
    """Draw the turbine hall behind the wall (FB-FLOATING-DAM-03): a long powerhouse.

    A concrete hall with a barrel roof of steel, three generator domes on it with lit rings, its
    penstocks into the wall's back, lit windows down its long sides, transformers at its ends.
    """
    x = -at[0]
    y = -at[2]
    hw = HALL[0]
    hd = HALL[1]
    top = HALL[2]
    body = [[x - hw, y - hd], [x + hw, y - hd], [x + hw, y + hd], [x - hw, y + hd]]
    p.hull.bevel_slab(outline_of(body), [-8, top - 3, top], [-1, 1.2], CONCRETE, None, ROOF)
    for k in [-1, 0, 1]:
        c = boss_point(x + k * 12, y + 1, top)
        p.hull.lathe([[4.2, 0], [3.6, 2.4], [2, 3.6], [0, 4]], 8, STEEL, Placement(c))
        p.neon.ring(4.25, 0.5, 8, N, Placement([c[0], top + 0.4, c[2]]))
        # Its penstock: a fat pipe from the hall's front into the wall's back.
        q = boss_point(x + k * 12, y - hd - 3, 6)
        p.hull.cylinder(2.2, 6.4, 8, COURSE, Placement(q, 0, math.pi / 2))
    for s in [-1, 1]:
        for k in range(5):
            wx = x - hw + 4 + k * (2 * hw - 8) / 4
            w = boss_point(wx, y + s * (hd + 0.05), top - 6)
            p.neon.box([2, 1.4, 0.3], N, Placement(w))
        t = boss_point(x + s * (hw + 3), y + 2, 0)
        p.hull.box([4.5, 9, 6], M.panel, Placement([t[0], 0, t[2]]), STEEL)
        for k in range(3):
            p.neon.box([0.5, 0.5, 5], N, Placement([t[0] + (k - 1) * 1.4, 9.4, t[2]]))


def _gate_points(side: float) -> list[list[Any]]:
    """Return the right (`side` +1) inner gate's panel corners on the face, as drawn (model)."""
    x0 = side * (GATE[0] + 1)
    x1 = side * (GATE[1] - 1)
    return [on_face(x0, 6, 0.7), on_face(x1, 6, 0.7), on_face(x1, 19, 0.7), on_face(x0, 19, 0.7)]


def inner_gate(side: float) -> Any:
    """Return the drawing of the inner sluice gate on `side`, as drawn: down, on the face.

    A ribbed steel panel lying on the face's slope over its bay, a lit rim, lifting lugs at its top
    (FB-FLOATING-DAM-10).
    """

    def draw(p: Any) -> None:
        c = _gate_points(side)
        top = c if side < 0 else [c[1], c[0], c[3], c[2]]
        thick = [[q[0], q[1] - 1.2, q[2]] for q in top]
        p.hull.face([top[0], top[3], top[2], top[1]], STEEL)
        p.hull.face([thick[0], thick[1], thick[2], thick[3]], ROOF)
        for k in range(4):
            a = top[k]
            b = top[(k + 1) % 4]
            ta = thick[k]
            tb = thick[(k + 1) % 4]
            p.hull.face([a, b, tb, ta], ROOF)
        for d in [8.5, 11.5, 14.5, 17]:
            lit_bar(p, on_face(c[0][0] * -1, d, 1), on_face(c[1][0] * -1, d, 1), 0.9, ROOF)
        lit_bar(
            p,
            on_face(side * GATE[0] + side * 1.3, 6.5, 0.9),
            on_face(side * GATE[0] + side * 1.3, 18.5, 0.9),
            0.45,
        )
        lit_bar(
            p,
            on_face(side * GATE[1] - side * 1.3, 6.5, 0.9),
            on_face(side * GATE[1] - side * 1.3, 18.5, 0.9),
            0.45,
        )
        for x in [GATE[0] + 4, GATE[1] - 4]:
            q = on_face(side * x, 6.5, 0.8)
            p.hull.box([1.6, 1.4, 1.6], M.panel, Placement(q))

    return draw


def leaf(side: float) -> Any:
    """Return the drawing of the bascule bridge's leaf on `side` (+1 the right), down, as drawn.

    The road's deck across the spillway, from the middle to its hinge on the notch's side: steel
    girders under it, asphalt on it with the road's lit lane line, rails along both edges, a lit
    seam at its tip where the two leaves meet (FB-FLOATING-DAM-11).
    """

    def draw(p: Any) -> None:
        outline = outline_of(LEAF, side)
        p.hull.slab(outline, [LEAF_DECK[0], LEAF_DECK[1] - 0.4], STEEL)
        road = [[side * 0.6, CREST_Y - 3.5], [side * (NOTCH - 1), CREST_Y - 3.5]]
        road.append([side * (NOTCH - 1), CREST_Y + 4.5])
        road.append([side * 0.6, CREST_Y + 4.5])
        p.hull.slab(outline_of(road), [LEAF_DECK[1] - 0.5, LEAF_DECK[1]], ASPHALT)
        for y in [CREST_Y - 4.3, CREST_Y + 5.3]:
            q = boss_point(side * NOTCH / 2, y, LEAF_DECK[1])
            p.hull.box([NOTCH - 0.6, 1.2, 0.7], M.panel, Placement(q))
        for k in range(2):
            q = boss_point(side * (2.5 + k * 6), CREST_Y + 0.5, LEAF_DECK[1] + 0.02)
            p.neon.box([3, 0.2, 0.5], N, Placement(q))
        tip = boss_point(side * 0.3, CREST_Y + 0.5, LEAF_DECK[1] - 1.5)
        p.neon.box([0.5, 1.6, 10.6], N, Placement(tip))
        for y in [CREST_Y - 2, CREST_Y + 3]:
            q = boss_point(side * NOTCH / 2, y, LEAF_DECK[0] - 1.2)
            p.bare.box([NOTCH - 1, 1.2, 1], ROOF, Placement(q))

    return draw


def cover(p: Any) -> None:
    """Draw the cover over the spillway chute and its basin (FB-FLOATING-DAM-12).

    Overlapping steel shutters down the chute's slope and a lid over the basin, a lit seam down
    the middle: it bursts off as the spillway opens.
    """
    x0 = COVER[0][0]
    x1 = COVER[1][0]
    for k in range(4):
        d0 = 6 + k * 3.8
        d1 = d0 + 4.4
        a = boss_point(x0, CREST_Y - d0, face_height(d0) - (WEIR_TOP - 12) + 0.8)
        b = boss_point(x0, CREST_Y - d1, face_height(d1) - 1 + 0.8)
        lit_bar(p, [0, a[1], a[2]], [0, b[1], b[2]], x1 - x0, STEEL)
    lid = [[x0, BASIN[1]], [x1, BASIN[1]], [x1, CREST_Y - 21], [x0, CREST_Y - 21]]
    p.hull.bevel_slab(
        outline_of(lid), [BASIN[2] - 0.2, BASIN[2] + 1, BASIN[2] + 1.6], [0, 0.6], STEEL
    )
    lit_bar(
        p,
        boss_point(0, BASIN[1] + 1, BASIN[2] + 1.65),
        boss_point(0, CREST_Y - 22, BASIN[2] + 1.65),
        0.6,
    )
    lit_bar(p, boss_point(0, CREST_Y - 7, WEIR_TOP + 0.4), boss_point(0, CREST_Y - 20, 2.6), 0.6)


def _lid(at: list[Any], half: list[Any], height: float) -> Any:
    """Return the drawing of a square hatch lid `half` big round config `at`, on `height`."""

    def draw(p: Any) -> None:
        q = boss_point(at[0], at[1], height)
        outline = square(at, half)
        p.hull.bevel_slab(outline, [height - 0.2, height + 0.6, height + 1.3], [0, 0.6], STEEL)
        p.neon.box([2 * half[0] - 1.8, 0.3, 0.45], N, Placement([q[0], height + 1.3, q[2]]))
        for sx in [-1, 1]:
            p.hull.box(
                [0.9, 0.5, 2 * half[1] - 2],
                M.panel,
                Placement([q[0] + sx * (half[0] - 1.2), height + 1.2, q[2]]),
            )

    return draw


def _well(at: list[Any], half: list[Any], height: float) -> Any:
    """Return what a hatch leaves (BOSS-44): a steel lip round its dark well."""

    def draw(p: Any) -> None:
        q = boss_point(at[0], at[1], height)
        for s in [-1, 1]:
            p.hull.box(
                [2 * half[0], 0.7, 0.8], ROOF, Placement([q[0], height - 0.1, q[2] + s * half[1]])
            )
            p.hull.box(
                [0.8, 0.7, 2 * half[1]], ROOF, Placement([q[0] + s * half[0], height - 0.1, q[2]])
            )
        p.bare.box([2 * half[0] - 0.6, 0.15, 2 * half[1] - 0.6], M.dark, Placement(q))
        p.neon.box([2 * half[0], 0.2, 0.3], N, Placement([q[0], height + 0.6, q[2] - half[1]]))

    return draw


def _hatch(at: list[Any], half: list[Any], height: float) -> Any:
    return {"whole": _lid(at, half, height), "frame": _well(at, half, height)}


def dam_armour() -> Any:
    """Return the Floating Dam's armour drawings by region id (`drawing.armour`, D-254)."""
    left_case = [-CASEMATE_AT[0], CASEMATE_AT[1]]
    left_outlet = [-OUTLET_AT[0], OUTLET_AT[1]]
    crest = [HATCH, HATCH]
    return {
        "gate-right": {"whole": inner_gate(1)},
        "gate-left": {"whole": inner_gate(-1)},
        "leaf-right": {"whole": leaf(1)},
        "leaf-left": {"whole": leaf(-1)},
        "cover": {"whole": cover},
        "casemate-hatch-left": _hatch(left_case, CASEMATE_HATCH, 16),
        "casemate-hatch-right": _hatch(CASEMATE_AT, CASEMATE_HATCH, 16),
        "mortar-hatch": _hatch(MORTAR_AT, crest, CREST),
        "outlet-hatch-left": _hatch(left_outlet, OUTLET_HATCH, OUTLET_TOP),
        "outlet-hatch-right": _hatch(OUTLET_AT, OUTLET_HATCH, OUTLET_TOP),
        "road-hatch": _hatch(ROAD_GUN_AT, crest, CREST),
        "rotor-hatch": _hatch(ROTOR_AT, crest, CREST),
    }
