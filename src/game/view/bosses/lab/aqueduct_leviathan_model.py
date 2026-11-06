# Copyright (c) 2026 Renaud Guillon
"""FB-AQUEDUCT-LEVIATHAN-01 to -05: the Aqueduct Leviathan, the Lab's L-23 final boss.

Logical pixels, nose +Z, Y up (towards the camera). A gigantic flying viaduct across the screen:
five stone piers with pointed cutwaters, iron arch ribs between them on stringers, a channel of
glowing water along its whole top, a keep over its middle pier, gate towers on its abutments (its
parts), lift engines slung before its outer piers (their fans are its rig,
`aqueduct_leviathan_rig`). A machine and a building, not a creature: the Lab's fifth round builds
flying fortresses (user request, 2026-11-06).
"""

from game.config.bosses.lab.aqueduct_leviathan import (
    ABUTMENT,
    ABUTMENT_HALF,
    AQUEDUCT_LEVIATHAN,
    CHANNEL_HALF,
    CHANNEL_TOP,
    CUT_SQUARE,
    CUT_TIP,
    CUTWATER,
    CUTWATER_LOW,
    KEEP_DEPTH,
    KEEP_HALF,
    KEEP_LASER_AT,
    KEEP_LASER_H,
    KEEP_TOP,
    OUTER_GUN_AT,
    PIER_DEPTH,
    PIER_HALF,
    PIER_TOP,
    PIERS,
    RIB,
    SLUICE,
    SPRING,
)
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.aqueduct_leviathan_kit import (
    COURSE,
    STONE,
    N,
    block,
    box_outline,
    channel,
    flat,
    pt,
    rib,
)
from game.view.bosses.lab.aqueduct_leviathan_parts import (
    aqueduct_armour,
    arch_gun,
    engine,
    gun_housing,
    tower,
)
from game.view.bosses.lab.aqueduct_leviathan_rig import build_fan_rig, fan_triangles
from game.view.bosses.world_1_organic_kit import M
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# The spans between its piers (the right ones; mirrored): `[x0, x1]` between their faces.
SPANS = [[6, 30], [42, 66], [78, 94]]


def _pier(p: Any, x: float, front: bool) -> None:
    """Draw a pier at `x`: dressed stone, pointed cutwaters, darker courses, lit seams.

    `front`: whether its front cutwater is its own (the keep pier's is armour above `CUTWATER_LOW`,
    only its foot drawn here).
    """
    w = PIER_HALF
    back = [
        flat(x - w, -PIER_DEPTH),
        flat(x + w, -PIER_DEPTH),
        flat(x + w, CUT_SQUARE),
        flat(x, CUT_TIP),
        flat(x - w, CUT_SQUARE),
    ]
    if front:
        back = [
            flat(x - w, -CUT_SQUARE),
            flat(x, -CUT_TIP),
            flat(x + w, -CUT_SQUARE),
            flat(x + w, CUT_SQUARE),
            flat(x, CUT_TIP),
            flat(x - w, CUT_SQUARE),
        ]
    else:
        foot = [flat(x + q[0], q[1]) for q in CUTWATER]
        p.hull.bevel_slab(foot, [0, CUTWATER_LOW - 0.5, CUTWATER_LOW], [1, 0], STONE, None, COURSE)
    p.hull.bevel_slab(back, [0, PIER_TOP - 1, PIER_TOP], [1.5, 0.6], STONE, None, COURSE)
    for h in [5.5, 11]:
        block(
            p.bare,
            [x - w - 0.15, x + w + 0.15, -PIER_DEPTH + 1, PIER_DEPTH - 1],
            [h, h + 0.8],
            COURSE,
        )
    tips = [CUT_TIP - 0.4] if not front else [-CUT_TIP + 0.4, CUT_TIP - 0.4]
    for y in tips:
        p.neon.box([0.5, 10, 0.5], N, Placement(pt(x, y, PIER_TOP - 11)))
    p.neon.box([2 * w - 1, 0.4, 0.4], N, Placement(pt(x, PIER_DEPTH - 0.3, PIER_TOP)))


def _span(p: Any, x0: float, x1: float) -> None:
    """Draw a span from `x0` to `x1`: an iron rib front and back on stringers, ties across.

    The stringers along the ribs' tops carry the channel; struts stand on the ribs' haunches.
    """
    w = (x1 - x0) / 2
    c = (x0 + x1) / 2
    for side in [-1, 1]:
        y0 = RIB[0] if side < 0 else -RIB[1]
        y1 = RIB[1] if side < 0 else -RIB[0]
        rib(p, x0, x1, y0, y1)
        top = SPRING + w
        block(p.hull, [x0, x1, y0 + 0.4, y1 - 0.4], [top, PIER_TOP], M.panel)
        for k in [-1, 1]:
            xs = c + k * w * 0.62
            block(p.bare, [xs - 0.5, xs + 0.5, y0 + 1, y1 - 1], [SPRING + w * 0.7, top], M.base)
    for xs in [c - w * 0.5, c + w * 0.5]:
        block(
            p.hull,
            [xs - 0.8, xs + 0.8, RIB[0] + 0.5, -RIB[0] - 0.5],
            [PIER_TOP - 1.2, PIER_TOP],
            M.base,
        )


def _abutment(p: Any, side: float) -> None:
    """Draw an abutment at its end on `side`: a stone block the gate tower stands on."""
    b = [ABUTMENT[0], ABUTMENT[1]] if side > 0 else [-ABUTMENT[1], -ABUTMENT[0]]
    outline = box_outline([b[0], b[1], -ABUTMENT_HALF, ABUTMENT_HALF])
    p.hull.bevel_slab(outline, [0, PIER_TOP - 1, PIER_TOP], [2, 0.6], STONE, None, COURSE)
    for h in [5.5, 11]:
        block(
            p.bare,
            [b[0] - 0.15, b[1] + 0.15, -ABUTMENT_HALF + 1.5, ABUTMENT_HALF - 1.5],
            [h, h + 0.8],
            COURSE,
        )
    for y in [-ABUTMENT_HALF + 0.2, ABUTMENT_HALF - 0.2]:
        p.neon.box(
            [b[1] - b[0] - 3, 0.4, 0.4], N, Placement(pt((b[0] + b[1]) / 2, y, PIER_TOP - 0.6))
        )


def _keep(p: Any) -> None:
    """Draw the keep over the middle pier (FB-AQUEDUCT-LEVIATHAN-01): a tall square tower.

    Its walls from the pier up past the channel (dark gates where the channel runs through),
    merlons round its roof, a pinnacle at each corner, lit slits, the turret's seat on its roof and
    the laser's bracket on its face.
    """
    h0 = PIER_TOP - 6
    outline = box_outline([-KEEP_HALF, KEEP_HALF, -KEEP_DEPTH, KEEP_DEPTH])
    p.hull.bevel_slab(outline, [h0, KEEP_TOP - 1.5, KEEP_TOP], [0, 1], STONE, None, M.panel)
    for x in [-KEEP_HALF - 0.1, KEEP_HALF + 0.1]:
        block(
            p.bare,
            [x - 0.2, x + 0.2, -CHANNEL_HALF, CHANNEL_HALF],
            [PIER_TOP + 0.5, CHANNEL_TOP + 2],
            M.dark,
        )
    merlon = [KEEP_TOP, KEEP_TOP + 2.5]
    for k in range(3):
        u = -KEEP_HALF + 4.5 + k * (KEEP_HALF - 4.5)
        v = -KEEP_DEPTH + 4.5 + k * (KEEP_DEPTH - 4.5)
        for y in [-KEEP_DEPTH + 0.8, KEEP_DEPTH - 0.8]:
            block(p.hull, [u - 1.2, u + 1.2, y - 0.8, y + 0.8], merlon, STONE)
        for x in [-KEEP_HALF + 0.8, KEEP_HALF - 0.8]:
            block(p.hull, [x - 0.8, x + 0.8, v - 1.2, v + 1.2], merlon, STONE)
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            corner = pt(sx * (KEEP_HALF - 1), sy * (KEEP_DEPTH - 1), KEEP_TOP)
            p.hull.cylinder(1.8, 5, 6, M.panel, Placement(corner), 0.6)
            p.neon.box([0.6, 1, 0.6], N, Placement([corner[0], KEEP_TOP + 5, corner[2]]))
    for x in [-5, 5]:
        p.neon.box([1, 4, 0.4], N, Placement(pt(x, -KEEP_DEPTH - 0.1, KEEP_TOP - 11)))
    p.neon.box([2 * KEEP_HALF - 2, 0.6, 0.4], N, Placement(pt(0, -KEEP_DEPTH - 0.1, KEEP_TOP - 4)))
    seat = pt(0, 0, KEEP_TOP)
    p.hull.cylinder(6.2, 0.8, 12, M.base, Placement(seat))
    p.neon.ring(6.25, 0.3, 12, N, Placement([seat[0], KEEP_TOP + 0.4, seat[2]]))
    b = [KEEP_LASER_AT[0] - 3.5, KEEP_LASER_AT[0] + 3.5, KEEP_LASER_AT[1] - 2.5, -KEEP_DEPTH + 0.5]
    block(p.hull, b, [KEEP_LASER_H - 5, KEEP_LASER_H], M.panel)


def _channel(p: Any) -> None:
    """Draw the water channel (FB-AQUEDUCT-LEVIATHAN-01) but for its middle sections (armour)."""
    a = SLUICE[0] - 0.5
    b = ABUTMENT[0] + 1
    channel(p, a, b)
    channel(p, -b, -a)


def build_aqueduct_leviathan(scene: Any) -> Any:
    """FB-AQUEDUCT-LEVIATHAN-01, FB-AQUEDUCT-LEVIATHAN-04: the Aqueduct Leviathan.

    A flying viaduct of five stone piers and iron arches carrying a glowing channel, a keep over its
    middle, gate towers at its ends; steel-blue lights (shown green); about 6.7 L across.
    """

    def core(p: Any) -> None:
        for x in PIERS:
            _pier(p, x, x != 0)
        for span in SPANS:
            _span(p, span[0], span[1])
            _span(p, -span[1], -span[0])
        _abutment(p, 1)
        _abutment(p, -1)
        _channel(p)
        _keep(p)
        for x in [-OUTER_GUN_AT[0], OUTER_GUN_AT[0]]:
            gun_housing(p, x, SPRING + (SPANS[2][1] - SPANS[2][0]) / 2 - 0.5)

    return build_boss_model(
        AQUEDUCT_LEVIATHAN,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "arch-gun-left": arch_gun,
                "arch-gun-right": arch_gun,
                "engine-left": engine,
                "engine-right": engine,
                "tower-left": tower,
                "tower-right": tower,
            },
            # FB-AQUEDUCT-LEVIATHAN-05: its lift fans spin.
            "rig": {"build": build_fan_rig, "triangles": fan_triangles},
            "armour": aqueduct_armour(),
        },
    )
