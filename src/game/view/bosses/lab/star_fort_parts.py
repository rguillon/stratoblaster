# Copyright (c) 2026 Renaud Guillon
"""FB-STAR-FORT-03, FB-STAR-FORT-05, FB-STAR-FORT-09 to 11: the Star Fort's parts and armour.

Logical pixels, nose +Z, Y up (towards the camera). Its parts' drawings (the moat's pylons on its
rear bastions, the redoubts on its ravelins, the cavalier's parapet in its nose bastion, the
gatehouse), its armour regions' (the rear bastions that swing out, the keep that rises, the
flagstones over its batteries, the shutters over its embrasures) and the kit its model shares:
scarped walls, parapets, merlons. A machine, not a creature: the Lab's fifth round builds gigantic
flying fortresses (user request, 2026-11-06).
"""

import math

from game.config.bosses.lab.star_fort import (
    FLAGSTONE_Y,
    FLAGSTONES,
    GATE_TOP,
    GATEHOUSE_AT,
    HATCH_R,
    KEEP_AT,
    KEEP_R,
    KEEP_TOP,
    PARADE,
    PYLON_AT,
    RAVELIN_TOP,
    REAR_BASTION,
    ROCK_TOP,
    WALL_TOP,
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


# Its neon (`BOSS_LOOK.neon["star-fort"]`): rose.
N = [1, 0.35, 0.6]
# Its materials: dressed stone (walls), dark stone (scarps), earth (the glacis), slate (roofs).
STONE = [0.15, 0.15, 0.145]
SCARP = [0.1, 0.1, 0.1]
EARTH = [0.045, 0.05, 0.045]
PAVE = [0.115, 0.115, 0.11]
SLATE = [0.06, 0.065, 0.075]
GLASS = [0.05, 0.06, 0.08]


def pt(x: float, y: float, h: float) -> Vec3:
    """Return the playfield point `(x, y)` at height `h` in model space."""
    return boss_point(x, y, h)


def flat(x: float, y: float) -> list[Any]:
    """Return the playfield point `(x, y)` as a model outline point `[x, z]`."""
    return [-x, -y]


def outline_of(points: list[Any], side: float = 1) -> list[Any]:
    """Return the model outline of playfield `points`, mirrored when `side` is -1."""
    return [flat(side * q[0], q[1]) for q in points]


def bar(layer: Any, a: list[Any], b: list[Any], size: list[float], color: Any) -> None:
    """Add a bar from the playfield point `a` to `b` (`[x, y]`), `size` `[width, height]`.

    Lying flat on height `a[2]` when given, else 0.
    """
    h = a[2] if len(a) > 2 else 0
    pa = pt(a[0], a[1], h)
    pb = pt(b[0], b[1], h)
    dx = pb[0] - pa[0]
    dz = pb[2] - pa[2]
    length = math.hypot(dx, dz)
    mid = [(pa[0] + pb[0]) / 2, h, (pa[2] + pb[2]) / 2]
    layer.box([size[0], size[1], length], color, Placement(mid, math.atan2(dx, dz)))


def parapet(p: Any, points: list[Any], top: float, lit: bool) -> None:
    """Add a parapet along the playfield polyline `points` on a wall `top` high, merlons on it.

    A light along it when `lit`.
    """
    for k in range(len(points) - 1):
        a = points[k]
        b = points[k + 1]
        bar(p.hull, [a[0], a[1], top], b, [1.4, 1.4], STONE)
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        count = math.floor(length / 5)
        for i in range(count):
            u = (i + 0.5) / count
            q = [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u]
            p.hull.box([1.6, 1, 1.6], STONE, Placement(pt(q[0], q[1], top + 1.4)))
        if lit:
            bar(p.neon, [a[0], a[1], top + 1.4], b, [0.35, 0.3], N)


def scarped(p: Any, points: list[Any], heights: list[float], color: Any, top: Any) -> None:
    """Add a scarped block: the playfield outline `points`, its sides sloping in as they rise."""
    p.hull.bevel_slab(
        outline_of(points), [heights[0], heights[0] + 0.4, heights[1]], [0, 1.6], color, None, top
    )


def _draw_rear_bastion(p: Any, side: float) -> None:
    """Draw the rear bastion on `side` (+1 the config's right), at rest (FB-STAR-FORT-10).

    A scarped stone bastion, its terreplein at the ramparts' height, a parapet along its faces and
    flanks lit at its salient, the pylon's socket on it (the sweeper rises from it), the pivot's
    great hinge drum at its outer flank root, and stone stairs down its gorge.
    """
    pts = [[side * q[0], q[1]] for q in REAR_BASTION]
    scarped(p, pts, [ROCK_TOP - 0.5, WALL_TOP], SCARP, STONE)
    parapet(p, pts, WALL_TOP, True)
    socket = pt(side * PYLON_AT[0], PYLON_AT[1], WALL_TOP - 0.2)
    p.hull.cylinder(5.4, 0.6, 8, M.dark, Placement(socket, math.pi / 8))
    p.neon.ring(5.45, 0.3, 8, N, Placement([socket[0], WALL_TOP + 0.1, socket[2]], math.pi / 8))
    hinge = pt(pts[0][0], pts[0][1], ROCK_TOP)
    p.hull.cylinder(3, WALL_TOP + 2 - ROCK_TOP, 8, M.panel, Placement(hinge))
    p.neon.ring(3.05, 0.4, 8, N, Placement([hinge[0], WALL_TOP + 1.2, hinge[2]]))
    for k in range(3):
        u = 0.35 + k * 0.1
        a = pts[4]
        b = pts[0]
        q = [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u]
        p.hull.box([3, WALL_TOP - PARADE - k * 1.6, 3], STONE, Placement(pt(q[0], q[1], PARADE)))
    lamps(p.neon, [pt(pts[2][0] * 0.9, pts[2][1] * 0.9, WALL_TOP + 0.3)], 1.2, N)


def rear_bastion(side: float) -> Any:
    """Return the drawing of the rear bastion on `side` (see `_draw_rear_bastion`)."""

    def draw(p: Any) -> None:
        _draw_rear_bastion(p, side)

    return draw


def keep(p: Any) -> None:
    """Draw the keep (FB-STAR-FORT-11): an octagonal tower on the parade ground, at rest.

    Dressed stone, a lit band of arrow slits, buttresses, a crenellated crown round its flat roof
    (the gatling unfolds on it once it has risen), the flag staff.
    """
    at = pt(KEEP_AT[0], KEEP_AT[1], PARADE)
    turn = math.pi / 8
    p.hull.cylinder(KEEP_R + 1, 2, 8, SCARP, Placement(at, turn), KEEP_R)
    p.hull.cylinder(
        KEEP_R,
        KEEP_TOP - PARADE - 2,
        8,
        STONE,
        Placement([at[0], PARADE + 2, at[2]], turn),
        KEEP_R - 0.6,
    )
    p.hull.cylinder(KEEP_R + 0.6, 1, 8, STONE, Placement([at[0], KEEP_TOP - 1.5, at[2]], turn))
    p.neon.ring(KEEP_R - 0.25, 0.6, 8, N, Placement([at[0], PARADE + 8, at[2]], turn))
    for k in range(8):
        a = turn + k * math.pi / 4
        p.hull.box(
            [2, 1.4, 2],
            STONE,
            Placement(
                [
                    at[0] + (KEEP_R - 0.1) * math.cos(a),
                    KEEP_TOP - 0.5,
                    at[2] + (KEEP_R - 0.1) * math.sin(a),
                ],
                -a,
            ),
        )
        b = a + math.pi / 8
        p.hull.box(
            [1.6, KEEP_TOP - PARADE - 6, 1.6],
            SCARP,
            Placement([at[0] + KEEP_R * math.cos(b), PARADE + 2, at[2] + KEEP_R * math.sin(b)], -b),
        )
    p.hull.cylinder(KEEP_R - 1.2, 0.4, 8, SLATE, Placement([at[0], KEEP_TOP - 0.5, at[2]], turn))
    p.neon.ring(KEEP_R - 1.2, 0.3, 8, N, Placement([at[0], KEEP_TOP - 0.2, at[2]], turn))
    staff = [at[0] + 6, KEEP_TOP - 0.5, at[2] - 6]
    p.hull.cylinder(0.3, 8, 4, M.dark, Placement(staff))
    p.neon.box([0.2, 2.4, 3.6], N, Placement([staff[0], KEEP_TOP + 5, staff[2] + 1.8]))


def flagstones(p: Any) -> None:
    """Draw the raised flagstone terraces either side of the keep (FB-STAR-FORT-11).

    Paved platforms, their slabs' joints dark, a lit kerb along their front; the batteries lie
    under them.
    """
    for s in [-1, 1]:
        pts = [[s * q[0], q[1]] for q in FLAGSTONES]
        p.hull.bevel_slab(
            outline_of(pts), [FLAGSTONE_Y[0], FLAGSTONE_Y[1] - 0.4, FLAGSTONE_Y[1]], [0, 0.4], STONE
        )
        for y in [5, 8, 11]:
            bar(p.bare, [s * 12.4, y, FLAGSTONE_Y[1]], [s * 26.6, y], [0.25, 0.15], SCARP)
        for x in [16, 20, 24]:
            bar(p.bare, [s * x, 2.4, FLAGSTONE_Y[1]], [s * x, 13.6], [0.25, 0.15], SCARP)
        bar(p.neon, [s * 12.4, 2.2, FLAGSTONE_Y[1] - 0.3], [s * 26.6, 2.2], [0.35, 0.35], N)


def hatch(at: list[Any], height: float) -> Any:
    """Return the drawing of an embrasure's shutter at `at`, on a wall `height` high (BOSS-58).

    An octagonal iron shutter flush on the rampart, riveted, a lit cross on it.
    """

    def draw(p: Any) -> None:
        q = pt(at[0], at[1], height - 0.2)
        p.hull.cylinder(HATCH_R, 1, 8, M.panel, Placement(q, math.pi / 8), HATCH_R - 0.6)
        p.neon.box([HATCH_R * 1.2, 0.3, 0.4], N, Placement([q[0], height + 0.8, q[2]]))
        p.neon.box([0.4, 0.3, HATCH_R * 1.2], N, Placement([q[0], height + 0.8, q[2]]))

    return draw


def hatch_frame(at: list[Any], height: float) -> Any:
    """Return what a shutter leaves once blown (BOSS-44): the embrasure's dark, lit-rimmed pit."""

    def draw(p: Any) -> None:
        q = pt(at[0], at[1], height - 0.3)
        p.hull.ring(HATCH_R - 0.4, 0.9, 8, M.dark, Placement(q, math.pi / 8))
        p.neon.ring(HATCH_R - 0.35, 0.25, 8, N, Placement([q[0], height + 0.4, q[2]], math.pi / 8))

    return draw


def pylon(p: Any, at: Vec3) -> None:
    """Draw a moat pylon (FB-STAR-FORT-03): an energy spire in its socket on a rear bastion.

    A stone plinth, a tapering iron mast ringed by three glowing coils, a lit crystal on its tip,
    and two conduits running down to the bastion's edge (they feed the moat).
    """
    base = [at[0], WALL_TOP, at[2]]
    p.hull.cylinder(4.6, 2, 8, STONE, Placement(base, math.pi / 8), 4)
    p.hull.cylinder(2.2, 16, 6, M.panel, Placement([at[0], WALL_TOP + 2, at[2]]), 0.8)
    for k in range(3):
        r = 3.4 - k * 0.7
        p.neon.ring(r, 0.6, 8, N, Placement([at[0], WALL_TOP + 5 + k * 4, at[2]]))
    p.neon.cylinder(1.2, 2.6, 4, N, Placement([at[0], WALL_TOP + 18, at[2]]), 0)
    out = 1 if at[0] < 0 else -1
    for dz in [-2.4, 2.4]:
        p.hull.box([8, 1.2, 1.2], M.dark, Placement([at[0] + out * 5, WALL_TOP + 0.4, at[2] + dz]))


def redoubt(p: Any, at: Vec3) -> None:
    """Draw a ravelin's redoubt (FB-STAR-FORT-03): a squat armoured blockhouse behind its gun.

    Its gun (a mount, BOSS-58) stands on the ravelin's top in front of it; loopholes lit along its
    front, a flag mast on its roof.
    """
    toward = math.atan2(at[0], at[2])
    back = [at[0] - 4.6 * math.sin(toward), RAVELIN_TOP, at[2] - 4.6 * math.cos(toward)]
    p.hull.box([6.4, 3.6, 3.6], STONE, Placement(back, toward), SLATE)
    front = [back[0] + 1.9 * math.sin(toward), RAVELIN_TOP + 2, back[2] + 1.9 * math.cos(toward)]
    p.neon.box([5, 0.6, 0.4], N, Placement(front, toward))
    p.hull.cylinder(0.25, 6, 4, M.dark, Placement([back[0], RAVELIN_TOP + 4.2, back[2]]))
    lamps(p.neon, [[back[0], RAVELIN_TOP + 10.2, back[2]]], 0.8, N)


def cavalier(p: Any, at: Vec3) -> None:
    """Draw the cavalier's parapet (FB-STAR-FORT-03): a horseshoe of stone round its turret.

    Its turret (a mount, BOSS-58) stands in it on the bastion's terreplein; a range-finder post
    and lamps behind it.
    """
    for k in range(7):
        a = math.pi * (0.15 + k * 0.243)
        q = [at[0] + 8 * math.cos(a), WALL_TOP, at[2] + 8 * math.sin(a)]
        p.hull.box([4.4, 3.2, 2.2], STONE, Placement(q, math.pi / 2 - a), SLATE)
    p.neon.ring(7.2, 0.3, 12, N, Placement([at[0], WALL_TOP + 0.1, at[2]]))
    post = [at[0], WALL_TOP, at[2] - 7.5]
    p.hull.cylinder(0.8, 6, 4, M.panel, Placement(post))
    p.hull.box([5, 1.2, 1.2], M.dark, Placement([post[0], WALL_TOP + 6, post[2]]))
    lamps(
        p.neon,
        [[post[0] - 2.4, WALL_TOP + 7.2, post[2]], [post[0] + 2.4, WALL_TOP + 7.2, post[2]]],
        0.8,
        N,
    )


def gatehouse(p: Any, _at: Vec3) -> None:
    """Draw the gatehouse (FB-STAR-FORT-03) on the rear curtain: twin towers over a lit gate.

    Two round towers with conical slate roofs, the gate's arch between them glowing, a
    drawbridge's chains, a banner over it.
    """
    x = -GATEHOUSE_AT[0]
    z = -GATEHOUSE_AT[1]
    for s in [-1, 1]:
        q = [x + s * 5.2, WALL_TOP, z]
        p.hull.cylinder(3.6, GATE_TOP - WALL_TOP, 8, STONE, Placement(q))
        p.hull.cylinder(4, 4, 8, SLATE, Placement([q[0], GATE_TOP, q[2]]), 0)
        lamps(p.neon, [[q[0], GATE_TOP + 4, q[2]]], 0.7, N)
    p.hull.box([7, GATE_TOP - WALL_TOP - 1, 6], STONE, Placement([x, WALL_TOP, z]), SLATE)
    p.neon.box([4, 3.4, 0.4], N, Placement([x, WALL_TOP + 0.5, z - 3.1]))
    p.neon.box([4, 3.4, 0.4], N, Placement([x, WALL_TOP + 0.5, z + 3.1]))
    vent(p.hull, [x, GATE_TOP - 1, z], [5, 3], 3)
