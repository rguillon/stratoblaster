# Copyright (c) 2026 Renaud Guillon
"""The Snow Owl's armour (MB-SNOW-OWL-07, D-254): its wing tips and its back plating.

Drawn as pieces of their own. The outer panel of each wing (`wingtips-right`, `wingtips-left`) is
the wing's slab beyond 30 px out, with its rime, its leading edge's neon, the pod's socket ring
and its lamp (no icicles hang from it: the frame it slides off lies just under its slab): the
engine slides it out. The back plating (`back`) is a shell of teal
plates with dark seams over the flattened back, snow on it, carrying the glands, the crystals, the
spine row, the lit stripes and the sensor's hood; it bursts into its slices. Logical pixels, nose
+Z, Y up.
"""

from game.view.bosses.mini_boss_greebles import lamps, seam
from game.view.bosses.mini_boss_shapes import SHADE, H
from game.view.bosses.world_2.snow_owl_parts import OWL_WHITE
from game.view.bosses.world_2.w2_organic import ICE_FLESH, crystals, gland, spine_row
from game.view.enemies.enemy_shapes import CANOPY_SIDES, SIDES
from render.geometry.organic import SHELL_SECTION
from render.geometry.solids import LoftOptions, Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import EnemyParts

type Outline = list[list[float]]
# __pragma__ ("noskip")


# Navigation lights on the tips: red to port (+X, the screen's left), green to starboard.
PORT_RED = [1, 0.1, 0.12]
STARBOARD_GREEN = [0.2, 1, 0.35]
# Where a wing splits into its inner part and its tip panel (px out from the centre line).
TIP_ROOT = 30.0
# The leading edge's neon of a tip, root to tip (one wing; mirrored for the other).
TIP_EDGE = [  # type: list[list[float]]
    [30, 7.97],
    [40, 3.8],
    [47, 0.4],
]
# The back plating (loft stations: z, half width, bottom, top) over the flattened back (its deck
# at 5.9), from a point on the tail to a point sunk in the head's rise; its bottom sunk 0.4 in the
# deck, so the frame's floor lies just over the deck.
SHELL = [  # type: list[list[float]]
    [-24.0, 2.0, 5.6, 6.4],
    [-20.0, 7.0, 5.5, 9.0],
    [-12.0, 11.0, 5.5, 11.8],
    [-2.0, 12.5, 5.5, 12.4],
    [6.0, 9.0, 5.5, 10.0],
    [8.5, 4.0, 5.6, 6.6],
]


def clip_x(outline: Outline, x0: float, side: float) -> Outline:
    """Return `outline` (XZ) clipped to the half plane `side * (x - x0) >= 0`."""
    result: Outline = []
    n = len(outline)
    for i in range(n):
        a = outline[i]
        b = outline[(i + 1) % n]
        da = side * (a[0] - x0)
        db = side * (b[0] - x0)
        if da >= 0:
            result.append(a)
        if (da >= 0) != (db >= 0):
            t = da / (da - db)
            result.append([x0, a[1] + (b[1] - a[1]) * t])
    return result


def draw_wing_slabs(p: EnemyParts, outline: Outline, rime: Outline) -> None:
    """Draw a piece of wing: its membrane slab on bone, the rimed teal flesh over it."""
    p.flesh.bevel_slab(
        outline, [-1.2, 0, 1.6], [0.8, 1.2], ICE_FLESH.membrane, None, ICE_FLESH.graphite
    )
    p.flesh.bevel_slab(rime, [1.5, 1.7, 2.1], [0, 0.5], ICE_FLESH.teal, None, ICE_FLESH.rime)


def draw_tip(p: EnemyParts, wing: Outline, rime: Outline, s: float) -> None:
    """Draw the tip panel of the wing on model side `s` (MB-SNOW-OWL-07): the moving piece.

    The wing's slabs beyond `TIP_ROOT`, its leading edge's neon, the pod's socket ring and its
    navigation lamp.
    """
    draw_wing_slabs(p, clip_x(wing, s * TIP_ROOT, s), clip_x(rime, s * TIP_ROOT, s))
    for i in range(len(TIP_EDGE) - 1):
        a = TIP_EDGE[i]
        b = TIP_EDGE[i + 1]
        seam(p.neon, [s * a[0], a[1]], [s * b[0], b[1]], [1.6, 0.8, 0.7], OWL_WHITE)
    p.hull.ring(8, 1, 8, H.panel, Placement([s * 38, 1.6, 2]))
    lamps(p.neon, [[s * 50.5, 0.4, -3]], 1.4, PORT_RED if s > 0 else STARBOARD_GREEN)


def _shell_paint(side: int, band: int) -> Any:
    """Snow on the shell's back, a dark seam on every other band of its flanks."""
    if side in CANOPY_SIDES:
        return ICE_FLESH.rime
    return ICE_FLESH.seam if band % 2 == 1 else None


def draw_shell(p: EnemyParts, first: int, last: int) -> None:
    """Draw the back plating from station `first` to station `last` of `SHELL`."""

    def paint(side: int, band: int) -> Any:
        return _shell_paint(side, band + first)

    p.flesh.loft(
        SHELL_SECTION, SHELL[first : last + 1], ICE_FLESH.teal, None, LoftOptions(False, paint)
    )


def draw_shell_gear(p: EnemyParts, first: int, last: int) -> None:
    """Draw what stands on the plating from station `first` to before station `last`.

    Each stands on the slice starting at its station: crystals on the tail's, the lit glands and
    stripes on the middle's, the sensor's hood on the nose's; the spine row runs down the whole.
    """
    for s in SIDES:
        if first <= 1 < last:
            crystals(p.flesh, [s * 5, 7.4, -20], 2.6)
        if first <= 2 < last:
            gland(p, [s * 7, 9.4, -10], 1.2, OWL_WHITE)
            p.neon.box([0.6, 0.4, 12], OWL_WHITE, Placement([s * 9.8, 7.4, -5], s * 0.05))
    if first <= 3 < last:
        p.hull.box([12, 0.4, 3], SHADE["edge"], Placement([0, 11.0, 2]))


def draw_plating(p: EnemyParts) -> None:
    """Draw the whole back plating as it lies at rest (MB-SNOW-OWL-07)."""
    last = len(SHELL) - 1
    draw_shell(p, 0, last)
    draw_shell_gear(p, 0, last)
    spine_row(p.flesh, [0, 10.6, 4], [0, 9.0, -18], 4, 2.6)


def _slice(k: int) -> Any:
    def draw(p: EnemyParts) -> None:
        draw_shell(p, k, k + 1)
        draw_shell_gear(p, k, k + 1)

    return draw


def plating_pieces() -> list[Any]:
    """Return the pieces the back plating bursts into: its slices, each with what stands on it."""
    return [_slice(k) for k in range(len(SHELL) - 1)]


def _tip(wing: Outline, rime: Outline, s: float) -> Any:
    def draw(p: EnemyParts) -> None:
        draw_tip(p, wing, rime, s)

    return draw


def owl_armour(wing: Outline, rime: Outline) -> Any:
    """Return the Snow Owl's armour drawings by region id.

    The tip panels (`wingtips-right` is the model's -X side: the config's +X is mirrored), moving
    pieces that burst into nothing, and the back plating with its slices.
    """
    return {
        "wingtips-right": {"whole": _tip(wing, rime, -1), "pieces": []},
        "wingtips-left": {"whole": _tip(wing, rime, 1), "pieces": []},
        "back": {"whole": draw_plating, "pieces": plating_pieces()},
    }
