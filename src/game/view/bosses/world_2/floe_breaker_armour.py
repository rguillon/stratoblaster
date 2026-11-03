# Copyright (c) 2026 Renaud Guillon
"""The Floe Breaker's front plating (MB-FLOE-BREAKER-07, D-254): the armour it sheds.

A rimed plate of teal flesh over the front deck either side of the bone ram, drawn as a piece of
its own in the `back` region's outlines; dark seams across it, a frosted metal plate grafted on
each and ice crystals grown through it. Logical pixels, nose +Z, Y up.
"""

from game.config.bosses.world_2.floe_breaker import FLOE_BREAKER
from game.view.bosses.boss_armour import model_outlines
from game.view.bosses.mini_boss_greebles import plate, rect, seam
from game.view.bosses.world_2.floe_breaker_frost import FROST
from game.view.bosses.world_2.w2_organic import ICE_FLESH, crystals
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from game.view.enemies.enemy_mesh import EnemyParts

# __pragma__ ("noskip")


# How far the plating rises over the deck it lies on.
PLATING_THICK = 3.0
# The dark seams across each plate, `[z, inner x, outer x]` (the plate narrows towards the nose).
SEAMS = [[14.0, 12.6, 20.4], [26.0, 10.3, 14.7]]


def draw_plating(p: EnemyParts, deck: float) -> None:
    """Draw the front plating lying on the `deck` (MB-FLOE-BREAKER-07).

    One plate in each outline of the `back` region, bevelled, rimed on top, `PLATING_THICK` over the
    deck; dark seams across it, a frosted metal plate grafted on it, ice crystals grown through it.
    """
    top = deck + PLATING_THICK
    for outline in model_outlines(FLOE_BREAKER.armour[0]):
        p.flesh.bevel_slab(
            outline, [deck, deck + 0.6, top], [0.4, 1.4], ICE_FLESH.teal, None, ICE_FLESH.rime
        )
    for s in SIDES:
        for line in SEAMS:
            seam(
                p.flesh,
                [s * line[1], line[0]],
                [s * line[2], line[0]],
                [top, 0.6, 0.3],
                ICE_FLESH.seam,
            )
        plate(p.hull, rect(8.0, 10.0), [top, 0.6], FROST.panel, Placement([s * 18.0, 0.0, 8.0]))
        crystals(p.flesh, [s * 15.0, top, 12.0 + s * 3.0], 3.5)
