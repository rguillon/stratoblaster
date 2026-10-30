"""P10-R11, 4-1: the Steam Dreadnought.
Logical
pixels, nose +Z (down the screen), Y up towards the camera; +X is the screen's left. A flying
battleship: a long armoured hull under a deck with sponsons for its broadside turrets, a stepped
bridge over the core, two smokestacks amidships, a laser ram at the bow and a missile rack on the
stern. P16-R06: a living sky-leviathan, its flesh belly banded and ribbed in bone, its back a
scorched
hide, a metal bridge, guns and ram grafted on, steaming blowholes for stacks.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_4.steam_dreadnought import (  # noqa: E402
    DREAD_BEACON,
    DREAD_BOW_GUNS,
    DREAD_HEIGHTS,
    DREAD_LENS,
    STEAM_DREADNOUGHT,
)
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.final_boss_greebles import mast  # noqa: E402
from game.view.bosses.mini_boss_greebles import seam, vent  # noqa: E402
from game.view.bosses.mini_boss_shapes import QUARTER, WHITE, H, offset  # noqa: E402
from game.view.bosses.overlord_city import edge_lights, symmetric  # noqa: E402
from game.view.bosses.world_4.black_sands_kit import (  # noqa: E402
    FORGE,
    barrel_to,
    blot,
    bolts,
    molten_seam,
    soot,
)
from game.view.bosses.world_4.living_forge import (  # noqa: E402
    SKIN,
    back_ribs,
    flesh_shell,
    glands,
    magma_vein,
    reactor_sacs,
)
from game.view.bosses.world_4.steam_dreadnought_parts import (  # noqa: E402
    DREAD_RED,
    barbette,
    broadside,
    missile_rack,
    smokestack,
)
from game.view.enemies.enemy_shapes import HULL_SECTION, SIDES, side_stripe  # noqa: E402
from render.geometry.organic import RibSpec  # noqa: E402
from render.geometry.solids import LoftOptions, Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type OutlinePoint = list[float]
type Vec3 = list[float]
__pragma__("noskip")

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
# The deck (right half, bow to stern), wide at the sponsons, closed across the bow.
DECK_OUTLINE = symmetric(
    [
        [10, 78],
        [22, 56],
        [36, 40],
        [66, 32],
        [70, 20],
        [66, 8],
        [40, 2],
        [39, -30],
        [32, -60],
        [20, -76],
    ],
    84,
)
# The bridge's tiers (width, height, depth, z of their middle), bottom to top.
BRIDGE = [
    [34.0, 8.0, 34.0, 4.0],
    [24.0, 8.0, 24.0, 6.0],
    [14.0, 8.0, 14.0, 7.0],
]
# The raised citadel amidships, under the bridge and between the stacks (w, h, d, z).
CITADEL = [36.0, 3.0, 74.0, -9.0]
# The laser lens at the stem (a lathe profile along its axis).
LENS = [
    [0.0, 0.0],
    [3.0, 0.8],
    [2.0, 2.4],
    [0.0, 3.0],
]


def _deck_flesh(p: Any, s: float) -> None:
    """P16-R05, P16-R06: its living flesh: veins, glands and ribs."""
    magma_vein(
        p,
        [
            [s * 34, DECK + 0.3, -60],
            [s * 40, DECK + 0.3, -20],
            [s * 36, DECK + 0.3, 30],
        ],
        1.4,
    )
    glands(
        p,
        [
            [s * 46, DECK, 0],
            [s * 30, DECK, 44],
        ],
        2.2,
        N,
    )


def _draw_hull(p: Any) -> None:
    """The hull, its glowing seams low on the sides, the deck with its red-lit rim, the reactors."""
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
    p.flesh.bevel_slab(DECK_OUTLINE, [4.5, 7, DECK], [1, 0.8], SKIN.dark, None, SKIN.panel)
    back_ribs(p, [-60, -48, 36, 48], RibSpec(30, DECK - 2, 4, 1))
    for s in SIDES:
        _deck_flesh(p, s)
    every = [i for i in range(len(DECK_OUTLINE))]
    edge_lights(neon, DECK_OUTLINE, every, [5.8, 6.8], N)
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
    """The deck's dressing: molten seams between its plates, soot behind the stacks, cowls,
    bolts."""
    hull = p.hull
    neon = p.neon
    w = CITADEL[0]
    h = CITADEL[1]
    d = CITADEL[2]
    middle = CITADEL[3]
    hull.box([w, h, d], H.base, Placement([0, DECK, middle]), H.panel)
    for row in [[DECK, 24, 34], [DECK + h, w / 2 - 2, -30]]:
        y = row[0]
        half = row[1]
        at = row[2]
        molten_seam(
            neon,
            [
                [-half, at],
                [-half * 0.4, at + 1.5],
                [half * 0.15, at - 1],
                [half, at + 0.8],
            ],
            y + 0.05,
        )
    for x in [-44, 44]:
        seam(hull, [x, 36], [x, 4], [DECK, 0.6, 0.15], H.dark)
    for s in SIDES:
        soot(hull, blot([s * 30, -32], 7, 1.6, s), DECK)
        soot(hull, blot([s * 50, 20], 5, 0.8, 2 * s), DECK)
        for z in [-4, -44]:
            hull.cylinder(1.6, 3, 5, H.panel, Placement([s * 22, DECK, z]))
            hull.box([3, 2.2, 2.4], H.dark, Placement([s * 22, DECK + 3, z + 0.6]))
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
    """The bridge over the core: stepped tiers, red-lit windows, wings, a mast and its beacon."""
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
    """The bow: the gun block with its twin guns, and the laser ram at the stem, lit as it
    charges."""
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
    """P10-R11: the Steam Dreadnought, a flying battleship 5 L long, red neon: a soot-black armoured
    hull with glowing seams, a stepped bridge over its core, two smokestacks puffing steam, two
    broadside turrets on sponsons, a laser ram at the bow and a missile rack on the stern."""

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
        },
    )
