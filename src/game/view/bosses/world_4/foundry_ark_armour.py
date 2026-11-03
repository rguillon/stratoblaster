# Copyright (c) 2026 Renaud Guillon
"""FB-FOUNDRY-ARK-16, FB-FOUNDRY-ARK-18, 4-4: the Foundry Ark's armour (D-254).

Drawn as pieces of their own, lying on the deck as the boss rests (BOSS-42): the fore flank plates
(`flanks`), shed at its first transformation; the aft wing plates (`wings`) and the furnace's stack
on its crown plate (`spine`), shed at its second. The plates are iron plating 1.5 px thick on the
flesh deck (its top at `DECK_TOP`), carrying the yard's dressing that stood there: each bursts into
plates cracked from its outline at its own height. Logical pixels, nose +Z, Y up; +X is the
screen's left, so a config outline (x, y) is drawn at (-x, -y).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.boss_armour import plate_pieces
from game.view.bosses.final_boss_greebles import hazard
from game.view.bosses.mini_boss_greebles import seam, vent
from game.view.bosses.mini_boss_shapes import WHITE, H
from game.view.bosses.overlord_city import box2d
from game.view.bosses.world_4.foundry_ark_parts import (
    ARK_ORANGE,
    DECK_TOP,
    MOLTEN,
    SOOT,
)
from game.view.bosses.world_4.foundry_ark_yard import shed
from game.view.bosses.world_4.living_forge import SKIN, glands, magma_vein
from game.view.enemies.enemy_shapes import SIDES, decal, flip_x
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type OutlinePoint = list[float]
type Vec3 = list[float]
# __pragma__ ("noskip")


# The plates lie on the deck, `PLATE` thick: their top is where their dressing stands.
PLATE = 1.5
TOP = DECK_TOP + PLATE
# A fore flank plate (the +X one; the other is its mirror): from x 20 out to the deck's edge,
# from z 13.5 to 78. Its config outline is this one, Z reversed.
FLANK: list[OutlinePoint] = [
    [20, 78],
    [44.9, 78],
    [56, 60],
    [60, 20],
    [60.3, 13.5],
    [20, 13.5],
]
# An aft wing plate (the +X one): from x 30 out to the deck's edge, from z -45 to 13.5.
WING: list[OutlinePoint] = [
    [30, 13.5],
    [60.3, 13.5],
    [62, -40],
    [61.2, -45],
    [30, -45],
]
# The furnace's crown plate: an octagon the hearth's top, where the stack stands (its sides face
# the axes, as the hearth's do).
CROWN_RADIUS = 21.0
CROWN_FOOT = DECK_TOP + 12.8
CROWN_TOP = CROWN_FOOT + 1.2
CROWN: list[OutlinePoint] = [
    [
        math.cos((k + 0.5) * math.pi / 4) * CROWN_RADIUS,
        math.sin((k + 0.5) * math.pi / 4) * CROWN_RADIUS,
    ]
    for k in range(8)
]
# The furnace's tapering stack (a lathe profile, from the crown plate up).
STACK = [
    [13.0, 0.0],
    [11.5, 12.0],
    [9.5, 18.0],
    [11.0, 19.5],
]
# The casting shed on each aft wing plate: centre, width, length, height.
WING_SHED = [42.0, 0.0, 10.0, 20.0, 7.0]


def plating(p: Any, outline: list[OutlinePoint]) -> None:
    """Draw an iron plate over `outline`, lying on the deck, `PLATE` thick."""
    p.hull.bevel_slab(outline, [DECK_TOP, DECK_TOP + 0.5, TOP], [0, 1], H.dark, None, H.panel)


def plating_pieces(outlines: list[list[OutlinePoint]], heights: list[float]) -> list[Any]:
    """Return the pieces a plating over `outlines` bursts into: plates cracked between `heights`.

    Its share of the boss's piece budget, three regions sharing it.
    """
    most = math.floor(BOSS_LOOK.armour.bossChunks / 3)
    return [piece[0] for piece in plate_pieces(outlines, heights, H.panel, most)]


def draw_flanks(p: Any) -> None:
    """Draw the fore flank plates (FB-FOUNDRY-ARK-16), both sides.

    On each the hazard paint, a vent, a soot stain and a molten seam between the deck plates. The
    gun batteries lie folded under them.
    """
    hull = p.hull
    for s in SIDES:
        plating(p, FLANK if s > 0 else flip_x(FLANK))
        hazard(hull, [s * 40, 76], [10, 6], 4, TOP + 0.05)
        vent(hull, [s * 48, TOP, 40], [8, 10], 4)
        decal(hull, box2d(20, 14, [s * 30, 40]), TOP + 0.04, SOOT)
        seam(p.neon, [s * 22, 30], [s * 46, 52], [TOP, 0.5, 0.15], MOLTEN)


def draw_wings(p: Any) -> None:
    """Draw the aft wing plates (FB-FOUNDRY-ARK-18), both sides.

    On each a casting shed, the magma vein's middle run, a gland, a vent and a molten seam. The
    gatlings lie folded under them.
    """
    hull = p.hull
    for s in SIDES:
        plating(p, WING if s > 0 else flip_x(WING))
        shed(p, s, WING_SHED, TOP)
        magma_vein(
            p,
            [
                [s * 31, TOP + 0.3, -44],
                [s * 44, TOP + 0.3, -36],
                [s * 56, TOP + 0.3, -10],
            ],
            1.6,
            MOLTEN,
        )
        glands(p, [[s * 50, TOP, 10]], 2.6, ARK_ORANGE)
        vent(hull, [s * 48, TOP, -20], [8, 10], 4)
        seam(p.neon, [s * 50, -30], [s * 56, 6], [TOP, 0.5, 0.15], MOLTEN)


def draw_spine(p: Any) -> None:
    """Draw the spine plating (FB-FOUNDRY-ARK-18): the furnace's crown plate and its stack.

    The stack tapering up from the plate, sooted at its lip, ringed in orange, the throat's charge
    light in its mouth (the core's ring volleys leave from there). The drone hangar lies folded
    under it, in the hearth.
    """
    hull = p.hull
    hull.slab(CROWN, [CROWN_FOOT, CROWN_TOP], SKIN.panel, None, H.panel)
    hull.lathe(STACK, 8, H.panel, Placement([0, CROWN_TOP, 0], math.pi / 8))
    hull.ring(11.2, 2.6, 8, SOOT, Placement([0, CROWN_TOP + 17, 0], math.pi / 8))
    p.neon.ring(12.3, 0.8, 8, ARK_ORANGE, Placement([0, CROWN_TOP + 6, 0], math.pi / 8))
    p.charge.cylinder(9, 0.4, 8, WHITE, Placement([0, CROWN_TOP + 17.4, 0]))


# The regions' drawings (`drawing.armour`): the plates, and the pieces they burst into.
FOUNDRY_ARK_ARMOUR = {
    "flanks": {
        "whole": draw_flanks,
        "pieces": plating_pieces([FLANK, flip_x(FLANK)], [DECK_TOP, TOP]),
    },
    "wings": {
        "whole": draw_wings,
        "pieces": plating_pieces([WING, flip_x(WING)], [DECK_TOP, TOP]),
    },
    "spine": {"whole": draw_spine, "pieces": plating_pieces([CROWN], [CROWN_FOOT, CROWN_TOP])},
}
