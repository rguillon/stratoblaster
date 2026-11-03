# Copyright (c) 2026 Renaud Guillon
"""FB-DAM-BREAKER-11, FB-DAM-BREAKER-12, 3-4: the Dam Breaker's armour (D-254).

The rusty plating grafted on the beast's back over its flank decks and its bow's wing decks, drawn
as pieces of their own lying on the deck (BOSS-42), with the deck's seams, rust and moss on them:
the flanks burst off at its first transformation, the wings at its second. Logical pixels, nose +Z,
Y up (towards the camera).
"""

from game.view.bosses.mini_boss_greebles import seam
from game.view.bosses.mini_boss_shapes import SHADE, H
from game.view.bosses.world_3.dam_breaker_parts import DECK_Y, RUST, moss
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import EnemyParts

# __pragma__ ("noskip")


# The plating lies on the deck, sunk a little into it (its frame floor shows 0.6 px over the deck
# once it is gone), up to `PLATING_TOP`.
PLATING = [DECK_Y - 0.3, DECK_Y + 1.2]
PLATING_TOP = PLATING[1]
# The flank plating's plan (the +X side; model x, z): the side deck from the sluice mounts back to
# the stern, to the deck's edge.
FLANK = [[30, -7], [56, -7], [56, -52], [50.5, -65], [35.5, -70], [30, -70]]
# The wing plating's plan (the +X side): the bow's deck beside the armour plate and the hangar.
WING = [[14, 21], [56, 21], [56, 30], [52.3, 47], [39, 62], [21.5, 70], [14, 71]]


def _sided(outline: list[Any], s: float) -> list[Any]:
    """Return `outline` on the side `s` of the centre line."""
    return [[s * point[0], point[1]] for point in outline]


def _plating(p: EnemyParts, outline: list[Any]) -> None:
    """Add a plate of rusty metal lying on the deck over `outline`."""
    p.hull.slab(outline, PLATING, H.base, None, SHADE["patch"])


def flank_plating(p: EnemyParts) -> None:
    """Draw the flank plating (FB-DAM-BREAKER-11): the armour shed first, both sides.

    A plate over each side deck from the sluice mounts back to the stern, the deck's cross seams
    running on over it, a rusty patch and moss on it.
    """
    hull = p.hull
    for s in SIDES:
        _plating(p, _sided(FLANK, s))
        for z in [-40, -20]:
            seam(hull, [s * 31, z], [s * 54, z], [PLATING_TOP, 0.8, 0.4], H.dark)
        hull.box([14, 0.4, 12], RUST, Placement([s * 40, PLATING_TOP, -46 + s * 6]))
    moss(hull, [[-38, PLATING_TOP, -30], [44, PLATING_TOP, -58]])


def wing_plating(p: EnemyParts) -> None:
    """Draw the wing plating (FB-DAM-BREAKER-12): the armour shed second, both sides.

    A plate over each side of the bow's deck, from the armour plate out to the deck's edge, the bow
    seam running on over it, moss on it.
    """
    hull = p.hull
    for s in SIDES:
        _plating(p, _sided(WING, s))
        seam(hull, [s * 15, 34], [s * 52, 34], [PLATING_TOP, 0.8, 0.4], H.dark)
    moss(hull, [[24, PLATING_TOP, 50], [-30, PLATING_TOP, 46]])
