# Copyright (c) 2026 Renaud Guillon
"""FB-MESA-FORTRESS-03: the Mesa Fortress's destroyable parts.

The lances its forelimbs cradle and the spore silos on its back Logical pixels, nose +Z, Y up.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.final_boss_shapes import edge_strips, shift
from game.view.bosses.world_1_organic_kit import (
    F,
    M,
    barbs,
    graft,
    polygon,
    sac,
    tentacle,
    vein_line,
)
from render.geometry.organic import organ
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["mesa-fortress"]

# Height of the skirt's top.
BASE_TOP = 7

# Where the sinews bind the lance's emitter (its laser mount's barrel, BOSS-58), from the lance's
# centre: across it, up and forward.
BINDING = [4.5, 7.7, 16]


def draw_lance(p: Any, at: Vec3) -> None:
    """Draw a laser lance (FB-MESA-FORTRESS-03): a swollen gland in the forelimb's cradle.

    Its laser emitter on the cradle before it (its mount, drawn by `build_boss_model`, BOSS-58),
    sinews binding it.
    """
    organ(p.flesh, 12, 8, F.slate, Placement(shift(at, [0, -2, -4]), math.pi / 8), 0.5)
    graft(p, polygon(6, 7, [1, 1.4]), [10, 11.4], shift(at, [0, 0, -6]))
    x = at[0]
    z = at[2]
    edge_strips(
        p.neon,
        [
            [x, z - 13],
            [x, z + 4],
        ],
        1.4,
        [11.4, 12],
        N,
    )
    for s in [-1, 1]:
        tentacle(
            p,
            shift(at, [s * 9, 4, -2]),
            shift(at, [s * BINDING[0], BINDING[1], BINDING[2]]),
            [s * 2, 2, 0],
            [1.6, 1],
            F.sinew,
            4,
        )
        vein_line(p, shift(at, [s * 11, 2, -12]), shift(at, [s * 6, 8, 4]), [s * 2, 2, 0], 1, N)


def draw_silo(p: Any, at: Vec3) -> None:
    """Draw a missile silo (FB-MESA-FORTRESS-03): a swollen spore pod on the shell's rear.

    A grafted collar round its mouth, its four missile ports standing in it like seeds (its mount,
    drawn by `build_boss_model`, BOSS-58), a vein ring at its foot.
    """
    base = shift(at, [0, BASE_TOP, 0])
    organ(p.flesh, 12.5, 7, F.graphite, Placement(shift(base, [0, -4, 0])), 0.4)
    p.neon.ring(12.7, 0.8, 7, N, Placement(shift(base, [0, 0.6, 0])))
    sac(p, shift(base, [0, 0, 0]), 9, F.slate, {"stretch": 0.3})
    graft(p, polygon(6, 8.5), [4.6, 5.4], base, {"color": M.base})
    barbs(p, shift(base, [0, 3, -10]), {"count": 3, "spacing": 4, "size": 3, "dir": [0, 0.6, -1]})
