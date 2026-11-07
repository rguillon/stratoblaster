# Copyright (c) 2026 Renaud Guillon
"""MB-MORTAR-RAFT-03, MB-MORTAR-RAFT-05, MB-MORTAR-RAFT-09: the Mortar Raft's parts and armour.

Logical pixels, nose +Z, Y up (towards the camera). Its parts' drawings (the mortar emplacement on
its forward hull section, the wheelhouse cabin, the mast and its sail), its armour regions' (the
stern outriggers that swing out, the tarpaulins over its core guns) and the small pieces of kit
its model and rig share: pontoons, ropes, ducted lift propellers. A machine, not a creature: the
Lab's fifth round builds gigantic flying fortresses (user request, 2026-11-06).
"""

import math

from game.config.bosses.lab.mortar_raft import (
    BARGE,
    BARGE_TOP,
    CABIN_Y,
    DECKHOUSE_TOP,
    MAST_AT,
    MAST_TOP,
    MORTAR_ATS,
    NEST,
    OUTRIGGER,
    OUTRIGGER_TOP,
    ROOF,
    TARP_TOP,
    TARPS,
    WHEELHOUSE,
    YARD,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.mini_boss_greebles import lamps, vent
from game.view.bosses.world_1_organic_kit import M
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


# Its neon (`BOSS_LOOK.neon["mortar-raft"]`): a pale green.
N = [0.6, 1, 0.4]
QUARTER = math.pi / 2
# Its materials: weathered timber, canvas (tarpaulins, the sail), rope, smoked glass.
TIMBER = [0.1, 0.095, 0.08]
CANVAS = [0.085, 0.1, 0.09]
PATCH = [0.12, 0.13, 0.115]
ROPE = [0.15, 0.15, 0.13]
GLASS = [0.05, 0.07, 0.08]


def pt(x: float, y: float, h: float) -> Vec3:
    """Return the playfield point `(x, y)` at height `h` in model space."""
    return boss_point(x, y, h)


def flat(x: float, y: float) -> list[Any]:
    """Return the playfield point `(x, y)` as a model outline point `[x, z]`."""
    return [-x, -y]


def box_outline(box: list[Any]) -> list[Any]:
    """Return the model outline of the playfield box `[x0, x1, y0, y1]`."""
    return [flat(box[0], box[2]), flat(box[1], box[2]), flat(box[1], box[3]), flat(box[0], box[3])]


def rope(layer: Any, a: Vec3, b: Vec3, thick: float, color: Any) -> None:
    """Add a straight rope (a thin square bar) from `a` to `b`, model space."""
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    dz = b[2] - a[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 0.01:
        return
    pitch = math.acos(max(-1, min(1, dy / length)))
    yaw = math.atan2(dx, dz)
    layer.box([thick, length, thick], color, Placement(a, yaw, pitch))


def pontoon(p: Any, x: float, ys: list[float], radius: float, axis: float) -> None:
    """Add a pontoon along the boss's length at `x` from `ys[0]` to `ys[1]` (config Y).

    A riveted drum with rounded ends, its axis `axis` high, a lit band and rope lashings round it.
    """
    length = ys[1] - ys[0] - radius
    start = pt(x, ys[1] - radius * 0.5, axis)
    p.hull.cylinder(radius, length, 8, M.base, Placement(start, 0, QUARTER))
    for end in [0, 1]:
        y = ys[1] - radius * 0.5 if end == 0 else ys[0] + radius * 0.5
        nose = [[radius, 0], [radius * 0.7, radius * 0.4], [0, radius * 0.55]]
        p.hull.lathe(
            nose, 8, M.panel, Placement(pt(x, y, axis), math.pi if end == 0 else 0, QUARTER)
        )
    for k in range(3):
        y = ys[0] + (ys[1] - ys[0]) * (0.22 + 0.28 * k)
        p.bare.ring(radius + 0.15, 0.7, 8, ROPE, Placement(pt(x, y, axis), 0, QUARTER))
    p.neon.box(
        [0.5, 0.35, (ys[1] - ys[0]) * 0.55],
        N,
        Placement(pt(x, (ys[0] + ys[1]) / 2, axis + radius - 0.1)),
    )


def prop(p: Any, at: list[float], root: list[float], height: float, radius: float) -> None:
    """Add a small ducted lift propeller at `at` (config), on an arm back to `root` (config).

    Its duct `radius` round, `height` high; its blades spin (`p.rotor`).
    """
    centre = pt(at[0], at[1], height)
    p.hull.ring(radius + 0.6, 1.6, 8, M.panel, Placement([centre[0], height - 0.8, centre[2]]))
    p.neon.ring(radius + 0.7, 0.3, 8, N, Placement([centre[0], height + 0.5, centre[2]]))
    a = pt(root[0], root[1], height - 0.6)
    b = pt(at[0], at[1], height - 0.6)
    rope(p.hull, [a[0], height - 0.5, a[2]], [b[0], height - 0.5, b[2]], 1.4, M.dark)
    p.hull.cylinder(0.9, 1.2, 4, M.dark, Placement([centre[0], height - 1.2, centre[2]]))
    p.rotor([centre[0], height + 0.1, centre[2]], radius - 0.3)


def mortar_emplacement(p: Any, _at: Vec3) -> None:
    """Draw the mortar emplacement on the forward hull section (MB-MORTAR-RAFT-03).

    A U of armoured blast walls round its two mortar tubes (their mounts, BOSS-58), ammunition
    lockers behind them, a little crew hut with a rangefinder on its roof at the section's stern,
    lit along its tops.
    """
    top = BARGE_TOP
    for spot in MORTAR_ATS:
        x = spot[0]
        y = spot[1]
        wall = [
            flat(x - 5.4, y - 4),
            flat(x - 4, y - 5.4),
            flat(x - 3, y - 4.4),
            flat(x - 4.2, y - 3.2),
            flat(x - 4.2, y + 4),
            flat(x + 4.2, y + 4),
            flat(x + 4.2, y - 3.2),
            flat(x + 3, y - 4.4),
            flat(x + 4, y - 5.4),
            flat(x + 5.4, y - 4),
            flat(x + 5.4, y + 5.4),
            flat(x - 5.4, y + 5.4),
        ]
        p.hull.slab(wall, [top, top + 2.6], M.panel, None, M.base)
        p.neon.box([8.6, 0.3, 0.4], N, Placement(pt(x, y + 5.2, top + 2.6)))
    # The lockers, the crew hut and its rangefinder.
    for x in [21, 27.5, 34]:
        p.hull.box([4.4, 2.2, 3], M.base, Placement(pt(x, -34.5, top)), M.panel)
        lamps(p.neon, [pt(x, -36.1, top + 1.4)], 0.7, N)
    hut = box_outline([BARGE[0] + 3, BARGE[1] - 4, -31, -23.5])
    p.hull.bevel_slab(hut, [top, top + 4.6, top + 5.4], [0, 0.8], M.panel, None, M.base)
    p.bare.box([12, 1.2, 0.4], GLASS, Placement(pt(28.5, -31.2, top + 2.6)))
    p.hull.cylinder(0.6, 3.2, 4, M.dark, Placement(pt(31, -27, top + 5.4)))
    p.hull.box([6, 1.2, 1.2], M.panel, Placement(pt(31, -27, top + 8.4)))
    lamps(p.neon, [pt(28, -23.4, top + 5.4)], 0.9, N)


def wheelhouse_cabin(p: Any, _at: Vec3) -> None:
    """Draw the wheelhouse cabin (MB-MORTAR-RAFT-03) on its deckhouse, aft of its turret.

    A boxy cabin, a band of smoked windows round its front, a lit roof rail, a whip aerial and a
    signal lamp; the turret's seat in front of it, a lit collar round it (the mount stands on it).
    """
    base = DECKHOUSE_TOP
    cabin = [WHEELHOUSE[0] + 1, WHEELHOUSE[1] - 1, CABIN_Y, WHEELHOUSE[3] - 1]
    p.hull.bevel_slab(box_outline(cabin), [base, ROOF - 0.8, ROOF], [0, 0.9], M.panel, None, M.base)
    windows = [cabin[0] + 0.6, cabin[1] - 0.6, cabin[2] - 0.2, cabin[2] + 5]
    p.bare.slab(box_outline(windows), [ROOF - 4, ROOF - 2], GLASS)
    p.neon.box([cabin[1] - cabin[0] - 2, 0.35, 0.4], N, Placement(pt(-5.5, cabin[2] + 0.5, ROOF)))
    vent(p.hull, pt(-8, 30, ROOF), [4, 3], 3)
    p.hull.cylinder(0.3, 9, 4, M.dark, Placement(pt(-1.5, 31.5, ROOF)), 0.12)
    lamps(p.neon, [pt(-1.5, 31.5, ROOF + 9)], 0.8, N)
    seat = pt(-5.5, 19.5, base - 0.4)
    p.hull.cylinder(5, 0.6, 8, M.dark, Placement(seat, math.pi / 8))
    p.neon.ring(5.05, 0.3, 8, N, Placement([seat[0], base - 0.1, seat[2]], math.pi / 8))
    for x in [cabin[0] - 0.4, cabin[1] + 0.4]:
        p.hull.box([0.6, 4.5, 6], M.dark, Placement(pt(x, 29, base)))


def _draw_sail(p: Any) -> None:
    """Draw the sail hung from the yard: patched canvas, lit seams, heeled out to the left."""
    yard = pt(MAST_AT[0], MAST_AT[1], YARD)
    lean = 0.95
    width = 24
    sail = [[0, 18], [width, 14], [width * 0.92, -17], [0, -20]]
    place = Placement([yard[0] + 0.6, YARD - 0.6, yard[2]], 0, 0, -lean)
    p.flesh.slab(sail, [0, 0.5], CANVAS, place, PATCH)
    for k in range(3):
        x = 5 + k * 7
        p.neon.box(
            [0.35, 0.65, 30], N, Placement([yard[0] + 0.6, YARD - 0.6, yard[2]], 0, 0, -lean)
        )
        p.bare.slab(
            [[x, 10 - k * 3], [x + 4, 10 - k * 3], [x + 4, 4 - k * 3], [x, 4 - k * 3]],
            [0.45, 0.7],
            PATCH,
            place,
        )


def mast(p: Any, _at: Vec3) -> None:
    """Draw the mast (MB-MORTAR-RAFT-03): its step, pole, crow's nest, yard, stays and sail.

    The sail flutters (a wing hinged along the yard, `p.flap`).
    """
    foot = pt(MAST_AT[0], MAST_AT[1], 7.6)
    p.hull.cylinder(3.4, 1.6, 8, M.panel, Placement(foot, math.pi / 8))
    p.neon.ring(3.45, 0.3, 8, N, Placement([foot[0], 8.8, foot[2]], math.pi / 8))
    p.hull.cylinder(1.2, MAST_TOP - 9, 6, M.base, Placement([foot[0], 9, foot[2]]), 0.7)
    nest = [foot[0], NEST, foot[2]]
    p.hull.cylinder(2.6, 2.4, 8, M.panel, Placement(nest), 3)
    lamps(p.neon, [[foot[0], NEST + 2.4, foot[2] - 2.6], [foot[0], MAST_TOP, foot[2]]], 0.9, N)
    yard_from = pt(MAST_AT[0], MAST_AT[1] + 19, YARD)
    yard_to = pt(MAST_AT[0], MAST_AT[1] - 21, YARD)
    rope(p.hull, yard_from, yard_to, 1, M.base)
    for end in [[-14, -40], [16, -40], [-14, 18], [14, 16]]:
        rope(p.bare, [foot[0], MAST_TOP - 1, foot[2]], pt(end[0], end[1], 8.4), 0.35, ROPE)
    p.flap([foot[0], YARD, foot[2]], 1, 30, _draw_sail)


def _draw_outrigger(p: Any, side: float) -> None:
    """Draw the stern outrigger on `side` (+1 the config's right), at rest beside the stern.

    A long pontoon under a strip of decking (the rack stands on it once swung out), two small lift
    propellers on short arms off its outer side, lit along its deck, its lashing cleats forward.
    """
    x0 = OUTRIGGER[0][0]
    x1 = OUTRIGGER[1][0]
    y0 = OUTRIGGER[0][1]
    y1 = OUTRIGGER[2][1]
    mid = (x0 + x1) / 2
    pontoon(p, side * mid, [y0, y1], 4.4, 3.6)
    deck = [side * (x0 + 0.5), side * (x1 - 0.5), y0 + 5, y1 - 2]
    deck = [min(deck[0], deck[1]), max(deck[0], deck[1]), deck[2], deck[3]]
    p.flesh.slab(box_outline(deck), [OUTRIGGER_TOP - 0.9, OUTRIGGER_TOP], TIMBER)
    for k in range(5):
        y = y0 + 7 + k * 5.6
        p.bare.box([x1 - x0 - 0.6, 0.2, 0.35], M.dark, Placement(pt(side * mid, y, OUTRIGGER_TOP)))
    p.neon.box(
        [0.4, 0.35, y1 - y0 - 10],
        N,
        Placement(pt(side * (x1 - 0.4), (y0 + y1) / 2 + 2, OUTRIGGER_TOP)),
    )
    for y in [y0 + 2.4, y0 + 6]:
        p.hull.box([3, 1.4, 1.2], M.panel, Placement(pt(side * (x0 + 1.2), y, OUTRIGGER_TOP - 0.6)))
    for y in [y0 + 14, y1 - 6]:
        prop(p, [side * (x1 + 6), y], [side * (x0 + 4), y], OUTRIGGER_TOP - 1.2, 4)


def outrigger(side: float) -> Any:
    """Return the drawing of the stern outrigger on `side` (see `_draw_outrigger`)."""

    def draw(p: Any) -> None:
        _draw_outrigger(p, side)

    return draw


def _tarp_box(mount_id: str) -> list[float]:
    box: list[float] = TARPS[mount_id]
    return box


def tarp(mount_id: str, base: float) -> Any:
    """Return the drawing of the tarpaulin over the core gun `mount_id`, lying on `base`.

    A canvas sheet draped over the gun's shape (a low, rounded mound), roped down across it, a
    lit tag on its ropes (MB-MORTAR-RAFT-09).
    """
    box = _tarp_box(mount_id)

    def draw(p: Any) -> None:
        cx = (box[0] + box[1]) / 2
        cy = (box[2] + box[3]) / 2
        w = box[1] - box[0]
        d = box[3] - box[2]
        p.flesh.bevel_slab(
            box_outline(box), [base, base + 1, base + TARP_TOP], [0, min(w, d) * 0.28], CANVAS
        )
        for k in [-1, 1]:
            a = pt(box[0] - 0.3, cy + k * d * 0.22, base + 0.4)
            b = pt(box[1] + 0.3, cy + k * d * 0.22, base + 0.4)
            mid = pt(cx, cy + k * d * 0.22, base + TARP_TOP + 0.15)
            rope(p.bare, a, mid, 0.45, ROPE)
            rope(p.bare, mid, b, 0.45, ROPE)
        lamps(p.neon, [pt(cx, cy, base + TARP_TOP + 0.2)], 0.8, N)

    return draw


def tarp_frame(mount_id: str, base: float) -> Any:
    """Return what a tarpaulin leaves once blown off (BOSS-44): a gun pit's lit rim on the deck."""
    box = _tarp_box(mount_id)

    def draw(p: Any) -> None:
        cx = (box[0] + box[1]) / 2
        cy = (box[2] + box[3]) / 2
        r = min(box[1] - box[0], box[3] - box[2]) * 0.46
        p.hull.ring(r, 0.8, 8, M.dark, Placement(pt(cx, cy, base - 0.2), math.pi / 8))
        p.neon.ring(r + 0.05, 0.25, 8, N, Placement(pt(cx, cy, base + 0.5), math.pi / 8))

    return draw
