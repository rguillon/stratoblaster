"""The Harbour Kraken's cargo: the container bay at its stern (a part, launching Gnats) and the
hatch covers along its deck, ported from `bosses/world-2/harbour-kraken-cargo.ts` (P08-R10,
2-2). Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemy_look import ENEMY_LOOK
from game.view.bosses.final_boss_shapes import open_hatch
from game.view.bosses.mini_boss_greebles import rect
from game.view.bosses.mini_boss_shapes import offset
from game.view.bosses.world_2.fjord_lynx_frost import RIME, snow_cap
from game.view.bosses.world_2.harbour_kraken_cranes import DECK_Y, ORANGE_NEON, beam
from game.view.bosses.world_2.w2_organic import ICE_FLESH, crystals, gland
from render.geometry.organic import organ
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
type Stacks = list[list[Any]]
__pragma__("noskip")

H = ENEMY_LOOK.hull

# The eggs' flesh shades (P16-R06), where the container paints were.
PAINT = [
    ICE_FLESH.membrane,
    ICE_FLESH.purple,
    ICE_FLESH.teal,
    ICE_FLESH.sinew,
]
# Hatch covers past this z (the bow cover) are nudged over by 2 instead of 3.
FRONT_COVER_Z = 20
# A container's size: across, high, along.
BOX = [7, 5, 13]
# The stacks either side of the launch hatch: x, z, and how many high.
STACKS = [  # type: Stacks
    [-14.5, -6, 2],
    [-7.5, -6, 1],
    [-14.5, 8, 1],
    [7.5, 7, 2],
    [14.5, 7, 1],
    [14.5, -7, 2],
]


def _container(p: EnemyParts, at: Vec3, paint: Rgb) -> None:
    """A container at `at` (its base), painted `paint`, its doors' end hatched, snow on its roof."""
    # P16-R06: an egg lying in the brood sac where a container was, a gland lit in it.
    organ(p.flesh, BOX[0] / 2, 6, paint, Placement(at, 0, math.pi / 2), BOX[2] / BOX[0])
    organ(p.vein, 0.9, 4, ORANGE_NEON, Placement(offset(at, 0, BOX[1] * 0.8, 0)), 0.6)


def container_bay(p: EnemyParts, at: Vec3) -> None:
    """The container bay (P08-R10): stacks of frosted containers either side of an open launch
    hatch, an orange-lit gantry over it; its Gnats leave through the hatch."""
    hull = p.hull
    neon = p.neon
    # P16-R06: the brood sac, a cradle of membrane full of eggs, its mouth held open by metal.
    p.flesh.bevel_slab(
        rect(38, 32),
        [DECK_Y - 1, DECK_Y, DECK_Y + 1.5],
        [0, 0.8],
        ICE_FLESH.membrane,
        Placement(at),
        ICE_FLESH.purple,
    )
    floor_at = offset(at, 0, DECK_Y + 1.5, 0)
    for i in range(len(STACKS)):
        x = STACKS[i][0]
        z = STACKS[i][1]
        high = STACKS[i][2]
        for k in range(high):
            paint = PAINT[(i + k) % len(PAINT)]
            if paint == None:  # noqa: E711
                paint = H.base
            _container(p, offset(floor_at, x, k * BOX[1], z), paint)
    open_hatch(p, offset(floor_at, 0, 0.1, 0), [8, 24])
    for z in [-11, 11]:
        hull.box([1.2, 12, 1.2], H.panel, Placement(offset(floor_at, -5.5, 0, z)))
        hull.box([1.2, 12, 1.2], H.panel, Placement(offset(floor_at, 5.5, 0, z)))
        beam(
            hull,
            offset(floor_at, -6, 12, z),
            offset(floor_at, 6, 12, z),
            [1.6, 1.4],
            [H.base, RIME],
        )
        neon.box([9, 0.4, 0.6], ORANGE_NEON, Placement(offset(floor_at, 0, 13.45, z)))
    crystals(p.flesh, offset(floor_at, -17, 0, -14), 3)


def hatch_covers(p: EnemyParts) -> None:
    """The hatch covers on the deck between the cranes: frosted lids with seams and a vent."""
    hull = p.hull
    flesh = p.flesh
    for z in [-20, 40]:
        # Armour plates grafted on the shell.
        hull.bevel_slab(
            rect(26, 12),
            [DECK_Y - 0.5, DECK_Y, DECK_Y + 2],
            [0, 1],
            H.panel,
            Placement([0, 0, z]),
            RIME,
        )
        snow_cap(
            flesh,
            rect(18, 7),
            DECK_Y + 2,
            Placement([2 if z > FRONT_COVER_Z else -3, 0, z]),
        )
    gland(p, [-10, DECK_Y + 2.4, 40], 1.4, ORANGE_NEON)
