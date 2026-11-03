# Copyright (c) 2026 Renaud Guillon
"""The Avalanche's flank armour (MB-AVALANCHE-07, D-254): the two flanks of its ridged shell.

The shell over its back is drawn in two kinds of piece: a narrow dorsal ridge on the core, and the
shell's flanks either side of it, teal plates with dark seams from the deck up to the ridge's
shoulder, drawn here as the `flanks` region's armour, with the lit glands and ice crystals on them.
They burst into four slices a side. Logical pixels, nose +Z, Y up.
"""

from game.view.bosses.world_2.avalanche_arms import AVALANCHE_YELLOW
from game.view.bosses.world_2.w2_organic import ICE_FLESH, crystals, gland
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.organic import SegmentedBody, segment_stations
from render.geometry.solids import LoftOptions

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import EnemyParts

# __pragma__ ("noskip")


# The shell's body: the ridge is `RIDGE_WIDTH` of its width, the flanks its outer part.
SHELL_WIDTH = 21.0
RIDGE_WIDTH = 12.0
# The shell's loft stations (a seam at every other band, as `carapace` draws them).
STATIONS = segment_stations(SegmentedBody(-36.0, 6.0, 4, SHELL_WIDTH, 4.0, 13.0, 0.12))
# The right flank's section (shares of the shell's half width and height, counter-clockwise seen
# from the nose): the shell's outer slope from just under the deck up to the ridge's shoulder, its
# inner edge sunk in the ridge. The left flank is its mirror image.
FLANK_SECTION = [  # type: list[list[float]]
    [0.956, 0.27],
    [0.75, 0.6],
    [0.32, 0.78],
    [0.3, 0.5],
    [0.5, 0.27],
]
# The slices a flank bursts into: pairs of bands (first station, last station).
SLICES = [[0, 2], [2, 4], [4, 6], [6, 8]]


def flank_section(s: float) -> list[list[float]]:
    """Return the section of the flank on model side `s` (+X: the screen's left)."""
    if s > 0:
        return FLANK_SECTION
    n = len(FLANK_SECTION)
    return [[-FLANK_SECTION[n - 1 - k][0], FLANK_SECTION[n - 1 - k][1]] for k in range(n)]


def _seam_paint(_side: int, band: int) -> Any:
    """Return the dark seam colour on every other band of the shell (None elsewhere)."""
    return ICE_FLESH.seam if band % 2 == 1 else None


def draw_flank(p: EnemyParts, s: float, first: int, last: int) -> None:
    """Draw the flank on side `s` from station `first` to station `last` of `STATIONS`."""

    def paint(side: int, band: int) -> Any:
        return _seam_paint(side, band + first)

    p.flesh.loft(
        flank_section(s),
        STATIONS[first : last + 1],
        ICE_FLESH.teal,
        None,
        LoftOptions(False, paint),
    )


def draw_flank_gear(p: EnemyParts, s: float, first: int, last: int) -> None:
    """Draw what grows on the flank on side `s` between stations `first` and `last`.

    Ice crystals on its tail slice, a lit gland at its foot near the nose.
    """
    if first <= 2 < last:
        crystals(p.flesh, [s * 11.0, 9.0, -28.0], 4)
    if first <= 6 < last:
        gland(p, [s * 15.0, 7.2, -6.0], 1.5, AVALANCHE_YELLOW)


def draw_flanks(p: EnemyParts) -> None:
    """Draw both flanks whole, as they lie on the deck at rest (MB-AVALANCHE-07)."""
    last = len(STATIONS) - 1
    for s in SIDES:
        draw_flank(p, s, 0, last)
        draw_flank_gear(p, s, 0, last)


def _slice(s: float, first: int, last: int) -> Any:
    def draw(p: EnemyParts) -> None:
        draw_flank(p, s, first, last)
        draw_flank_gear(p, s, first, last)

    return draw


def flank_pieces() -> list[Any]:
    """Return the pieces the flanks burst into: four slices a side, with what grows on them."""
    pieces: list[Any] = []
    for s in SIDES:
        pieces.extend([_slice(s, bounds[0], bounds[1]) for bounds in SLICES])
    return pieces
