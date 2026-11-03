# Copyright (c) 2026 Renaud Guillon
"""The Ice Queen's rear plating (MB-ICE-QUEEN-07, D-254): the armour it sheds.

A shell of graphite plates with dark seams, snow on its ridge, lying over the flattened rear of the
fuselage and the engine sacs either side, from the tail to the spire's gland; the lit glands on it.
Drawn as a piece of its own in the `back` region; it bursts into its slices. The tail's crystal fins
are rooted in the deck and grow through it. Logical pixels, nose +Z, Y up.
"""

from game.view.bosses.world_2.ice_queen_shards import VIOLET
from game.view.bosses.world_2.w2_organic import ICE_FLESH, gland
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.organic import SHELL_SECTION
from render.geometry.solids import LoftOptions

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import EnemyParts

# __pragma__ ("noskip")


# The plating (loft stations: z, half width, bottom, top) over the rear deck (at 5.5) and the
# engine sacs (their tops at 5.6), from a point on the tail to a point sunk in the body's rise
# before the spire; its bottom sunk 0.5 in the deck, so the frame's floor lies just over it.
SHELL = [  # type: list[list[float]]
    [-57.0, 2.0, 5.0, 5.6],
    [-50.0, 12.0, 5.0, 7.0],
    [-44.0, 16.0, 5.0, 8.0],
    [-26.0, 16.5, 5.0, 9.6],
    [-14.0, 12.5, 5.0, 10.0],
    [-6.0, 1.5, 5.3, 6.5],
]
# The shell's sides along its ridge, snowed over.
RIDGE = [3, 4]
# The station whose slice carries the glands.
GLAND_STATION = 2


def _shell_paint(side: int, band: int) -> Any:
    """Return the plating's paint: rime on its ridge, a dark seam on every other band."""
    if side in RIDGE:
        return ICE_FLESH.rime
    return ICE_FLESH.seam if band % 2 == 1 else None


def draw_shell(p: EnemyParts, first: int, last: int) -> None:
    """Draw the plating from station `first` to station `last` of `SHELL`."""

    def paint(side: int, band: int) -> Any:
        return _shell_paint(side, band + first)

    p.flesh.loft(
        SHELL_SECTION,
        SHELL[first : last + 1],
        ICE_FLESH.graphite,
        None,
        LoftOptions(False, paint),
    )


def draw_shell_gear(p: EnemyParts, first: int, last: int) -> None:
    """Draw the lit glands, on the slice from `GLAND_STATION` when it lies in `first..last`."""
    if first <= GLAND_STATION < last:
        for s in SIDES:
            gland(p, [s * 5.0, 9.4, -30.0], 1.1, VIOLET)


def draw_plating(p: EnemyParts) -> None:
    """Draw the whole rear plating as it lies at rest (MB-ICE-QUEEN-07)."""
    last = len(SHELL) - 1
    draw_shell(p, 0, last)
    draw_shell_gear(p, 0, last)


def _slice(k: int) -> Any:
    def draw(p: EnemyParts) -> None:
        draw_shell(p, k, k + 1)
        draw_shell_gear(p, k, k + 1)

    return draw


def plating_pieces() -> list[Any]:
    """Return the pieces the rear plating bursts into: its slices, the glands on theirs."""
    return [_slice(k) for k in range(len(SHELL) - 1)]
