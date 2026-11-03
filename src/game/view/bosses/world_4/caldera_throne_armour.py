# Copyright (c) 2026 Renaud Guillon
"""FB-CALDERA-THRONE-14, FB-CALDERA-THRONE-16, 4-5: the Caldera Throne's armour (D-254).

Drawn as pieces of their own, lying on the core as the boss rests (BOSS-42): the flank plates
(`flanks`), armour on the deck's sides out to its edge, shed at its first transformation; and the
spine plating (`spine`), the keep's upper works (its two upper tiers and the throne tower) with the
inner smokestacks, shed at its second. The lowest tier of the keep, the deck and the prow are the
core's. Logical pixels, nose +Z, Y up; +X is the screen's left, so a config outline (x, y) is drawn
at (-x, -y).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.boss_armour import plate_pieces
from game.view.bosses.final_boss_greebles import grille, plate, rect, studs
from game.view.bosses.final_boss_mechanism import conduit, glow_line
from game.view.bosses.mini_boss_shapes import H
from game.view.bosses.world_4.caldera_throne_keep import (
    STACKS,
    TIERS,
    draw_stack,
    draw_tier,
    draw_tower,
    octagon,
)
from game.view.bosses.world_4.caldera_throne_parts import (
    CRIMSON,
    DECK_TOP,
    GOLD,
    HEAT,
)
from game.view.bosses.world_4.living_forge import glands, magma_vein
from game.view.enemies.enemy_shapes import SIDES, flip_x
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type OutlinePoint = list[float]
type Vec3 = list[float]
# __pragma__ ("noskip")


# The flank plates lie on the deck, `PLATE` thick: their top is where their dressing stands.
PLATE = 1.5
TOP = DECK_TOP + PLATE
# A flank plate (the +X one; the other is its mirror): on the deck's top face from x 34 out to
# the face's edge, beside the bastion. Its config outline is this one, Z reversed.
FLANK: list[OutlinePoint] = [
    [34, -15],
    [62.6, -15],
    [61, 8],
    [55, 34],
    [46, 51],
    [34, 51],
]
# The flank's armour plate on it: centre, size, turn.
FLANK_PLATE = [48.0, 14.0, 12.0, 20.0, -0.25]
# The spine's share of the piece budget: plates cracked from the keep's middle tier.
MIDDLE_TIER = 1


def plating_pieces(outlines: list[list[OutlinePoint]], heights: list[float]) -> list[Any]:
    """Return the pieces a plating over `outlines` bursts into: plates cracked between `heights`.

    Its share of the boss's piece budget, two regions sharing it.
    """
    most = math.floor(BOSS_LOOK.armour.bossChunks / 2)
    return [piece[0] for piece in plate_pieces(outlines, heights, H.panel, most)]


def draw_flanks(p: Any) -> None:
    """Draw the flank plates (FB-CALDERA-THRONE-14), both sides.

    Iron plates on the deck beside the bastions; on each an armour plate, a molten seam, a grille,
    a row of gold lamps, a gland and the magma vein's forward run. The gun decks lie folded under
    them.
    """
    hull = p.hull
    neon = p.neon
    for s in SIDES:
        outline = FLANK if s > 0 else flip_x(FLANK)
        hull.bevel_slab(outline, [DECK_TOP, DECK_TOP + 0.5, TOP], [0, 1], H.base, None, H.panel)
        item = FLANK_PLATE
        plate(
            hull, rect([s * item[0], item[1]], [item[2], item[3]], s * item[4]), TOP, H.panel, 0.8
        )
        glow_line(neon, [[s * 40, 30], [s * 56, 6]], TOP - 0.3, HEAT["molten"])
        grille(hull, [s * 44, 40], [8, 10], [3, TOP + 0.05], s * 0.4)
        studs(neon, [[s * 50, 46], [s * 60, 20]], [5, 1.6], TOP + 0.06, GOLD)
        glands(p, [[s * 50, TOP - 0.5, -6]], 2.6, CRIMSON)
        magma_vein(p, [[s * 41, TOP + 0.3, -13], [s * 40, TOP + 0.3, 30]], 1.6)


def draw_spine(p: Any) -> None:
    """Draw the spine plating (FB-CALDERA-THRONE-16): the keep's upper works.

    The two upper tiers on the lowest one, the throne tower with its gold crown and charge light
    (the core's rings leave from the crown's height), the gold plaque on the middle tier, the two
    inner smokestacks with their conduits from the keep. The lances and the rack lie folded under
    it, on the deck.
    """
    for i in range(1, len(TIERS)):
        draw_tier(p, i)
    draw_tower(p)
    p.neon.box(
        [10, 2.4, 0.5],
        GOLD,
        Placement([0, 22, TIERS[1][0] * math.cos(math.pi / 8) + 0.3]),
    )
    for s in SIDES:
        draw_stack(p, s, STACKS[0])
        conduit(p.flesh, [s * 18, DECK_TOP + 3, -36], [s * 24, DECK_TOP + 3, -68], [1.6, 3])


# The regions' drawings (`drawing.armour`): the plates, and the pieces they burst into.
CALDERA_THRONE_ARMOUR = {
    "flanks": {
        "whole": draw_flanks,
        "pieces": plating_pieces([FLANK, flip_x(FLANK)], [DECK_TOP, TOP]),
    },
    "spine": {
        "whole": draw_spine,
        "pieces": plating_pieces(
            [octagon(TIERS[MIDDLE_TIER][0], [0, 0])],
            [TIERS[MIDDLE_TIER][1], TIERS[MIDDLE_TIER][1] + 2.5],
        ),
    },
}
