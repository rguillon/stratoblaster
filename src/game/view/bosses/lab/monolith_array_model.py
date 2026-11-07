# Copyright (c) 2026 Renaud Guillon
"""MB-MONOLITH-ARRAY-01 to MB-MONOLITH-ARRAY-05, Lab L-10: the Monolith Array.

Logical pixels, nose +Z, Y up (towards the camera). Three tall, dark obelisks hovering in a row
over a low platform of stone slabs and metal, each on a glowing pylon: the big central one (the
core) capped by its rotor's collar, the two side ones (its parts) pointed, their laser emitters set
in their front faces; cyan glyphs cut into their faces and channels of light linking their feet.
Machined stone and metal, no creature (the user's request of 2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.monolith_array import (
    CORE_AT,
    CORE_FOOT,
    CORE_HEAD,
    CORE_HOVER,
    CORE_TOP,
    EMITTER_HEIGHT,
    EMITTER_Y,
    MONOLITH_ARRAY,
    PLATFORM_HALF,
    PLATFORM_TOP,
    PLINTH_HEIGHTS,
    PLINTH_OUTLINE,
    SIDE_AT,
    SIDE_FOOT,
    SIDE_HEAD,
    SIDE_HOVER,
    SIDE_TOP,
    SIDE_X,
    SIGHT_AT,
    SIGHT_HEIGHT,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.monolith_array_kit import (
    BASALT,
    PALE,
    STEEL,
    STONE,
    chamfered,
    frustum,
    glyph,
    glyphs,
)
from game.view.bosses.mini_boss_shapes import neon_band
from game.view.enemies.enemy_shapes import decal
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["monolith-array"]
# The capstone collar under the crown rotor: its half sizes, from the shaft's head up to the top.
COLLAR = [8, 6.4]
COLLAR_FOOT = CORE_TOP - 4.5
# The side monoliths' pointed tips: how high over their heads.
POINT = 9


def _xz(x: float, y: float) -> list[float]:
    """Return the model `[x, z]` of the config point `[x, y]`."""
    return [-x, -y]


def _platform() -> list[list[float]]:
    """Return the platform's whole outline (model `[x, z]`): its right half and its mirror."""
    n = len(PLATFORM_HALF)
    result = [_xz(q[0], q[1]) for q in PLATFORM_HALF]
    result.extend([
        _xz(-PLATFORM_HALF[n - 2 - k][0], PLATFORM_HALF[n - 2 - k][1]) for k in range(n - 2)
    ])
    return result


def _pylon(p: Any, at: list[Any], radius: float, top: float) -> None:
    """Add the glowing pylon an obelisk hovers on: a dark hexagonal stem, rings of light round."""
    foot = boss_point(at[0], at[1], PLATFORM_TOP - 0.2)
    p.hull.cylinder(radius + 1.5, 1.2, 6, STEEL, Placement(foot, math.pi / 6))
    p.hull.cylinder(
        radius, top - PLATFORM_TOP + 0.4, 6, BASALT, Placement(foot, math.pi / 6), radius * 0.8
    )
    for k in range(2):
        h = PLATFORM_TOP + 1.4 + k * (top - PLATFORM_TOP - 2.4)
        p.neon.ring(
            radius + 0.15 - k * 0.2, 0.55, 6, N, Placement(boss_point(at[0], at[1], h), math.pi / 6)
        )


def _shaft(p: Any, at: list[Any], sizes: list[Any], heights: list[Any], first: int) -> list[Any]:
    """Add an obelisk's shaft at config `at`, from its foot `sizes[0]` to its head `sizes[1]`.

    Between `heights[0]` and `heights[1]`, its corners chamfered; glyphs on its four broad faces
    (patterns from `first` on), neon along its two front chamfers. Returns its head's outline.
    """
    centre = _xz(at[0], at[1])
    foot = chamfered(centre, sizes[0], 2.2)
    head = chamfered(centre, sizes[1], 1.3)
    faces = frustum(p.hull, [foot, head], heights, STONE, BASALT)
    # The broad faces: right (+X), front (+Z), left, back, in the chamfered outline's order.
    for k in range(4):
        glyphs(p.neon, faces[k * 2], first + k, N)
    # The front chamfers (towards the nose, +Z): a lit seam up each.
    for k in [1, 3]:
        glyph(p.neon, faces[k], [0.3, 0.7, 0.04, 0.96], N, 0.12)
    return head


def _core_obelisk(p: Any) -> None:
    """Draw the central obelisk (MB-MONOLITH-ARRAY-02): the tallest, its rotor's collar on top."""
    _pylon(p, CORE_AT, 4.2, CORE_HOVER)
    centre = _xz(CORE_AT[0], CORE_AT[1])
    # A thin plinth of light under its foot: it hovers.
    p.neon.box(
        [CORE_FOOT[0] * 1.6, 0.4, CORE_FOOT[1] * 1.6],
        N,
        Placement(boss_point(CORE_AT[0], CORE_AT[1], CORE_HOVER - 0.5)),
    )
    head = _shaft(p, CORE_AT, [CORE_FOOT, CORE_HEAD], [CORE_HOVER, COLLAR_FOOT], 0)
    collar = chamfered(centre, COLLAR, 1.6)
    frustum(
        p.hull,
        [head, chamfered(centre, [COLLAR[0] - 1.2, COLLAR[1] - 1.2], 1.2)],
        [COLLAR_FOOT, COLLAR_FOOT + 0.6],
        STEEL,
    )
    frustum(
        p.hull,
        [collar, chamfered(centre, [COLLAR[0] - 0.8, COLLAR[1] - 0.8], 1.4)],
        [COLLAR_FOOT + 0.6, CORE_TOP],
        STEEL,
        BASALT,
    )
    p.neon.ring(
        COLLAR[0] * 0.98,
        0.5,
        8,
        N,
        Placement(boss_point(CORE_AT[0], CORE_AT[1], CORE_TOP - 2.6), math.pi / 8),
    )
    # The rotor's seat on the cap.
    p.hull.cylinder(
        4.6, 0.6, 8, PALE, Placement(boss_point(CORE_AT[0], CORE_AT[1], CORE_TOP - 0.05))
    )


def _sight(p: Any) -> None:
    """Draw the sight's plinth (MB-MONOLITH-ARRAY-03): a squat block before the central obelisk.

    Its turret stands on it (its mount, BOSS-58); a buttress ties it to the obelisk's pylon.
    """
    at = boss_point(SIGHT_AT[0], SIGHT_AT[1], PLATFORM_TOP - 0.2)
    centre = _xz(SIGHT_AT[0], SIGHT_AT[1])
    frustum(
        p.hull,
        [chamfered(centre, [5, 4.4], 1.4), chamfered(centre, [4, 3.6], 1.2)],
        [PLATFORM_TOP - 0.2, SIGHT_HEIGHT],
        STONE,
        STEEL,
    )
    p.neon.ring(4.5, 0.4, 8, N, Placement([at[0], SIGHT_HEIGHT - 1.6, at[2]], math.pi / 8))
    p.hull.box(
        [3, 2.2, 8],
        BASALT,
        Placement(boss_point(0, (SIGHT_AT[1] + CORE_AT[1]) / 2 - 1, PLATFORM_TOP - 0.2)),
    )


def _platform_top(p: Any) -> None:
    """Draw the platform (MB-MONOLITH-ARRAY-01): a low slab of stone and metal under the obelisks.

    Bevelled, a rim of light round its edge, a metal frame on its top, channels of light linking
    the obelisks' pylons (their field), vents at its back.
    """
    outline = _platform()
    p.hull.bevel_slab(
        outline, [0, PLATFORM_TOP - 1.6, PLATFORM_TOP], [2.4, 1], BASALT, None, [0.04, 0.042, 0.05]
    )
    neon_band(p.neon, outline, [PLATFORM_TOP - 1.8, PLATFORM_TOP - 1.2], [1.002, 1.002], N)
    for s in [-1, 1]:
        # A metal rail round its outer end.
        for rail in [[[46, -7], [51, 4]], [[51, 4], [47, 14]]]:
            a = _xz(s * rail[0][0], rail[0][1])
            b = _xz(s * rail[1][0], rail[1][1])
            length = math.hypot(b[0] - a[0], b[1] - a[1])
            p.hull.box(
                [1.6, 0.7, length],
                STEEL,
                Placement(
                    [(a[0] + b[0]) / 2, PLATFORM_TOP - 0.1, (a[1] + b[1]) / 2],
                    math.atan2(b[0] - a[0], b[1] - a[1]),
                ),
            )
        # The field's channels: from the core's pylon out to the side monolith's.
        y = (SIDE_AT[1] + CORE_AT[1]) / 2
        for dy in [-1.6, 1.6]:
            a = _xz(s * 6, y + dy)
            b = _xz(s * (SIDE_X - 4), y + dy)
            p.neon.box(
                [abs(b[0] - a[0]), 0.2, 0.5], N, Placement([(a[0] + b[0]) / 2, PLATFORM_TOP, a[1]])
            )
    # Vents across its back.
    for k in range(5):
        x = -10 + k * 5
        p.hull.box([3.2, 0.5, 2.6], STEEL, Placement(boss_point(x, 13.5, PLATFORM_TOP - 0.1)))
        decal(
            p.neon,
            [_xz(x - 1, 12.9), _xz(x + 1, 12.9), _xz(x + 1, 13.3), _xz(x - 1, 13.3)],
            PLATFORM_TOP + 0.45,
            N,
        )


def side_monolith(p: Any, at: Vec3) -> None:
    """Add a side monolith (MB-MONOLITH-ARRAY-03): a pointed obelisk on its pylon.

    Its laser's emitter set in a lit socket in its front face (its mount, BOSS-58).
    """
    x = -at[0]
    y = -at[2]
    _pylon(p, [x, y], 3.2, SIDE_HOVER)
    p.neon.box(
        [SIDE_FOOT[0] * 1.5, 0.4, SIDE_FOOT[1] * 1.5],
        N,
        Placement(boss_point(x, y, SIDE_HOVER - 0.5)),
    )
    head = _shaft(p, [x, y], [SIDE_FOOT, SIDE_HEAD], [SIDE_HOVER, SIDE_TOP], 1 if x > 0 else 2)
    centre = _xz(x, y)
    point = [
        [centre[0] + 0.3 * math.cos(k), centre[1] + 0.3 * math.sin(k)] for k in range(len(head))
    ]
    frustum(p.hull, [head, point], [SIDE_TOP, SIDE_TOP + POINT], STONE)
    p.neon.box([0.9, 0.9, 0.9], N, Placement(boss_point(x, y, SIDE_TOP + POINT - 0.4)))
    # The emitter's socket: a dark frame round the barrel, a bar of light over it.
    socket = boss_point(x, EMITTER_Y - 0.4, EMITTER_HEIGHT - 2.6)
    p.hull.box([5.6, 5.2, 2], BASALT, Placement(socket))
    p.neon.box([4.4, 0.4, 2.1], N, Placement([socket[0], EMITTER_HEIGHT + 2.7, socket[2]]))
    # The field's beams of light, from the central obelisk's flank to this one's.
    inner = SIDE_FOOT[0] - 1.2 if x > 0 else -(SIDE_FOOT[0] - 1.2)
    for h in [SIDE_HOVER + 3, SIDE_HOVER + 9]:
        a = _xz(x - inner, (y + CORE_AT[1]) / 2)
        b = _xz((CORE_FOOT[0] - 1.5) * (1 if x > 0 else -1), (y + CORE_AT[1]) / 2)
        p.neon.box([abs(b[0] - a[0]), 0.6, 0.6], N, Placement([(a[0] + b[0]) / 2, h, a[1]]))


def _draw_plinths(p: Any) -> None:
    """Draw the plinth plates (MB-MONOLITH-ARRAY-05): stone slabs either side of the sight.

    Each with a glyph of light along it; the lances lie folded under them.
    """
    for s in [-1, 1]:
        outline = [_xz(s * q[0], q[1]) for q in PLINTH_OUTLINE]
        p.hull.bevel_slab(
            outline,
            [PLINTH_HEIGHTS[0], PLINTH_HEIGHTS[1] - 1.2, PLINTH_HEIGHTS[1]],
            [0, 1],
            STONE,
            None,
            STEEL,
        )
        top = PLINTH_HEIGHTS[1] + 0.05
        decal(
            p.neon,
            [_xz(s * 16, -12), _xz(s * 30, -11), _xz(s * 30, -10.2), _xz(s * 16, -11.2)],
            top,
            N,
        )
        decal(
            p.neon,
            [_xz(s * 22, -10.6), _xz(s * 23, -10.6), _xz(s * 23, -4.5), _xz(s * 22, -4.5)],
            top,
            N,
        )


def build_monolith_array(scene: Any) -> Any:
    """MB-MONOLITH-ARRAY-01, MB-MONOLITH-ARRAY-04: the Monolith Array.

    Three dark obelisks hovering in a row over a stone platform, cyan glyphs cut into their faces;
    the side monoliths carry its lasers, the central one its crown rotor and, before it, its sight
    turret (their mounts, BOSS-58). Its plinth plates burst off for a pair of lances at its
    transformation (MB-MONOLITH-ARRAY-05).
    """

    def core(p: Any) -> None:
        _platform_top(p)
        _core_obelisk(p)
        _sight(p)

    return build_boss_model(
        MONOLITH_ARRAY,
        scene,
        N,
        {
            "core": core,
            "parts": {"monolith-left": side_monolith, "monolith-right": side_monolith},
            "armour": {"plinths": {"whole": _draw_plinths}},
        },
    )
