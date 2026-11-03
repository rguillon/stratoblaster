# Copyright (c) 2026 Renaud Guillon
"""FB-STORM-PETREL-02, FB-STORM-PETREL-05: the Storm Petrel's wings, drawn in two pieces a side.

Each wing is a membrane on bone struts, split at its hinge (`HINGE_X`): its root, between the body
and the hinge, with the engine sac on it (the armour the `wing-roots` region sheds, D-254), and its
outer wing, beyond the hinge, with the gland at its tip (the piece that swings forward,
FB-STORM-PETREL-10). Both are drawn in model space as they rest on the boss: the engine toggles and
moves them. Logical pixels, nose +Z, Y up (towards the camera); `s` is the model side (1: +X).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.final_boss_shapes import edge_strips, shift, sided
from game.view.bosses.world_1_organic_kit import F, gland, graft, polygon, tentacle, vein_line
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import SegmentedBody, segmented_body
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["storm-petrel"]

# Where each wing hinges: the outer wing swings about the root of its leading edge there.
HINGE_X = 31
# The right wing's membrane, split at the hinge: its root (reaching into the body's flank, so it
# holds to it) and its outer wing, the tip squared off (the gun pod sits near it).
ROOT_WING = [
    [11, 19.1],
    [HINGE_X, 13.4],
    [HINGE_X, -13.8],
    [30, -14],
    [11, -19.2],
]
OUTER_WING = [
    [HINGE_X, 13.4],
    [36, 12],
    [74, 3],
    [77, -1],
    [76, -7],
    [56, -10],
    [HINGE_X, -13.8],
]
# Neon along the right wing's leading edge and around its tip, just proud of the edge, split at
# the hinge.
ROOT_LEAD = [
    [13, 19.4],
    [HINGE_X, 14.2],
]
OUTER_LEAD = [
    [HINGE_X, 14.2],
    [36, 12.8],
    [74.4, 3.8],
    [77.8, -1],
    [76.8, -7.6],
]
# The bone struts of the right wing, from its root out (x, z of their ends), and their radii at
# the root and the tip; each is drawn in two lengths, split at the hinge.
STRUTS = [
    [
        [10, 16],
        [74, 2],
    ],
    [
        [10, 4],
        [70, -8],
    ],
    [
        [10, -8],
        [46, -11],
    ],
]
STRUT_RADII = [1.8, 0.5]
STRUT_Y = 9
# The vein across the right wing (its ends), split at the hinge.
VEIN = [
    [12, 9.8, -2],
    [60, 9.7, -6],
]
# The wing membrane's heights (bottom, waist, top) and where the engine sac stands on the root.
WING_Y = [6, 7.5, 9.5]
NACELLE_X = 24
NACELLE_Y = 7


def _at_x(start: list[Any], end: list[Any], x: float) -> list[Any]:
    """Return the point of the segment from `start` to `end` (2 or 3 coordinates) at `x`."""
    k = (x - start[0]) / (end[0] - start[0])
    return [start[i] + (end[i] - start[i]) * k for i in range(len(start))]


def _sided(point: Vec3, s: float) -> Vec3:
    """`point` on side `s` (its X mirrored when `s` is -1)."""
    return [s * point[0], point[1], point[2]]


def _membrane(p: Any, s: float, outline: list[Any], lead: list[Any]) -> None:
    """Draw a length of wing membrane (`outline`), neon along its leading edge (`lead`)."""
    p.flesh.bevel_slab(sided(outline, s), WING_Y, [1.2, 1.8], F.membrane, None, F.graphite)
    edge_strips(p.neon, sided(lead, s), 1.2, [6.9, 8.1], N)


def _struts(p: Any, s: float, outer: bool) -> None:
    """Draw the bone struts of a wing on side `s`: their outer lengths, or the ones to the hinge."""
    for strut in STRUTS:
        root = strut[0]
        tip = strut[1]
        hinge = _at_x(root, tip, HINGE_X)
        k = (HINGE_X - root[0]) / (tip[0] - root[0])
        r = STRUT_RADII[0] + (STRUT_RADII[1] - STRUT_RADII[0]) * k
        start = hinge if outer else root
        end = tip if outer else hinge
        radii = [r, STRUT_RADII[1]] if outer else [STRUT_RADII[0], r]
        tentacle(
            p,
            [s * start[0], STRUT_Y, start[1]],
            [s * end[0], STRUT_Y, end[1]],
            [0, 1.2, 0],
            radii,
            F.bone,
            4,
        )


def _vein(p: Any, s: float, outer: bool) -> None:
    """Draw the vein across a wing on side `s`: its outer length, or the one to the hinge."""
    hinge = _at_x(VEIN[0], VEIN[1], HINGE_X)
    start = hinge if outer else VEIN[0]
    end = VEIN[1] if outer else hinge
    vein_line(p, _sided(start, s), _sided(end, s), [0, 0.4, 1], 1.1, N)


def _nacelle(p: Any, s: float) -> None:
    """Draw the engine sac on a wing root: a segmented sac, its reactor at its tail.

    A grafted plate and an intake ring on its nose, both set on it.
    """
    nacelle = [s * NACELLE_X, NACELLE_Y, 0]
    segmented_body(
        p.flesh,
        SegmentedBody(-19, 19, 3, 5.5, -1, 9),
        F.slate,
        Placement(nacelle),
    )
    graft(p, polygon(5, 3.4), [7.4, 8.4], shift(nacelle, [0, 0, 12]))
    p.neon.ring(3.6, 0.8, 6, N, Placement(shift(nacelle, [0, 3.8, 15.5]), 0, math.pi / 2))
    reactor_sac(p, shift(nacelle, [0, 3.5, -19.2]), 3.2, N)


def wing_root(s: float) -> Any:
    """Return the drawing of the wing root on side `s` (the `wing-roots` armour, D-254).

    The membrane from the body's flank to the hinge, the struts' and the vein's inner lengths, the
    neon of the leading edge there, and the engine sac standing on it.
    """

    def draw(p: Any) -> None:
        _membrane(p, s, ROOT_WING, ROOT_LEAD)
        _struts(p, s, False)
        _vein(p, s, False)
        _nacelle(p, s)

    return draw


def outer_wing(s: float) -> Any:
    """Return the drawing of the outer wing on side `s` (the `outer-wings` moving piece).

    The membrane beyond the hinge, the struts' and the vein's outer lengths, the neon round the
    leading edge and the tip, and the gland at the tip.
    """

    def draw(p: Any) -> None:
        _membrane(p, s, OUTER_WING, OUTER_LEAD)
        _struts(p, s, True)
        _vein(p, s, True)
        gland(p, [s * 76.6, 8.6, -3.5], 1.2, N)

    return draw


def draw_floats(p: Any) -> None:
    """Draw the float of flesh under each wing root (the core's), up against the membrane."""
    for s in [-1, 1]:
        segmented_body(
            p.flesh,
            SegmentedBody(-14, 24, 2, 4, 0, 7),
            F.sinew,
            Placement([s * 20, -1, 0]),
        )
