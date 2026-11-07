# Copyright (c) 2026 Renaud Guillon
"""MB-DRILL-FORT-01 to MB-DRILL-FORT-05: the Drill Fort, the Lab's L-23 mini boss.

Logical pixels, nose +Z, Y up (towards the camera). A gigantic flying mining fortress: a boxy
armoured body on two long track pontoons, a huge drill head at its front (its spiral flutes spin
in its view rig, `drill_fort_rig`), a conveyor belt down its back from the drill's intake to the
control cab, two ore hoppers either side of the belt, two exhaust stacks. A machine, not a
creature: the Lab's fifth round builds flying fortresses (user request, 2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.drill_fort import (
    BELT_TOP,
    BODY,
    BODY_LOW,
    BODY_WALL,
    CAB,
    CAB_GUN_AT,
    CAB_TOP,
    CHEEK_GUN_AT,
    COLLAR,
    CONE_BASE,
    CONE_TIP,
    CONVEYOR,
    COWL_HALF,
    DECK,
    DRILL_AXIS,
    DRILL_FORT,
    GRATE_HALF,
    HOPPER_FRONT,
    HOPPER_GUN_AT,
    HOPPER_REAR,
    HOPPER_TOP,
    ORE,
    ORE_TOP,
    ROTOR_AT,
    ROTOR_COWL,
    ROTOR_H,
    SPITTER_AT,
    SPITTER_H,
    STACK_AT,
    STACK_RADIUS,
    STACK_TOP,
    TRACK,
    TRACK_TOP,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.drill_fort_rig import build_drill_rig, drill_rig_triangles
from game.view.bosses.world_1_organic_kit import M
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["drill-fort"]
QUARTER = math.pi / 2
# Ore: dark rock with a warm glint (body shades, so it stays neutral).
ROCK = [0.13, 0.12, 0.11]
# The head of the conveyor: its intake ramp `[front, back]` up to `HEAD_TOP`, over the drill's
# collar, the spitter's cowl on it.
HEAD = [-33, -23]
HEAD_TOP = SPITTER_H - 0.5


def pt(x: float, y: float, h: float) -> Vec3:
    """Return the playfield point `(x, y)` at height `h` in model space."""
    return boss_point(x, y, h)


def flat(x: float, y: float) -> list[Any]:
    """Return the playfield point `(x, y)` as a model outline point `[x, z]`."""
    return [-x, -y]


def box_outline(b: list[Any]) -> list[list[Any]]:
    """Return the model outline of the playfield box `[x0, x1, y0, y1]`."""
    return [flat(b[0], b[2]), flat(b[1], b[2]), flat(b[1], b[3]), flat(b[0], b[3])]


def _body(p: Any) -> None:
    """Draw the body (MB-DRILL-FORT-01): a bevelled armoured box, plated deck, lit rim.

    Its front corners chamfered round the drill's collar; seams across its deck, rivets, a lit
    seam round its deck's edge and a row of vents along its walls.
    """
    w = BODY[0]
    f = BODY[1]
    b = BODY[2]
    outline = [
        flat(-w, f + 4),
        flat(-w + 4, f),
        flat(w - 4, f),
        flat(w, f + 4),
        flat(w, b - 4),
        flat(w - 4, b),
        flat(-w + 4, b),
        flat(-w, b - 4),
    ]
    p.hull.bevel_slab(outline, [BODY_LOW, BODY_WALL, DECK], [3, 1.2], M.base, None, M.panel)
    for side in [-1, 1]:
        p.neon.box([0.4, 0.4, b - f - 10], N, Placement(pt(side * (w - 1.1), (f + b) / 2, DECK)))
        for y in [-18, -6, 6, 18, 30]:
            p.bare.box([0.4, 2.2, 3.4], M.dark, Placement(pt(side * (w + 0.1), y, BODY_WALL - 6)))
    p.neon.box([2 * w - 10, 0.4, 0.4], N, Placement(pt(0, b - 1.1, DECK)))
    for y in [-4, 20]:
        p.bare.box([2 * w - 4, 0.25, 0.6], M.dark, Placement(pt(0, y, DECK)))


def _tracks(p: Any) -> None:
    """Draw the track pontoons (MB-DRILL-FORT-01): a tread band round each, sprocket drums.

    Each a long bevelled pontoon along a flank, tread plates across its top, a drum at each end,
    a lit strip along its outer side, and three struts to the body's wall.
    """
    for side in [-1, 1]:
        x0 = side * TRACK[0]
        x1 = side * TRACK[1]
        xm = (x0 + x1) / 2
        span = TRACK[1] - TRACK[0]
        outline = [flat(x0, TRACK[2]), flat(x1, TRACK[2]), flat(x1, TRACK[3]), flat(x0, TRACK[3])]
        p.hull.bevel_slab(
            outline, [0.5, TRACK_TOP - 2, TRACK_TOP], [1.5, 0.8], M.base, None, M.dark
        )
        y: float = TRACK[2] + 3
        while y < TRACK[3] - 2:
            p.bare.box([span - 1.2, 0.6, 1.5], M.panel, Placement(pt(xm, y, TRACK_TOP - 0.1)))
            y += 4.5
        for end in [TRACK[2], TRACK[3]]:
            p.hull.cylinder(
                4.5,
                span + 1,
                8,
                M.panel,
                Placement(pt(x0 - side * 0.5, end, 4.5), 0, 0, side * QUARTER),
            )
        p.neon.box([0.4, 0.5, TRACK[3] - TRACK[2] - 6], N, Placement(pt(x1 + side * 0.1, 4, 5.5)))
        for y in [-14, 4, 22]:
            p.hull.box([3.2, 3.5, 4], M.panel, Placement(pt(side * (BODY[0] + 0.8), y, 4)))


def _collar(p: Any) -> None:
    """Draw the drill's collar (MB-DRILL-FORT-02): a thick armoured ring on the body's front.

    It holds the drill head's bearing; a lit ring round its front lip, braces to the body.
    """
    r = COLLAR[2]
    base = pt(0, COLLAR[1], DRILL_AXIS)
    p.hull.cylinder(r, COLLAR[1] - COLLAR[0], 12, M.panel, Placement(base, 0, QUARTER), r - 1.5)
    p.neon.ring(r - 1.2, 0.6, 12, N, Placement(pt(0, COLLAR[0] + 1.2, DRILL_AXIS), 0, QUARTER))
    p.bare.ring(r + 0.1, 2, 12, M.dark, Placement(pt(0, COLLAR[1] - 2.5, DRILL_AXIS), 0, QUARTER))
    for side in [-1, 1]:
        p.hull.box([4, 6, 7], M.base, Placement(pt(side * 11, COLLAR[1] + 1, BODY_LOW + 3)))


def _conveyor(p: Any) -> None:
    """Draw the conveyor (MB-DRILL-FORT-01): a belt down the centre line, its intake ramp.

    The belt between two rails over rollers, lit chevrons on its rails; at its head a ramp rising
    over the drill's collar to the spitter's seat.
    """
    w = CONVEYOR[0]
    p.bare.box(
        [2 * w - 1.2, BELT_TOP - DECK, CONVEYOR[2] - HEAD[1]],
        M.dark,
        Placement(pt(0, (HEAD[1] + CONVEYOR[2]) / 2, DECK)),
    )
    for side in [-1, 1]:
        p.hull.box(
            [1, BELT_TOP + 1.2 - DECK, CONVEYOR[2] - HEAD[1]],
            M.panel,
            Placement(pt(side * (w - 0.5), (HEAD[1] + CONVEYOR[2]) / 2, DECK)),
        )
    y = HEAD[1] + 4
    while y < CONVEYOR[2] - 1:
        p.bare.box([2 * w - 1.4, 0.3, 0.7], M.base, Placement(pt(0, y, BELT_TOP)))
        p.neon.box([0.5, 0.35, 1.2], N, Placement(pt(w - 0.5, y, BELT_TOP + 1.2)))
        p.neon.box([0.5, 0.35, 1.2], N, Placement(pt(-w + 0.5, y, BELT_TOP + 1.2)))
        y += 5
    # The intake ramp: a raised housing over the collar, the belt climbing into it.
    head = [
        flat(-w - 1.5, HEAD[0]),
        flat(w + 1.5, HEAD[0]),
        flat(w + 1.5, HEAD[1]),
        flat(-w - 1.5, HEAD[1]),
    ]
    p.hull.bevel_slab(head, [DECK, HEAD_TOP - 1.5, HEAD_TOP], [0, 0.8], M.panel, None, M.base)
    p.neon.box([2 * w + 2, 0.4, 0.4], N, Placement(pt(0, HEAD[0] + 0.3, HEAD_TOP - 1)))


def _hopper_bin(p: Any, b: list[Any]) -> None:
    """Draw an ore hopper's bin over the box `b`: tapered walls, a lit rim, its ore inside."""
    p.hull.bevel_slab(
        box_outline(b), [DECK, HOPPER_TOP - 1.2, HOPPER_TOP], [2.4, 0], M.panel, None, M.base
    )
    inner = [b[0] + 1.2, b[1] - 1.2, b[2] + 1.2, b[3] - 1.2]
    p.bare.slab(box_outline(inner), [ORE_TOP - 0.6, HOPPER_TOP + 0.05], M.dark)
    xm = (b[0] + b[1]) / 2
    ym = (b[2] + b[3]) / 2
    p.neon.box([b[1] - b[0] - 2, 0.4, 0.5], N, Placement(pt(xm, b[2] + 0.3, HOPPER_TOP - 0.2)))
    p.neon.box([b[1] - b[0] - 2, 0.4, 0.5], N, Placement(pt(xm, b[3] - 0.3, HOPPER_TOP - 0.2)))
    p.bare.box([0.6, 0.3, b[3] - b[2] - 2], M.dark, Placement(pt(xm, ym, HOPPER_TOP)))


def _rear_hoppers(p: Any) -> None:
    """Draw the rear hoppers (MB-DRILL-FORT-03), their ore: the core's (their guns rise out)."""
    for side in [-1, 1]:
        b = HOPPER_REAR
        box = [b[0], b[1], b[2], b[3]] if side > 0 else [-b[1], -b[0], b[2], b[3]]
        _hopper_bin(p, box)
        _ore_heap(p, box, ORE_TOP - 0.6, p.bare)


def _ore_heap(p: Any, b: list[Any], base: float, rock: Any) -> None:
    """Draw a heap of ore lumps (on the builder `rock`) in the box `b` from `base` up, glinting."""
    xm = (b[0] + b[1]) / 2
    ym = (b[2] + b[3]) / 2
    lumps = [[-3, -3, 2.2], [2.5, -2, 2.6], [-1, 2.5, 3], [3, 3.5, 1.8], [0, 0, 3.4]]
    for k in range(len(lumps)):
        q = lumps[k]
        rock.box([3.2, q[2], 3], ROCK, Placement(pt(xm + q[0], ym + q[1], base), k * 0.7))
    p.neon.box([0.8, 0.5, 0.8], N, Placement(pt(xm + 1, ym - 1, base + 3.2), 0.4))


def _stacks(p: Any) -> None:
    """Draw the exhaust stacks (MB-DRILL-FORT-01): tall banded pipes, a glowing mouth each."""
    for side in [-1, 1]:
        at = pt(side * STACK_AT[0], STACK_AT[1], DECK)
        p.hull.cylinder(STACK_RADIUS + 1.2, 2.5, 8, M.base, Placement(at))
        p.hull.cylinder(STACK_RADIUS, STACK_TOP - DECK, 8, M.panel, Placement(at))
        for h in [STACK_TOP - 6, STACK_TOP - 1.2]:
            p.bare.ring(STACK_RADIUS + 0.15, 1, 8, M.dark, Placement([at[0], h, at[2]]))
        p.neon.ring(STACK_RADIUS + 0.2, 0.5, 8, N, Placement([at[0], STACK_TOP - 3.5, at[2]]))
        p.reactor([at[0], STACK_TOP + 0.1, at[2]], STACK_RADIUS - 0.8)


def _cab(p: Any) -> None:
    """Draw the control cab at its back (MB-DRILL-FORT-01): a raised house, lit windows.

    A bevelled box over the conveyor's tail end, a band of windows round its front, an aerial on
    each back corner and the cab turret's seat on its roof.
    """
    outline = box_outline([-CAB[0], CAB[0], CAB[1], CAB[2]])
    p.hull.bevel_slab(outline, [DECK, CAB_TOP - 2, CAB_TOP], [0, 1.2], M.panel, None, M.base)
    p.neon.box([2 * CAB[0] - 3, 1, 0.4], N, Placement(pt(0, CAB[1] - 0.1, CAB_TOP - 5)))
    for side in [-1, 1]:
        p.neon.box(
            [0.4, 1, CAB[2] - CAB[1] - 4], N, Placement(pt(side * (CAB[0] + 0.1), 31, CAB_TOP - 5))
        )
        p.bare.cylinder(
            0.3, 7, 4, M.dark, Placement(pt(side * (CAB[0] - 1.5), CAB[2] - 1.5, CAB_TOP))
        )
    seat = pt(CAB_GUN_AT[0], CAB_GUN_AT[1], 0)
    p.hull.cylinder(5.4, 0.8, 10, M.base, Placement([seat[0], CAB_TOP - 0.2, seat[2]]))
    p.neon.ring(5.45, 0.3, 10, N, Placement([seat[0], CAB_TOP + 0.2, seat[2]]))


def _cheek(p: Any, at: Vec3) -> None:
    """Add a cheek casemate (MB-DRILL-FORT-04): an armoured sponson beside the drill.

    A wedge-fronted block on the body's front corner, its fixed twin cannon on top, lit seams round
    its front and a gun port collar.
    """
    side = -1 if at[0] > 0 else 1
    x = side * CHEEK_GUN_AT[0]
    outline = [
        flat(x - 5, -31),
        flat(x + 5, -31),
        flat(x + 5, -41),
        flat(x + 3, -44),
        flat(x - 3, -44),
        flat(x - 5, -41),
    ]
    p.hull.bevel_slab(outline, [BODY_LOW + 1, DECK - 1.5, DECK], [2, 0.8], M.panel, None, M.base)
    p.neon.box([6.5, 0.4, 0.4], N, Placement(pt(x, -43.6, DECK - 1)))
    for dx in [-4.7, 4.7]:
        p.neon.box([0.4, 0.4, 9], N, Placement(pt(x + dx, -36.5, DECK - 1)))
    p.bare.cylinder(4.4, 0.5, 8, M.dark, Placement(pt(x, CHEEK_GUN_AT[1], DECK - 0.3)))


def _drill(p: Any, _at: Vec3) -> None:
    """Add the drill head (MB-DRILL-FORT-02): a great cone on the collar's bearing.

    Its spiral flutes are the rig's; here the cone, a lit ring round its base and its tip.
    """
    length = CONE_BASE[0] - CONE_TIP
    base = pt(0, CONE_BASE[0], DRILL_AXIS)
    p.hull.cylinder(CONE_BASE[1], length, 12, M.panel, Placement(base, 0, QUARTER), 0.8)
    p.hull.cylinder(CONE_BASE[1] + 0.8, 2.5, 12, M.base, Placement(base, 0, QUARTER), CONE_BASE[1])
    p.neon.ring(
        CONE_BASE[1] + 0.85,
        0.6,
        12,
        N,
        Placement(pt(0, CONE_BASE[0] - 1.4, DRILL_AXIS), 0, QUARTER),
    )
    p.neon.cylinder(0.9, 2.5, 6, N, Placement(pt(0, CONE_TIP + 2.5, DRILL_AXIS), 0, QUARTER), 0.1)


def _front_hopper(side: float) -> Any:
    """Return the drawing of the front hopper on `side` (MB-DRILL-FORT-10), as it rests.

    A bin like the rear ones (its ore is armour of its own), a tipping hinge along its outer foot.
    """

    def draw(p: Any) -> None:
        b = HOPPER_FRONT
        box = [b[0], b[1], b[2], b[3]] if side > 0 else [-b[1], -b[0], b[2], b[3]]
        p.hull.bevel_slab(
            box_outline(box), [DECK, HOPPER_TOP - 1.2, HOPPER_TOP], [2.4, 0], M.panel, None, M.base
        )
        xm = (box[0] + box[1]) / 2
        for y in [b[2] + 0.3, b[3] - 0.3]:
            p.neon.box([b[1] - b[0] - 2, 0.4, 0.5], N, Placement(pt(xm, y, HOPPER_TOP - 0.2)))
        hinge = side * b[1]
        p.hull.cylinder(
            0.9, b[3] - b[2] - 2, 6, M.base, Placement(pt(hinge, b[3] - 1, DECK + 0.9), 0, QUARTER)
        )
        for y in [b[2] + 3, b[3] - 3]:
            p.bare.box([1.4, 2.2, 2], M.dark, Placement(pt(hinge - side * 0.6, y, DECK)))

    return draw


def _ore() -> Any:
    """Return the drawing of the ore loads in the front hoppers: they burst into lumps."""

    def draw(p: Any) -> None:
        for side in [-1, 1]:
            box = [ORE[0][0], ORE[1][0], ORE[0][1], ORE[2][1]]
            if side < 0:
                box = [-box[1], -box[0], box[2], box[3]]
            p.hull.slab(box_outline(box), [DECK + 0.5, ORE_TOP - 0.6], ROCK)
            _ore_heap(p, box, ORE_TOP - 0.6, p.hull)

    return draw


def _hatch(at: list[Any], half: list[Any], heights: list[Any], grate: bool) -> Any:
    """Return the drawing of a hatch round `at` (BOSS-58): a lid, a lit seam, bars or a cowl."""

    def draw(p: Any) -> None:
        b = [at[0] - half[0], at[0] + half[0], at[1] - half[1], at[1] + half[1]]
        top = heights[1]
        p.hull.bevel_slab(
            box_outline(b), [heights[0], top - 0.8, top], [0, 0.7], M.panel, None, M.base
        )
        c = pt(at[0], at[1], top)
        if grate:
            for k in range(-2, 3):
                p.bare.box(
                    [0.5, 0.4, 2 * half[1] - 1.5], M.dark, Placement([c[0] + k * 2.1, top, c[2]])
                )
        else:
            p.bare.box([2 * half[0] - 2, 0.4, 0.8], M.dark, Placement([c[0], top, c[2]]))
        p.neon.box(
            [2 * half[0] - 1.6, 0.35, 0.4], N, Placement([c[0], top - 0.5, c[2] - half[1] + 0.1])
        )

    return draw


def _hatch_frame(at: list[Any], half: list[Any], h: float) -> Any:
    """Return what a hatch leaves (BOSS-44): a dark collar round the opening, a lit lip."""

    def draw(p: Any) -> None:
        b = [at[0] - half[0], at[0] + half[0], at[1] - half[1], at[1] + half[1]]
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
        p.neon.box([b[1] - b[0] - 1, 0.3, 0.3], N, Placement([c[0], h + 0.6, c[2] - half[1] + 0.5]))

    return draw


def _armour() -> Any:
    """Return the drawings of its armour: the front hoppers, their ore, the hatches."""
    grate = [HOPPER_TOP - 0.6, HOPPER_TOP + 1.2]
    left_gun = [-HOPPER_GUN_AT[0], HOPPER_GUN_AT[1]]
    return {
        "hopper-right": {"whole": _front_hopper(1)},
        "hopper-left": {"whole": _front_hopper(-1)},
        "ore": {"whole": _ore()},
        "grate-left": {
            "whole": _hatch(left_gun, GRATE_HALF, grate, True),
            "frame": _hatch_frame(left_gun, GRATE_HALF, HOPPER_TOP),
        },
        "grate-right": {
            "whole": _hatch(HOPPER_GUN_AT, GRATE_HALF, grate, True),
            "frame": _hatch_frame(HOPPER_GUN_AT, GRATE_HALF, HOPPER_TOP),
        },
        "head-cowl": {
            "whole": _hatch(SPITTER_AT, COWL_HALF, [HEAD_TOP - 0.3, HEAD_TOP + 2.5], False),
            "frame": _hatch_frame(SPITTER_AT, COWL_HALF, HEAD_TOP),
        },
        "tail-cowl": {
            "whole": _hatch(ROTOR_AT, ROTOR_COWL, [BELT_TOP - 0.3, ROTOR_H + 3], False),
            "frame": _hatch_frame(ROTOR_AT, ROTOR_COWL, BELT_TOP + 0.4),
        },
    }


def build_drill_fort(scene: Any) -> Any:
    """MB-DRILL-FORT-01, MB-DRILL-FORT-04: the Drill Fort.

    A boxy armoured body on two track pontoons, a huge spiralled drill head at its front, a
    conveyor, ore hoppers, exhaust stacks and a control cab; amber lights (shown yellow); about
    3.4 L long.
    """

    def core(p: Any) -> None:
        _body(p)
        _tracks(p)
        _collar(p)
        _conveyor(p)
        _rear_hoppers(p)
        _stacks(p)
        _cab(p)

    return build_boss_model(
        DRILL_FORT,
        scene,
        N,
        {
            "core": core,
            "parts": {"gun-left": _cheek, "gun-right": _cheek, "drill": _drill},
            # MB-DRILL-FORT-05: its drill's flutes spin, its belt runs.
            "rig": {"build": build_drill_rig, "triangles": drill_rig_triangles},
            "armour": _armour(),
        },
    )
