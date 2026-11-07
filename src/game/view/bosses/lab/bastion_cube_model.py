# Copyright (c) 2026 Renaud Guillon
"""MB-BASTION-CUBE-01 to MB-BASTION-CUBE-05: the Bastion Cube, the Lab's L-7 mini boss.

Logical pixels, nose +Z, Y up (towards the camera). A square block fortress seen from above: a
cross-shaped plinth with crenellated curtain walls, a ziggurat of plated steel tiers up to the keep
on its summit, a gatehouse jutting out of its front. Its four corner blocks, each with a drum tower,
are moving pieces of their own (`bastion_cube_blocks`): they slide out as it transforms, baring the
lit rails and machinery of the corner notches they filled.
"""

import math

from game.config.bosses.lab.bastion_cube import (
    BASTION_CUBE,
    GATE_FRONT,
    GATE_HALF,
    GATE_TOP,
    HALF,
    KEEP_GUN_AT,
    NOTCH,
    PLINTH_TOP,
    ROTOR_AT,
    TIERS,
    TOWER_RADIUS,
    TOWER_TOP,
)
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_greebles import SHADE, grille, plate, rect
from game.view.bosses.final_boss_mechanism import conduit
from game.view.bosses.final_boss_shapes import edge_strips
from game.view.bosses.lab.bastion_cube_blocks import (
    N,
    cube_blocks,
    merlons,
    model_outline,
    pt,
    square,
)
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


# The plinth's outline (config, X right, Y up): the cube's square with a notch cut out of each
# corner, where a corner block sits.
PLINTH = [
    [-NOTCH, -HALF],
    [NOTCH, -HALF],
    [NOTCH, -NOTCH],
    [HALF, -NOTCH],
    [HALF, NOTCH],
    [NOTCH, NOTCH],
    [NOTCH, HALF],
    [-NOTCH, HALF],
    [-NOTCH, NOTCH],
    [-HALF, NOTCH],
    [-HALF, -NOTCH],
    [-NOTCH, -NOTCH],
]
CORNERS = [[1, 1], [1, -1], [-1, 1], [-1, -1]]


def _chamfered(half: float, cut: float) -> list[Any]:
    """Return a square `half` px either side of the centre, its corners cut `cut` px (config)."""
    return [
        [-half + cut, -half],
        [half - cut, -half],
        [half, -half + cut],
        [half, half - cut],
        [half - cut, half],
        [-half + cut, half],
        [-half, half - cut],
        [-half, -half + cut],
    ]


def _draw_plinth(p: Any) -> None:
    """Draw the plinth (MB-BASTION-CUBE-02): the cross-shaped base, crenellated curtain walls.

    A lit line round its top, and merlons along its four outer walls (the gatehouse's stretch of
    the front left out).
    """
    p.hull.bevel_slab(
        model_outline(PLINTH),
        [0, PLINTH_TOP - 1.4, PLINTH_TOP],
        [0, 1.2],
        SHADE["dark"],
        None,
        M_BASE,
    )
    for s in [-1, 1]:
        wall = HALF - 1.5
        merlons(p, [[s * wall, -NOTCH + 3], [s * wall, NOTCH - 3]], 6, PLINTH_TOP, 0, 0)
        merlons(p, [[s * (NOTCH - 3), wall], [s * (GATE_HALF - 6), wall]], 3, PLINTH_TOP, 0, 0)
        merlons(p, [[s * (NOTCH - 3), -wall], [s * (GATE_HALF + 3), -wall]], 2, PLINTH_TOP, 0, 0)
        # The outer walls' lit lines, just under their merlons.
        edge_strips(
            p.neon,
            [_m(s * (HALF + 0.1), -NOTCH + 1), _m(s * (HALF + 0.1), NOTCH - 1)],
            0.5,
            [PLINTH_TOP - 3.6, PLINTH_TOP - 2.8],
            N,
        )
        edge_strips(
            p.neon,
            [_m(s * (NOTCH - 1), HALF + 0.1), _m(s * 1, HALF + 0.1)],
            0.5,
            [PLINTH_TOP - 3.6, PLINTH_TOP - 2.8],
            N,
        )
    # The rear gate: a sealed door in the middle of the back wall, its frame lit.
    p.hull.box([12, 7, 2], SHADE["dark"], Placement(pt(0, HALF - 0.6, 0)), SHADE["mid"])
    p.neon.box([13, 0.6, 2.2], N, Placement(pt(0, HALF - 0.5, 7)))


def _m(x: float, y: float) -> list[Any]:
    """Return the config point `(x, y)` as a model `[x, z]`."""
    return [-x, -y]


def _draw_notches(p: Any) -> None:
    """Draw the corner notches (MB-BASTION-CUBE-05), under the corner blocks at rest.

    A dark floor with two lit rails running out diagonally (the blocks slide out along them), and
    on the notch's inner walls a lit slot and a ribbed conduit (the machinery the blocks bare).
    """
    for c in CORNERS:
        sx = c[0]
        sy = c[1]
        floor = square([sx * (NOTCH + 10), sy * (NOTCH + 10)], 9.5)
        p.hull.slab(model_outline(floor), [0, 1.2], SHADE["dark"])
        for k in [-1, 1]:
            a = _m(sx * (NOTCH + 2 + 2.5 * (1 + k)), sy * (NOTCH + 2 + 2.5 * (1 - k)))
            b = _m(sx * (HALF - 6 + 2.5 * (1 + k)), sy * (HALF - 6 + 2.5 * (1 - k)))
            edge_strips(p.neon, [a, b], 0.9, [1.2, 1.7], N)
        # The inner walls' slots: one on each wall of the notch, and a conduit along their foot.
        p.neon.box([0.5, 4, 9], N, Placement(pt(sx * (NOTCH + 0.1), sy * (NOTCH + 10), 3)))
        p.neon.box([9, 4, 0.5], N, Placement(pt(sx * (NOTCH + 10), sy * (NOTCH + 0.1), 3)))
        conduit(
            p.hull,
            pt(sx * (NOTCH + 1.6), sy * (NOTCH + 3), 2.4),
            pt(sx * (NOTCH + 1.6), sy * (HALF - 3), 2.4),
            [1.1, 3],
        )
        conduit(
            p.hull,
            pt(sx * (NOTCH + 3), sy * (NOTCH + 1.6), 2.4),
            pt(sx * (HALF - 3), sy * (NOTCH + 1.6), 2.4),
            [1.1, 3],
        )


M_BASE = SHADE["base"]
M_PANEL = SHADE["panel"]


def _draw_tiers(p: Any) -> None:
    """Draw the ziggurat (MB-BASTION-CUBE-02): plated steel tiers stepping up to the keep.

    Each tier a chamfered square slab, a lit line round its top edge; plates on the faces of the
    lower tiers, vent grilles at the back, the keep's lit crown on the summit.
    """
    low = PLINTH_TOP - 1
    tiers: list[Any] = TIERS
    for k in range(len(tiers)):
        half = tiers[k][0]
        top = tiers[k][1]
        cut = 4 if k < 2 else 3
        color = M_BASE if k % 2 == 0 else M_PANEL
        p.hull.bevel_slab(
            model_outline(_chamfered(half, cut)), [low, top - 1.2, top], [0, 1], color, None
        )
        ring = _chamfered(half - 1.6, cut)
        points = [_m(q[0], q[1]) for q in ring]
        points.append(points[0])
        edge_strips(p.neon, points, 0.45, [top + 0.02, top + 0.12], N)
        low = top - 0.5
    # Armour plates on the first tier's top, between its corners: one a side.
    first: list[Any] = TIERS[0]
    second: list[Any] = TIERS[1]
    mid = (first[0] + second[0]) / 2
    span = second[0] * 1.2
    for s in [-1, 1]:
        plate(
            p.hull, rect(_m(s * mid, 0), [first[0] - second[0] - 3, span]), first[1], SHADE["light"]
        )
        plate(
            p.hull, rect(_m(0, s * mid), [span, first[0] - second[0] - 3]), first[1], SHADE["light"]
        )
    # Vent grilles on the second tier's back, and studs of light on its front corners.
    grille(p.hull, _m(0, second[0] - 4), [14, 5], [4, second[1] + 0.05])
    for s in [-1, 1]:
        p.neon.box(
            [1.4, 0.4, 1.4], N, Placement(pt(s * (second[0] - 3), -second[0] + 3, second[1]))
        )


def _draw_keep(p: Any) -> None:
    """Draw the keep on the summit: its turret's seat, lit corner posts, the rotor's hatch frame."""
    summit: list[Any] = TIERS[2]
    top = summit[1]
    seat = pt(KEEP_GUN_AT[0], KEEP_GUN_AT[1], top - 0.6)
    p.hull.cylinder(5.6, 0.8, 8, SHADE["dark"], Placement(seat, math.pi / 8))
    for c in CORNERS:
        at = pt(c[0] * (summit[0] - 2.5), c[1] * (summit[0] - 2.5), top - 0.4)
        p.hull.box([3, 2.4, 3], SHADE["light"], Placement(at))
        p.neon.box([1.6, 0.4, 1.6], N, Placement([at[0], top + 2, at[2]]))
    # The collar the crown rotor rises out of (its hatch is drawn apart).
    p.hull.ring(5.4, 1, 12, SHADE["dark"], Placement(pt(ROTOR_AT[0], ROTOR_AT[1], top - 0.4)))


def _draw_gate_base(p: Any) -> None:
    """Draw the gatehouse's foot on the front wall (what stays once the gatehouse is gone)."""
    foot = [
        [-GATE_HALF, GATE_FRONT],
        [GATE_HALF, GATE_FRONT],
        [GATE_HALF, -HALF + 2],
        [-GATE_HALF, -HALF + 2],
    ]
    p.hull.bevel_slab(model_outline(foot), [0, 5.4, 6.2], [0, 0.8], SHADE["mid"])
    edge_strips(
        p.neon,
        [_m(-GATE_HALF + 1, GATE_FRONT - 0.1), _m(GATE_HALF - 1, GATE_FRONT - 0.1)],
        0.5,
        [3, 3.8],
        N,
    )


def _gatehouse(p: Any, _at: Vec3) -> None:
    """Add the gatehouse (MB-BASTION-CUBE-03): a squat gate tower over the front wall.

    Its two flanking bastions, a lit portcullis in its face, battlements round its roof; the wall
    gun stands on its front.
    """
    front = GATE_FRONT
    back = -HALF + 8
    body = [
        [-GATE_HALF + 2, front + 1],
        [GATE_HALF - 2, front + 1],
        [GATE_HALF - 2, back],
        [-GATE_HALF + 2, back],
    ]
    p.hull.bevel_slab(model_outline(body), [6, GATE_TOP - 1.2, GATE_TOP], [0, 1], M_PANEL)
    for s in [-1, 1]:
        bastion = square([s * (GATE_HALF - 1.5), front + 5], 3.5)
        p.hull.bevel_slab(
            model_outline(bastion), [6, GATE_TOP + 0.5, GATE_TOP + 2.5], [0, 0.8], SHADE["mid"]
        )
        p.neon.box(
            [1.2, 0.4, 1.2], N, Placement(pt(s * (GATE_HALF - 1.5), front + 5, GATE_TOP + 2.5))
        )
    # The portcullis: lit bars in a dark doorway on its face.
    p.hull.box([10, 7, 0.8], SHADE["dark"], Placement(pt(0, front + 0.6, 7)))
    for k in range(4):
        x = -3.6 + k * 2.4
        p.neon.box([0.5, 6, 0.4], N, Placement(pt(x, front + 0.3, 7.4)))
    p.neon.box([10, 0.5, 0.4], N, Placement(pt(0, front + 0.3, 13.6)))
    merlons(p, [[-GATE_HALF + 4, back + 1], [GATE_HALF - 4, back + 1]], 4, GATE_TOP, 0, 0)


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over the crown rotor (BOSS-58): an octagonal steel cap, a lit seam round it.

    It bursts off as the rotor comes into use.
    """
    top = TIERS[2][1]
    at = pt(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.bevel_slab(
        square_cap(5.8), [top - 0.4, top + 0.6, top + 1.4], [0, 0.6], M_PANEL, Placement(at)
    )
    p.hull.box([6.4, 0.5, 1.2], SHADE["dark"], Placement(pt(ROTOR_AT[0], ROTOR_AT[1], top + 1.3)))
    p.neon.ring(5.6, 0.3, 8, N, Placement([at[0], top + 0.7, at[2]], math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a lit collar round the opening the rotor rises from."""
    top = TIERS[2][1]
    at = pt(ROTOR_AT[0], ROTOR_AT[1], top)
    p.neon.ring(5.5, 0.4, 12, N, Placement(at))


def square_cap(radius: float) -> list[Any]:
    """Return an octagon `radius` px round its centre (model)."""
    return [
        [
            radius * math.cos(math.pi / 8 + k * math.pi / 4),
            radius * math.sin(math.pi / 8 + k * math.pi / 4),
        ]
        for k in range(8)
    ]


def build_bastion_cube(scene: Any) -> Any:
    """MB-BASTION-CUBE-01, MB-BASTION-CUBE-04: the Bastion Cube.

    A square, stepped block fortress 3.6 L across with coral lights: its front towers' turrets,
    its gatehouse's wall gun, the keep's turret and the crown rotor (their mounts, drawn by
    `build_boss_model`, BOSS-58). Its corner blocks slide out at its transformation
    (MB-BASTION-CUBE-05).
    """

    def core(p: Any) -> None:
        _draw_plinth(p)
        _draw_notches(p)
        _draw_tiers(p)
        _draw_keep(p)
        _draw_gate_base(p)

    armour = cube_blocks()
    armour["rotor-hatch"] = {"whole": _draw_hatch, "frame": _draw_hatch_frame}
    return build_boss_model(
        BASTION_CUBE,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "tower-left": _tower_crown,
                "tower-right": _tower_crown,
                "gatehouse": _gatehouse,
            },
            "armour": armour,
        },
    )


def _tower_crown(p: Any, at: Vec3) -> None:
    """Add a front tower's crown (MB-BASTION-CUBE-03): the battlemented ring its turret stands in.

    A lit band round it and four merlons; the drum it stands on is its corner block's.
    """
    top = TOWER_TOP
    r = TOWER_RADIUS
    p.hull.lathe(
        [[r - 1.6, top - 2.6], [r + 0.8, top - 2.6], [r + 0.8, top], [r - 1.6, top]],
        8,
        M_PANEL,
        Placement([at[0], 0, at[2]], math.pi / 8),
    )
    p.neon.ring(r + 0.9, 0.7, 8, N, Placement([at[0], top - 2, at[2]], math.pi / 8))
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        q = [at[0] + math.cos(a) * (r - 0.3), top, at[2] + math.sin(a) * (r - 0.3)]
        p.hull.box([2.6, 2, 2.6], SHADE["light"], Placement(q, a))
