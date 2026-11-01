# Copyright (c) 2026 Renaud Guillon
"""FB-STEAM-DREADNOUGHT-03 to FB-STEAM-DREADNOUGHT-05, 4-1: the Steam Dreadnought's parts.

Its two smokestacks, its two broadside turrets (each turning on its barbette, D-058) and the missile
rack on its stern. Logical pixels, nose +Z, Y up; the left ones (the screen's left, -X on the
playfield) are drawn at +X.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.boss_kit import mirror
from game.config.bosses.world_4.steam_dreadnought import (
    DREAD_HEIGHTS,
    DREAD_RACK,
    DREAD_STACK,
    DREAD_TURRET_GUNS,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.final_boss_shapes import missile_tips
from game.view.bosses.mini_boss_greebles import hazard
from game.view.bosses.mini_boss_shapes import SHADE, WHITE, H, offset
from game.view.bosses.world_4.black_sands_kit import (
    FORGE,
    barrel_to,
    blot,
    molten_seam,
    soot,
    steam,
)
from game.view.bosses.world_4.living_forge import SKIN
from render.geometry.organic import organ
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Rgb = list[float]
type Vec3 = list[float]
# __pragma__ ("noskip")


def _neon_or(kind: str, fallback: Rgb) -> Rgb:
    """`BOSS_LOOK.neon[kind] ?? fallback`."""
    colour: Rgb = BOSS_LOOK.neon[kind]
    if colour == None:
        return fallback
    return colour


def _sign(v: float) -> float:
    """`Math.sign`."""
    if v > 0:
        return 1
    if v < 0:
        return -1
    return 0


# The Steam Dreadnought's red neon (FB-STEAM-DREADNOUGHT-06).
DREAD_RED = _neon_or("steam-dreadnought", [1, 0.08, 0.1])

# FB-STEAM-DREADNOUGHT-03 to FB-STEAM-DREADNOUGHT-05: the stacks are steaming blowholes of flesh
# banded in metal, the rack a fleshy growth cased in a metal launcher, the turrets metal grafts on
# flesh mounts.

DECK = DREAD_HEIGHTS.deck


def side_at(at: list[float]) -> float:
    """Return the side of a part drawn at `at`: +1 for a left one (at +X), -1 for a right one."""
    s = _sign(at[0])
    if s == 0:
        return 1
    return s


# A smokestack's casing (a lathe profile up from the deck, radius and height).
STACK = [
    [9.5, DECK],
    [9.5, DECK + 2.0],
    [7.2, DECK + 3.0],
    [6.4, DECK + 8.0],
    [6.4, DREAD_HEIGHTS.stack - 4.0],
    [7.4, DREAD_HEIGHTS.stack - 3.0],
    [7.4, DREAD_HEIGHTS.stack],
]


def smokestack(p: Any, at: Vec3) -> None:
    """Add a smokestack (FB-STEAM-DREADNOUGHT-03) around its centre `at`.

    A tall casing banded with worn metal and a red neon ring, sooted at the top, its mouth glowing
    as the next ring loads, steam puffing back from it.
    """
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    s = side_at(at)
    source = DREAD_STACK if s > 0 else mirror(DREAD_STACK)
    if len(source) == 0:
        return
    m = source[0]
    tip = boss_point(m[0], m[1], m[2])
    p.flesh.lathe(STACK, 8, SKIN.base, Placement([at[0], 0, at[2]], math.pi / 8))
    for y in [DECK + 9, DECK + 15]:
        hull.ring(6.7, 1, 8, SHADE["edge"], Placement([at[0], y, at[2]], math.pi / 8))
    neon.ring(6.75, 0.9, 8, DREAD_RED, Placement([at[0], DREAD_HEIGHTS.stack - 6, at[2]]))
    hull.ring(7.6, 2.4, 8, FORGE["soot"], Placement(offset(tip, 0, -2.4, 0), math.pi / 8))
    hull.cylinder(5.8, 0.3, 8, H.dark, Placement(offset(tip, 0, -0.25, 0)))
    charge.cylinder(4.6, 0.3, 8, WHITE, Placement(offset(tip, 0, -0.1, 0)))
    muzzle(tip)
    steam(neon, offset(tip, s * 0.6, 3, -3), 3, 2.6)
    hull.box([2, 10, 2], H.dark, Placement([at[0] - s * 7.4, DECK, at[2] - 3]))


# The broadside turret's barbette (a lathe profile up from the deck) and its dome.
BARBETTE = [
    [10.5, DECK - 0.5],
    [10.5, DECK + 2.5],
    [9.5, DECK + 3.0],
]
DOME = [
    [8.6, 0.0],
    [8.6, 1.4],
    [7.2, 3.4],
    [4.0, 4.6],
    [0.0, 4.8],
]


def barbette(p: Any, at: Vec3) -> None:
    """Add a broadside turret's mount (FB-STEAM-DREADNOUGHT-04).

    Its armoured barbette with a red ring, on the sponson.
    """
    hull = p.hull
    neon = p.neon
    flesh = p.flesh
    s = side_at(at)
    flesh.lathe(BARBETTE, 8, SKIN.panel, Placement([at[0], 0, at[2]], math.pi / 8))
    neon.ring(10.6, 0.7, 8, DREAD_RED, Placement([at[0], DECK + 0.6, at[2]], math.pi / 8))
    hazard(hull, [at[0] + s * 4, DECK + 0.05, at[2] - 13], [10, 3], 4)


def broadside(p: Any, at: Vec3) -> None:
    """Add a broadside turret (FB-STEAM-DREADNOUGHT-04) around its pivot `at`.

    A faceted dome with a mantlet, a rangefinder across its roof, twin barrels pointing down the
    screen at rest (they turn with the turret, D-058), a molten seam on its roof.
    """
    hull = p.hull
    neon = p.neon
    s = side_at(at)
    foot = [at[0], DECK + 2.6, at[2]]
    hull.lathe(DOME, 8, H.base, Placement(foot, math.pi / 8))
    hull.box([9, 4, 4], H.dark, Placement(offset(foot, 0, 0.5, 6.6)), H.panel)
    hull.box([16, 1.4, 2], H.panel, Placement(offset(foot, 0, 4.2, -2)))
    hull.box([3, 1.6, 2.6], SHADE["edge"], Placement(offset(foot, s * 7.5, 3.8, -2)))
    molten_seam(
        neon,
        [
            [at[0] - 4, at[2] + 1],
            [at[0], at[2] + 2.2],
            [at[0] + 4, at[2] + 1],
        ],
        foot[1] + 4.6,
    )
    guns = DREAD_TURRET_GUNS if s > 0 else mirror(DREAD_TURRET_GUNS)
    for tip in guns:
        barrel_to(p, tip, [1.3, 10])


# The missile tubes: their radius (their tips stand `2.6 radius` above their foot).
TUBE = 1.8


def missile_rack(p: Any, at: Vec3) -> None:
    """Add the missile rack (FB-STEAM-DREADNOUGHT-05) around its centre `at`, on the stern.

    An armoured launcher box, red lights along its sides, four missile tips in their tubes, soot
    from the launches.
    """
    hull = p.hull
    neon = p.neon
    cell_height = DREAD_RACK[0][2] if len(DREAD_RACK) > 0 else DREAD_HEIGHTS.rack
    top = cell_height - TUBE * 2.6
    organ(p.flesh, 13, 6, SKIN.base, Placement([at[0], DECK - 3, at[2]]), 0.3)
    hull.box([18, top - DECK, 18], H.base, Placement([at[0], DECK, at[2]]), H.panel)
    for s in [-1, 1]:
        neon.box([0.5, 0.8, 18], DREAD_RED, Placement([at[0] + s * 11.1, top - 2, at[2]]))
        hull.box([2.4, top - DECK + 1, 6], H.dark, Placement([at[0] + s * 12, DECK - 1, at[2] - 7]))
    missile_tips(p, [at[0], top, at[2]], [2, 2], [10, TUBE])
    soot(hull, blot([at[0], at[2] + 6], 4, 0.5, 4), top)
