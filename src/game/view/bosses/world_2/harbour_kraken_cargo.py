# Copyright (c) 2026 Renaud Guillon
"""The Harbour Kraken's cargo (FB-HARBOUR-KRAKEN-03, FB-HARBOUR-KRAKEN-02, 2-2).

The container bay at its stern (a part, launching Gnats); the hatch covers along its deck are on
its armour (`harbour_kraken_armour`). Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from game.config.enemy_look import ENEMY_LOOK
from game.view.bosses.final_boss_shapes import open_hatch
from game.view.bosses.mini_boss_greebles import rect
from game.view.bosses.mini_boss_shapes import offset
from game.view.bosses.world_2.fjord_lynx_frost import RIME
from game.view.bosses.world_2.harbour_kraken_cranes import DECK_Y, ORANGE_NEON, beam
from game.view.bosses.world_2.w2_organic import ICE_FLESH, crystals
from render.geometry.organic import organ
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import EnemyParts

type Rgb = list[float]
type Vec3 = list[float]
type Stacks = list[list[Any]]
# __pragma__ ("noskip")


H = ENEMY_LOOK.hull

# The eggs' flesh shades (FB-HARBOUR-KRAKEN-03), where the container paints were.
PAINT = [
    ICE_FLESH.membrane,
    ICE_FLESH.graphite,
    ICE_FLESH.teal,
    ICE_FLESH.sinew,
]
# A container's size: across, high, along; and where an egg lying in its place is widest, along
# it from its base (`organ`: 0.45 of its length).
BOX = [7, 5, 13]
EGG_WIDEST = 0.45 * BOX[2]
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
    """Add a container at `at` (its base), painted `paint`.

    Its doors' end hatched, snow on its roof.
    """
    # FB-HARBOUR-KRAKEN-03: an egg lying in the brood sac where a container was, a gland lit in it
    # (on the egg's back where it is widest, BOSS-52).
    organ(p.flesh, BOX[0] / 2, 6, paint, Placement(at, 0, math.pi / 2), BOX[2] / BOX[0])
    organ(
        p.vein,
        0.9,
        4,
        ORANGE_NEON,
        Placement(offset(at, 0, BOX[1] * 0.8, EGG_WIDEST)),
        0.6,
    )


def container_bay(p: EnemyParts, at: Vec3) -> None:
    """Add the container bay (FB-HARBOUR-KRAKEN-03).

    Stacks of frosted containers either side of an open launch hatch, an orange-lit gantry over it;
    its Gnats leave through the hatch.
    """
    hull = p.hull
    neon = p.neon
    # FB-HARBOUR-KRAKEN-03: the brood sac, a cradle of membrane full of eggs, its mouth held open by
    # metal.
    p.flesh.bevel_slab(
        rect(38, 32),
        [DECK_Y - 1, DECK_Y, DECK_Y + 1.5],
        [0, 0.8],
        ICE_FLESH.membrane,
        Placement(at),
        ICE_FLESH.graphite,
    )
    floor_at = offset(at, 0, DECK_Y + 1.5, 0)
    for i in range(len(STACKS)):
        x = STACKS[i][0]
        z = STACKS[i][1]
        high = STACKS[i][2]
        for k in range(high):
            paint = PAINT[(i + k) % len(PAINT)]
            if paint == None:
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
