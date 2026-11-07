# Copyright (c) 2026 Renaud Guillon
"""FB-FOLDING-CITADEL-05, FB-FOLDING-CITADEL-11: the Folding Citadel's panels and shed armour.

Logical pixels, nose +Z, Y up (towards the camera). Its four wall panels are moving pieces
(BOSS-45), each drawn folded up as it rests and swung open flat by the engine: a thick plated
slab, armour plates and lit fold lines on its outer face, ribs and lit creases on its inner face
(bared as it opens), the side panels' gun sponsons on their outer faces and their rack beds on
their inner faces. The front courtyard's plating and the keep's rotor hatch are shed regions.

A panel is drawn in its own frame: its hinge along local Z through the origin, the panel lying out
along local -X (`PANEL_LENGTH`) between local Y `-PANEL_THICK` (its outer face) and 0 (its inner
face), then rolled up `FOLD` degrees and turned to its side of the box.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.folding_citadel import (
    BASE,
    COURT,
    COURT_TOP,
    FOLD,
    HINGE_H,
    KEEP_TOP,
    LEAN,
    PANEL_LENGTH,
    PANEL_THICK,
    RACK_AT,
    ROTOR_AT,
    WALL_AT,
    WALL_GUN_HEIGHT,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.world_1_organic_kit import M, polygon
from render.geometry.organic import tendril
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["folding-citadel"]
DEG = math.pi / 180
ROLL = -FOLD * DEG
# Each panel's side: its turn about the vertical and its hinge's middle (model space).
SIDES: dict[str, Any] = {
    "right": [0.0, [-BASE, HINGE_H, 0]],
    "left": [math.pi, [BASE, HINGE_H, 0]],
    "front": [math.pi / 2, [0, HINGE_H, BASE]],
    "back": [-math.pi / 2, [0, HINGE_H, -BASE]],
}
# The outer face's armour plates, `[x0, x1]` along the panel (local X, from its hinge out).
PLATES = [[-1, -10.5], [-11.5, -21], [-22, -31.2]]
# The inner face's ribs across it (local X).
RIBS = [-7, -15, -24, -30]
T = PANEL_THICK


def half_width(x: float) -> float:
    """Return the panel's half width `x` px out from its hinge (local X, negative)."""
    return float(BASE + x * math.cos(LEAN * DEG))


def _rotate(p: Vec3, yaw: float) -> Vec3:
    """Return local `p` rolled up by the fold, then turned by `yaw` (as `Placement` does)."""
    x2 = p[0] * math.cos(ROLL) - p[1] * math.sin(ROLL)
    y2 = p[0] * math.sin(ROLL) + p[1] * math.cos(ROLL)
    return [
        x2 * math.cos(yaw) + p[2] * math.sin(yaw),
        y2,
        -x2 * math.sin(yaw) + p[2] * math.cos(yaw),
    ]


def panel_point(side: str, p: Vec3) -> Vec3:
    """Return the model point of the local point `p` of the panel on `side`, as it rests."""
    yaw = SIDES[side][0]
    o = SIDES[side][1]
    r = _rotate(p, yaw)
    return [o[0] + r[0], o[1] + r[1], o[2] + r[2]]


def panel_place(side: str, p: Vec3) -> Placement:
    """Return the placement of a solid drawn in the panel's frame with its origin at local `p`."""
    return Placement(panel_point(side, p), SIDES[side][0], 0, ROLL)


def _trapezoid(x0: float, x1: float, inset: float) -> list[list[float]]:
    """Return the panel's outline between local X `x0` and `x1`, `inset` in from its sides."""
    a = half_width(x0) - inset
    b = half_width(x1) - inset
    return [[x0, -a], [x0, a], [x1, b], [x1, -b]]


def _strip(a: list[float], b: list[float], width: float) -> list[list[float]]:
    """Return a thin outline `width` wide from local XZ `a` to `b`."""
    dx = b[0] - a[0]
    dz = b[1] - a[1]
    n = math.sqrt(dx * dx + dz * dz)
    ox = -dz / n * width / 2
    oz = dx / n * width / 2
    return [
        [a[0] + ox, a[1] + oz],
        [b[0] + ox, b[1] + oz],
        [b[0] - ox, b[1] - oz],
        [a[0] - ox, a[1] - oz],
    ]


def _slab(p: Any, side: str, outline: list[Any], heights: list[float], color: Any) -> None:
    """Add a flat slab of `outline` (local XZ) between local Y `heights` to a panel."""
    p.slab(outline, heights, color, panel_place(side, [0, 0, 0]))


def _draw_panel(p: Any, side: str) -> None:
    """Draw the wall panel on `side` (FB-FOLDING-CITADEL-05) as it rests, folded up.

    A thick plated slab; on its outer face three armour plates and lit fold lines from its hinge's
    ends to its tip (the origami creases); on its inner face ribs across it and two lit creases.
    """
    place = panel_place(side, [0, 0, 0])
    p.hull.bevel_slab(
        _trapezoid(0, -PANEL_LENGTH, 0), [-T, -T / 2, 0], [0.7, 0.7], M.dark, place, M.base
    )
    for k in range(len(PLATES)):
        band = PLATES[k]
        p.hull.bevel_slab(
            _trapezoid(band[0], band[1], 2.2),
            [-T - 1.3, -T - 0.5, -T + 0.2],
            [0.9, 0],
            M.panel if k % 2 == 0 else M.base,
            place,
        )
    tip = [-PANEL_LENGTH + 1.2, 0]
    for s in [-1, 1]:
        corner = [-0.8, s * (BASE - 4)]
        _slab(p.neon, side, _strip(corner, tip, 0.7), [-T - 1.7, -T - 1.2], N)
        _slab(p.neon, side, _strip([-1.5, s * 9], tip, 0.5), [0, 0.45], N)
    _slab(p.neon, side, _strip([-0.8, 0], [-PANEL_LENGTH + 4, 0], 0.6), [-T - 1.7, -T - 1.2], N)
    # The seams along its sides, where it meets its neighbours folded: a dark lip, a lit line.
    for s in [-1, 1]:
        root = [-0.6, s * (half_width(-0.6) - 0.9)]
        end = [-PANEL_LENGTH + 0.6, s * (half_width(-PANEL_LENGTH + 0.6) - 0.9)]
        p.bare.slab(_strip(root, end, 1.6), [-T - 1.1, -T + 0.4], M.base, place)
        _slab(p.neon, side, _strip(root, end, 0.4), [-T - 1.4, -T - 1], N)
    for x in RIBS:
        hw = half_width(x) - 1.5
        p.bare.slab(_strip([x, -hw], [x, hw], 1.4), [0, 1.1], M.panel, place)
    # The rails along its inner face, and dark recessed bays between its ribs.
    for z in [-13, 13]:
        p.bare.slab(_strip([-1.5, z], [-PANEL_LENGTH + 1.5, z], 1.6), [0, 1.5], M.panel, place)
    for k in range(len(RIBS) - 1):
        x0 = RIBS[k] - 1.2
        x1 = RIBS[k + 1] + 1.2
        for z in [-1, 1]:
            a = z * 15
            b = z * (half_width(x1) - 3)
            p.bare.slab([[x0, a], [x0, b], [x1, b], [x1, a]], [0, 0.25], M.dark, place)
    # The tip's lip: a lit edge along its outer end.
    hw = half_width(-PANEL_LENGTH) - 1
    _slab(
        p.neon,
        side,
        _strip([-PANEL_LENGTH + 0.4, -hw], [-PANEL_LENGTH + 0.4, hw], 0.6),
        [-T + 0.2, -0.2],
        N,
    )


def _draw_rack_bed(p: Any, side: str) -> None:
    """Draw a side panel's rack bed on its inner face: a dark plate, lit studs at its corners."""
    x = BASE - RACK_AT[0]
    place = panel_place(side, [0, 0, 0])
    p.bare.slab([[x - 7, -7], [x - 7, 7], [x + 7, 7], [x + 7, -7]], [0, 0.7], M.dark, place, M.base)
    for dx in [-6, 6]:
        for dz in [-6, 6]:
            p.neon.box([1.2, 0.5, 1.2], N, panel_place(side, [x + dx, 0.6, dz]))


def _draw_sponson(p: Any, side: str, s: float) -> None:
    """Draw a side panel's gun sponson (FB-FOLDING-CITADEL-03): a level platform on its face.

    An octagonal platform jutting from the panel's outer face, braced to it by two struts; the
    wall gun stands on it. `s`: 1 on the config's right (+X), -1 on its left.
    """
    at = boss_point(s * WALL_AT[0], WALL_AT[1], 0)
    top = WALL_GUN_HEIGHT - 2.6
    p.hull.bevel_slab(
        polygon(8, 6.6), [top - 2.6, top - 1, top], [1.2, 0.4], M.panel, Placement(at, math.pi / 8)
    )
    for dz in [-3.5, 3.5]:
        foot = panel_point(side, [-4, -T - 1, dz])
        head = [at[0] - s * 3, top - 2.4, at[2] + dz]
        tendril(p.hull, [foot, head], [1.1, 1.1], 5, M.base)


def panel(side: str) -> Any:
    """Return the drawing of the panel on `side` (`right`, `left`, `front`, `back`)."""

    def draw(p: Any) -> None:
        _draw_panel(p, side)
        if side == "right":
            _draw_rack_bed(p, side)
            _draw_sponson(p, side, 1)
        elif side == "left":
            _draw_rack_bed(p, side)
            _draw_sponson(p, side, -1)

    return draw


def draw_court(p: Any) -> None:
    """Draw the front courtyard's plating (FB-FOLDING-CITADEL-11), shed as it transforms again.

    Four heavy plates across it with lit seams between them, vents along its back.
    """
    width = (COURT[1] - COURT[0]) / 4
    for k in range(4):
        x0 = COURT[0] + width * k + 0.4
        x1 = x0 + width - 0.8
        outline = [
            [-x0, -COURT[2] - 0.4],
            [-x1, -COURT[2] - 0.4],
            [-x1, -COURT[3] + 0.4],
            [-x0, -COURT[3] + 0.4],
        ]
        p.hull.bevel_slab(
            outline,
            [HINGE_H, COURT_TOP - 1, COURT_TOP],
            [0, 0.8],
            M.panel if k % 2 == 0 else M.base,
        )
    for k in range(1, 4):
        x = COURT[0] + width * k
        p.neon.box(
            [0.5, COURT_TOP - HINGE_H - 0.6, COURT[3] - COURT[2] - 3],
            N,
            Placement(boss_point(x, (COURT[2] + COURT[3]) / 2, HINGE_H)),
        )
    for k in range(5):
        x = COURT[0] + 8 + k * (COURT[1] - COURT[0] - 16) / 4
        p.bare.box([5, 0.6, 2.4], M.dark, Placement(boss_point(x, COURT[3] - 3, COURT_TOP)))


def draw_hatch(p: Any) -> None:
    """Draw the hatch over the keep's rotor (BOSS-58): an octagonal cap, a lit seam round it."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.bevel_slab(
        polygon(8, 6.8), [KEEP_TOP, KEEP_TOP, KEEP_TOP + 1.6], [0, 0.8], M.panel, Placement(at)
    )
    p.hull.bevel_slab(
        polygon(8, 4.4),
        [KEEP_TOP + 1.6, KEEP_TOP + 1.6, KEEP_TOP + 2.6],
        [0, 0.6],
        M.base,
        Placement(at),
    )
    p.neon.ring(6.6, 0.25, 8, N, Placement([at[0], KEEP_TOP + 1.2, at[2]], math.pi / 8))


def draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.ring(6.4, 1.2, 16, M.base, Placement([at[0], KEEP_TOP - 0.4, at[2]]))
    p.neon.ring(6.4, 0.3, 16, N, Placement([at[0], KEEP_TOP + 0.6, at[2]]))


def citadel_armour() -> Any:
    """Return the Folding Citadel's armour drawings by region id (`drawing.armour`, D-254)."""
    return {
        "panel-right": {"whole": panel("right")},
        "panel-left": {"whole": panel("left")},
        "panel-front": {"whole": panel("front")},
        "panel-back": {"whole": panel("back")},
        "court": {"whole": draw_court},
        "rotor-hatch": {"whole": draw_hatch, "frame": draw_hatch_frame},
    }
