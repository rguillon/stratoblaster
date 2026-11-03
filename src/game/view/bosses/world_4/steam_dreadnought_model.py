# Copyright (c) 2026 Renaud Guillon
"""FB-STEAM-DREADNOUGHT-01 to FB-STEAM-DREADNOUGHT-06, 4-1: the Steam Dreadnought.

Logical pixels, nose +Z (down the screen), Y up towards the camera; +X is the screen's left. A
flying battleship: a long armoured hull under a deck with sponsons for its broadside turrets, a
stepped bridge over the core, two smokestacks amidships, a laser ram at the bow and a missile rack
on the stern.

FB-STEAM-DREADNOUGHT-02: a living sky-leviathan, its flesh belly banded and ribbed in bone, its back
a scorched hide, a metal bridge, guns and ram grafted on, steaming blowholes for stacks.
"""

from game.config.bosses.world_4.steam_dreadnought import (
    DREAD_BEACON,
    DREAD_BOW_GUNS,
    DREAD_HEIGHTS,
    DREAD_LENS,
    STEAM_DREADNOUGHT,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_greebles import mast
from game.view.bosses.mini_boss_greebles import seam, vent
from game.view.bosses.mini_boss_shapes import QUARTER, WHITE, H, offset
from game.view.bosses.overlord_city import symmetric
from game.view.bosses.world_4.black_sands_kit import (
    FORGE,
    barrel_to,
    blot,
    bolts,
    soot,
)
from game.view.bosses.world_4.living_forge import (
    SKIN,
    back_ribs,
    flesh_shell,
    magma_vein,
    reactor_sacs,
)
from game.view.bosses.world_4.steam_dreadnought_armour import (
    CITADEL_Z,
    SPINE_BOW,
    citadel,
    cowl,
    deck_plate,
    deck_seam,
    draw_deck,
    draw_flanks,
    draw_spine,
)
from game.view.bosses.world_4.steam_dreadnought_parts import (
    DREAD_RED,
    barbette,
    broadside,
    missile_rack,
    smokestack,
)
from game.view.enemies.enemy_shapes import HULL_SECTION, SIDES, side_stripe
from render.geometry.organic import RibSpec
from render.geometry.solids import LoftOptions, Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type OutlinePoint = list[float]
type Vec3 = list[float]
# __pragma__ ("noskip")


N = DREAD_RED
DECK = DREAD_HEIGHTS.deck

# The hull under the deck (loft stations, stern to bow: z, half width, bottom, top).
HULL = [
    [-80.0, 16.0, 2.0, 7.0],
    [-72.0, 24.0, -3.0, 8.0],
    [-40.0, 28.0, -6.0, 8.5],
    [10.0, 28.0, -6.0, 8.5],
    [46.0, 22.0, -5.0, 8.0],
    [70.0, 13.0, -2.0, 7.5],
    [84.0, 5.0, 0.0, 7.0],
]
# The core's deck (right half, bow to stern), closed across the bow: the bow, a strip down the
# spine and the mid band between the armour decks (`steam_dreadnought_armour`: the front side
# decks, x 20 out, z -2..54, and the stern flank decks, x 18 out, z -76..-17), which lie on the
# hull beside it and complete the deck's shape at rest.
CORE_DECK = symmetric(
    [
        [10, 78],
        [22, 56],
        [20, 54],
        [20, -2],
        [40, -2],
        [39.5, -17],
        [18, -17],
        [18, -76],
    ],
    84,
)
# Its lit edges: the bow, the mid band's sides and the stern (not the seams with the armour).
CORE_DECK_RIM = [0, 1, 5, 8, 11, 15, 16]
# The bridge's tiers (width, height, depth, z of their middle), bottom to top.
BRIDGE = [
    [34.0, 8.0, 34.0, 4.0],
    [24.0, 8.0, 24.0, 6.0],
    [14.0, 8.0, 14.0, 7.0],
]
# The laser lens at the stem (a lathe profile along its axis).
LENS = [
    [0.0, 0.0],
    [3.0, 0.8],
    [2.0, 2.4],
    [0.0, 3.0],
]


def _deck_flesh(p: Any, s: float) -> None:
    """FB-STEAM-DREADNOUGHT-02: its living flesh on the core's deck: the molten vein's middle run.

    The vein's stern and forward runs, and the glands, are on the armour decks either side.
    """
    magma_vein(p, [[s * 40, DECK + 0.3, -17], [s * 39.5, DECK + 0.3, -3]], 1.4)


def _draw_hull(p: Any) -> None:
    """Draw the hull, the deck and the reactors.

    The hull has glowing seams low on its sides, the deck a red-lit rim.
    """
    neon = p.neon
    flesh_shell(p.flesh, HULL_SECTION, HULL, [SKIN.base, SKIN.dark])
    for side in [0, 4]:
        neon.loft(
            side_stripe(HULL_SECTION, side, [0.35, 0.6], 1.03),
            HULL[1:6],
            FORGE["molten"],
            None,
            LoftOptions(True, None),
        )
    deck_plate(p, CORE_DECK, CORE_DECK_RIM)
    back_ribs(p, [-60, -48, 36, 48], RibSpec(30, DECK - 2, 4, 1))
    for s in SIDES:
        _deck_flesh(p, s)
    reactor_sacs(p, [[0, 3, -82]], 5, FORGE["molten"])
    reactor_sacs(
        p,
        [
            [14, 3, -78],
            [-14, 3, -78],
        ],
        4,
        FORGE["molten"],
    )


def _draw_deck(p: Any) -> None:
    """Draw the core deck's dressing.

    The citadel's bow half under the bridge, a molten seam between the deck plates, soot at the bow,
    cowls, bolts and a hot vent (the stern soot, cowls and seam are on the armour,
    `steam_dreadnought_armour`).
    """
    hull = p.hull
    citadel(hull, [SPINE_BOW, CITADEL_Z[1]])
    deck_seam(p.neon, DECK, 19, 34)
    for x in [-44, 44]:
        seam(hull, [x, 36], [x, 4], [DECK, 0.6, 0.15], H.dark)
    for s in SIDES:
        cowl(hull, [s * 22, DECK, -4])
        bolts(
            hull,
            [
                [s * 14, -60],
                [s * 14, -50],
                [s * 14, 40],
                [s * 14, 50],
            ],
            DECK,
            1.1,
        )
    soot(hull, blot([0, -70], 8, 0.6, 7), DECK)
    vent(hull, [0, DECK + 0.05, 30], [10, 6], 4)


def _draw_bridge(p: Any) -> None:
    """Draw the bridge over the core.

    Stepped tiers, red-lit windows, wings, a mast and its beacon.
    """
    hull = p.hull
    neon = p.neon
    charge = p.charge
    y = DECK
    for tier in BRIDGE:
        w = tier[0]
        h = tier[1]
        d = tier[2]
        z = tier[3]
        hull.box([w, h, d], H.base, Placement([0, y, z]), H.panel)
        neon.box([w * 0.7, 0.9, 0.4], N, Placement([0, y + h * 0.55, z + d / 2 + 0.05]))
        y += h
    hull.box([44, 1.2, 4], H.panel, Placement([0, DECK + 13, 16]))
    for s in SIDES:
        neon.box([1.2, 1, 1.2], N, Placement([s * 21.5, DECK + 14.2, 16]))
    mast(p, [-4, y, 3], 6, N)
    if len(DREAD_BEACON) == 0:
        return
    m = DREAD_BEACON[0]
    top = boss_point(m[0], m[1], m[2])
    hull.cylinder(3.6, top[1] - y - 0.6, 6, H.panel, Placement([top[0], y, top[2]]), 2.4)
    neon.ring(3.7, 0.7, 6, N, Placement([top[0], y + 0.6, top[2]]))
    charge.cylinder(2.4, 0.6, 6, WHITE, Placement(offset(top, 0, -0.6, 0)), 1)
    p.muzzle(top, "ring")


def _draw_bow(p: Any) -> None:
    """Draw the bow: the gun block with its twin guns, and the laser ram at the stem.

    The ram is lit as it charges.
    """
    hull = p.hull
    charge = p.charge
    muzzle = p.muzzle
    hull.box([24, 3.5, 10], H.base, Placement([0, DECK, 62]), H.panel)
    for m in DREAD_BOW_GUNS:
        barrel_to(p, m, [1.4, 8])
    if len(DREAD_LENS) == 0:
        return
    m = DREAD_LENS[0]
    tip = boss_point(m[0], m[1], m[2])
    back = tip[2] - LENS[len(LENS) - 1][1]
    hull.cylinder(3.8, 12, 8, H.panel, Placement([0, tip[1], back - 12], 0, QUARTER), 3.2)
    hull.ring(4.2, 1.4, 8, FORGE["soot"], Placement([0, tip[1], back - 2], 0, QUARTER))
    charge.lathe(LENS, 6, WHITE, Placement([0, tip[1], back], 0, QUARTER))
    muzzle(tip, "laser")


def build_steam_dreadnought(scene: Any) -> Any:
    """FB-STEAM-DREADNOUGHT-01, FB-STEAM-DREADNOUGHT-06: the Steam Dreadnought.

    A flying battleship 5 L long, red neon: a soot-black armoured hull with glowing seams, a stepped
    bridge over its core, two smokestacks puffing steam, two broadside turrets on sponsons, a laser
    ram at the bow and a missile rack on the stern.
    """

    def core(p: Any) -> None:
        _draw_hull(p)
        _draw_deck(p)
        _draw_bridge(p)
        _draw_bow(p)

    return build_boss_model(
        STEAM_DREADNOUGHT,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "stack-left": smokestack,
                "stack-right": smokestack,
                "turret-left": barbette,
                "turret-right": barbette,
                "rack": missile_rack,
            },
            "turrets": {"turret-left": broadside, "turret-right": broadside},
            # D-254: the front side decks (`decks-right` at -X: config x > 0), the stern flank
            # decks and the spine plating, drawn apart from the core.
            "armour": {
                "decks-right": {"whole": draw_deck(-1)},
                "decks-left": {"whole": draw_deck(1)},
                "flanks": {"whole": draw_flanks},
                "spine": {"whole": draw_spine},
            },
        },
    )
