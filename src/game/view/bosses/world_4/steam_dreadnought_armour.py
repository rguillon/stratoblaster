# Copyright (c) 2026 Renaud Guillon
"""FB-STEAM-DREADNOUGHT-15, FB-STEAM-DREADNOUGHT-17, 4-1: the Steam Dreadnought's armour (D-254).

Drawn as pieces of their own, lying on the core as the boss rests (BOSS-42): the two front side
decks that fan out at its first transformation (`decks-left` at +X, `decks-right` at -X), the stern
flank decks (`flanks`) and the stern half of the citadel (`spine`) that burst off at its second.
The core draws the deck between them (`deck_plate`). Logical pixels, nose +Z, Y up; +X is the
screen's left, so a config outline (x, y) is drawn at (-x, -y).
"""

from game.config.bosses.world_4.steam_dreadnought import DREAD_HEIGHTS
from game.view.bosses.mini_boss_shapes import H
from game.view.bosses.overlord_city import edge_lights
from game.view.bosses.world_4.black_sands_kit import blot, molten_seam, soot
from game.view.bosses.world_4.living_forge import SKIN, glands, magma_vein
from game.view.bosses.world_4.steam_dreadnought_parts import DREAD_RED
from game.view.enemies.enemy_shapes import SIDES, flip_x
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type OutlinePoint = list[float]
type Vec3 = list[float]
# __pragma__ ("noskip")


N = DREAD_RED
DECK = DREAD_HEIGHTS.deck
# The deck slabs: bottom, waist and top of their bevel, and their insets (`bevel_slab`).
DECK_SLAB = [4.5, 7, DECK]
DECK_INSETS = [1, 0.8]
# The red rim lights along a deck's edges, from one height to the other.
RIM = [5.8, 6.8]

# A front side deck (the +X one, `decks-left`; the other is its mirror): the deck's own edge from
# its hinge at its inner bow corner (20, 54) round the sponson to the seam with the core at x 20.
# Its config outline (`moving_region("decks", ...)`) is this one, Z reversed.
DECK_PIECE: list[OutlinePoint] = [
    [20, 54],
    [24, 54],
    [36, 40],
    [66, 32],
    [70, 20],
    [66, 8],
    [40, 2],
    [40, -2],
    [20, -2],
]
# Its lit edges: the sponson's rim (not the seams with the core).
DECK_PIECE_RIM = [1, 2, 3, 4, 5, 6, 7]
# A stern flank deck (the +X one; `flanks` draws both): from the mid band to the stern edge.
FLANK_PIECE: list[OutlinePoint] = [
    [18, -17],
    [39.5, -17],
    [39, -30],
    [32, -60],
    [20, -76],
    [18, -76],
]
FLANK_PIECE_RIM = [1, 2, 3, 4]
# The raised citadel amidships (width, height), from the stern of its spine half to its bow: the
# stern half (`spine`, to `SPINE_BOW`) is armour, the bow half under the bridge is the core's.
CITADEL = [36.0, 3.0]
CITADEL_Z = [-46.0, 28.0]
SPINE_BOW = -13.0


def sided(outline: list[OutlinePoint], s: float) -> list[OutlinePoint]:
    """Return `outline` (drawn at +X) for side `s`: itself at +X, mirrored at -X."""
    return outline if s > 0 else flip_x(outline)


def deck_plate(p: Any, outline: list[OutlinePoint], rim: list[int]) -> None:
    """Draw a deck plate over `outline`: a bevelled slab of scorched hide, its edges `rim` lit."""
    p.flesh.bevel_slab(outline, DECK_SLAB, DECK_INSETS, SKIN.dark, None, SKIN.panel)
    edge_lights(p.neon, outline, rim, RIM, N)


def deck_seam(neon: Any, y: float, half: float, z: float) -> None:
    """Draw a molten seam across a deck at height `y`, `half` either side of the axis, about `z`."""
    molten_seam(
        neon,
        [
            [-half, z],
            [-half * 0.4, z + 1.5],
            [half * 0.15, z - 1],
            [half, z + 0.8],
        ],
        y + 0.05,
    )


def cowl(hull: Any, at: Vec3) -> None:
    """Draw a cowl standing on a deck at `at`: a short pipe with a hooded top."""
    hull.cylinder(1.6, 3, 5, H.panel, Placement(at))
    hull.box([3, 2.2, 2.4], H.dark, Placement([at[0], at[1] + 3, at[2] + 0.6]))


def citadel(hull: Any, z: list[float]) -> None:
    """Draw the citadel's section from `z[0]` to `z[1]`: a low metal box on the deck."""
    hull.box(
        [CITADEL[0], CITADEL[1], z[1] - z[0]],
        H.base,
        Placement([0, DECK, (z[0] + z[1]) / 2]),
        H.panel,
    )


def draw_deck(s: float) -> Any:
    """Return the drawing of the front side deck at side `s` (FB-STEAM-DREADNOUGHT-15).

    The sponson deck plate with its rim lights, the molten vein's forward run, two glands and a
    soot stain on it; the broadside turret's barbette stands on it while the turret lives.
    """

    def draw(p: Any) -> None:
        deck_plate(p, sided(DECK_PIECE, s), DECK_PIECE_RIM)
        magma_vein(p, [[s * 39.5, DECK + 0.3, -1], [s * 36, DECK + 0.3, 30]], 1.4)
        glands(p, [[s * 44, DECK, 10], [s * 30, DECK, 44]], 2.2, N)
        soot(p.hull, blot([s * 50, 20], 5, 0.8, 2 * s), DECK)

    return draw


def draw_flanks(p: Any) -> None:
    """Draw the stern flank decks (FB-STEAM-DREADNOUGHT-17), both sides.

    Each a deck plate from the mid band to the stern with its rim lights, the molten vein's stern
    run, a soot stain and a cowl on it; the mortars lie folded under them.
    """
    for s in SIDES:
        deck_plate(p, sided(FLANK_PIECE, s), FLANK_PIECE_RIM)
        magma_vein(p, [[s * 34, DECK + 0.3, -60], [s * 40, DECK + 0.3, -20]], 1.4)
        soot(p.hull, blot([s * 30, -32], 7, 1.6, s), DECK)
        cowl(p.hull, [s * 22, DECK, -44])


def draw_spine(p: Any) -> None:
    """Draw the spine plating (FB-STEAM-DREADNOUGHT-17): the citadel's stern half on the deck.

    A molten seam between its plates; the ring emitter lies folded under it.
    """
    citadel(p.hull, [CITADEL_Z[0], SPINE_BOW])
    deck_seam(p.neon, DECK + CITADEL[1], CITADEL[0] / 2 - 2, -30)
