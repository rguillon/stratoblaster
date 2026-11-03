# Copyright (c) 2026 Renaud Guillon
"""The Fjord Lynx's head plating (MB-FJORD-LYNX-06, D-254): the armour it sheds.

The crown of its head, a loft of graphite flesh with dark seams lying on the flattened head, the
tufted antennas (its ears) on it, and a lobe of flesh on the deck either side of the chin cannon,
where the ring emitters lie folded. Drawn as pieces of their own in the `back` region: the whole
plating at rest, and the pieces it bursts into (the crown in three slices, each ear, each lobe).
Logical pixels, nose +Z, Y up.
"""

import math

from game.view.bosses.mini_boss_shapes import H, offset
from game.view.bosses.world_2.fjord_lynx_parts import CYAN, WHITE_NEON
from game.view.bosses.world_2.w2_organic import ICE_FLESH
from game.view.enemies.enemy_shapes import FIGHTER_SECTION, SIDES, canopy_paint
from render.geometry.solids import LoftOptions, Placement, place_at

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import EnemyParts

type Vec3 = list[float]
# __pragma__ ("noskip")


# The crown over the flattened head (loft stations: z, half width, bottom, top): its back sunk in
# the head's slope, its nose a point just over the deck.
CROWN = [  # type: list[list[float]]
    [3.0, 10.6, 7.5, 11.6],
    [10.0, 10.0, 7.0, 12.5],
    [20.0, 8.0, 6.5, 9.5],
    [26.0, 0.0, 5.5, 5.5],
]
# The crown's bands painted as seams.
CROWN_SEAMS = [0, 1]
# The right lobe on the deck beside the chin cannon (mirrored on the left), from the deck up.
LOBE = [  # type: list[list[float]]
    [5.5, 24.0],
    [10.0, 24.0],
    [10.0, 34.0],
    [6.5, 40.0],
    [5.5, 40.0],
]
LOBE_HEIGHTS = [5.0, 5.4, 6.0]


def tip(length: float, place: Placement) -> Vec3:
    """Return the point `length` along the +Y axis of a solid placed by `place` (its tip)."""
    at: Vec3 = place.at if place.at is not None else [0.0, 0.0, 0.0]
    y1 = length * math.cos(place.pitch)
    z1 = length * math.sin(place.pitch)
    return offset(at, -y1 * math.sin(place.roll), y1 * math.cos(place.roll), z1)


def draw_ear(p: EnemyParts, s: float) -> None:
    """Draw the tufted antenna on side `s` of the crown: an ear, a whip with a light on its tip."""
    ear = Placement([s * 6.0, 9.5, 14.0], 0.0, -0.25, -s * 0.35)
    p.flesh.cylinder(3.4, 8, 3, ICE_FLESH.sinew, Placement(ear.at, s * 0.5, ear.pitch, ear.roll), 0)
    top = tip(7.0, ear)
    whip = Placement(top, 0.0, -0.55, -s * 0.5)
    p.hull.cylinder(0.4, 9, 4, H.dark, whip, 0.25)
    end = tip(9.0, whip)
    p.neon.lathe([[0.0, 0.0], [1.0, 1.2], [0.0, 3.4]], 4, WHITE_NEON, place_at(whip, end))
    p.neon.box(
        [0.6, 0.4, 3.0],
        CYAN,
        Placement(offset(ear.at, s * 1.2, 3.4, 0.6), 0.0, 0.0, -s * 0.35),
    )


def draw_crown(p: EnemyParts, first: int, last: int) -> None:
    """Draw the crown from station `first` to station `last` of `CROWN`, its seams painted."""

    def paint(side: int, band: int) -> Any:
        return canopy_paint(CROWN_SEAMS, ICE_FLESH.seam)(side, band + first)

    p.flesh.loft(
        FIGHTER_SECTION,
        CROWN[first : last + 1],
        ICE_FLESH.graphite,
        None,
        LoftOptions(False, paint),
    )


def draw_lobe(p: EnemyParts, s: float) -> None:
    """Draw the lobe of rimed graphite flesh on the deck on side `s` of the chin cannon."""
    lobe = [[s * q[0], q[1]] for q in LOBE]
    p.flesh.bevel_slab(lobe, LOBE_HEIGHTS, [0.3, 0.8], ICE_FLESH.graphite, None, ICE_FLESH.rime)


def draw_plating(p: EnemyParts) -> None:
    """Draw the whole head plating as it lies at rest (MB-FJORD-LYNX-06)."""
    draw_crown(p, 0, len(CROWN) - 1)
    for s in SIDES:
        draw_ear(p, s)
        draw_lobe(p, s)


def _slice(k: int) -> Any:
    def draw(p: EnemyParts) -> None:
        draw_crown(p, k, k + 1)

    return draw


def _ear(s: float) -> Any:
    def draw(p: EnemyParts) -> None:
        draw_ear(p, s)

    return draw


def _lobe(s: float) -> Any:
    def draw(p: EnemyParts) -> None:
        draw_lobe(p, s)

    return draw


def plating_pieces() -> list[Any]:
    """Return the pieces the head plating bursts into: the crown's slices, the ears, the lobes."""
    pieces: list[Any] = [_slice(k) for k in range(len(CROWN) - 1)]
    for s in SIDES:
        pieces.append(_ear(s))
        pieces.append(_lobe(s))
    return pieces
