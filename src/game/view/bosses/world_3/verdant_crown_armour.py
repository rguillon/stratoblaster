# Copyright (c) 2026 Renaud Guillon
"""FB-VERDANT-CROWN-12, FB-VERDANT-CROWN-13, 3-5: the Verdant Crown's armour (D-254).

The stone plating grafted on the beast's back over its flank decks and its aft deck, drawn as pieces
of their own lying on the deck (BOSS-42), the towers, moss and vines of the city standing on them:
the flanks burst off at its first transformation, the spine plating aft of the dome at its second.
Model space: logical pixels, nose +Z (down the screen), Y up towards the camera.
"""

from game.config.enemy_look import ENEMY_LOOK
from game.view.bosses.world_3.jungle_flesh import table
from game.view.bosses.world_3.verdant_crown_city import FLANKS, SPINE, draw_city
from game.view.bosses.world_3.verdant_crown_garden import DECK_TOP, JUNGLE
from game.view.enemies.enemy_shapes import SIDES

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import EnemyParts

# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
# The plating lies on the deck, sunk a little into it (its frame floor shows 0.6 px over the deck
# once it is gone), up to `PLATING_TOP`.
PLATING = [DECK_TOP - 0.3, DECK_TOP + 1.2]
PLATING_TOP = PLATING[1]
# The flank plating's plan (the +X side; model x, z): the side deck from the dome's rim out to the
# deck's edge, clear of the root generator ahead of it.
FLANK_PLAN = table([
    [34, -24],
    [58.5, -24],
    [61, 0],
    [55, 44],
    [51, 50],
    [46, 50],
    [46, 36],
    [34, 36],
])
# The spine plating's plan: the aft deck behind the dome, round the missile hatches' block, to the
# deck's tail.
SPINE_PLAN = table([[-32, -36], [32, -36], [32, -72], [24, -85], [-24, -85], [-32, -72]])


def _plating(p: EnemyParts, outline: list[Any]) -> None:
    """Add a plate of old stone lying on the deck over `outline`."""
    p.hull.slab(outline, PLATING, H.panel, None, JUNGLE["stone"])


def flank_plating(p: EnemyParts) -> None:
    """Draw the flank plating (FB-VERDANT-CROWN-12): the armour shed first, both sides.

    A plate over each side deck beside the dome, the towers, moss and vine of the city there
    standing on it.
    """
    for s in SIDES:
        _plating(p, [[s * point[0], point[1]] for point in FLANK_PLAN])
    draw_city(p, FLANKS, PLATING_TOP)


def spine_plating(p: EnemyParts) -> None:
    """Draw the spine plating (FB-VERDANT-CROWN-13): the armour shed second.

    A plate over the aft deck behind the dome, round the missile hatches' block, the towers and
    moss of the city there standing on it.
    """
    _plating(p, SPINE_PLAN)
    draw_city(p, SPINE, PLATING_TOP)
