"""P07-R05, P16-R06: the Mesa Fortress's destroyable parts, the lances its forelimbs cradle and the
spore silos on its back Logical pixels, nose +Z, Y up.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.view.bosses.final_boss_shapes import edge_strips, missile_tips, shift  # noqa: E402
from game.view.bosses.world_1_organic_kit import (  # noqa: E402
    F,
    M,
    barbs,
    graft,
    polygon,
    sac,
    tentacle,
    vein_line,
)
from render.geometry.organic import organ  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[Any]
__pragma__("noskip")

N = BOSS_LOOK.neon["mesa-fortress"]
WHITE = [1, 1, 1]
QUARTER = math.pi / 2

# Height of the skirt's top.
BASE_TOP = 7

# The lance's lens (a lathe profile along its axis).
LENS = [
    [0, 0],
    [4, 1],
    [3.2, 3],
    [0, 3.8],
]


def draw_lance(p: Any, at: Vec3) -> None:
    """A laser lance (P16-R06): a swollen gland in the forelimb's cradle, a long grafted barrel out
    of it ringed with neon, sinews binding it, its lens glowing as it charges."""
    organ(p.flesh, 12, 8, F.crimson, Placement(shift(at, [0, -2, -4]), math.pi / 8), 0.5)
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
    barrel = shift(at, [0, 6, 8])
    p.hull.cylinder(5.5, 28, 8, M.dark, Placement(barrel, 0, QUARTER), 3.6)
    for dz in [6, 13, 20]:
        r = 5.5 - (dz / 28) * 1.9 + 0.3
        p.neon.ring(r, 1.2, 8, N, Placement(shift(barrel, [0, 0, dz]), 0, QUARTER))
    for s in [-1, 1]:
        tentacle(
            p,
            shift(at, [s * 9, 4, -2]),
            shift(barrel, [s * 4.6, 0, 9]),
            [s * 2, 2, 0],
            [1.6, 1],
            F.sinew,
            4,
        )
        vein_line(p, shift(at, [s * 11, 2, -12]), shift(at, [s * 6, 8, 4]), [s * 2, 2, 0], 1, N)
    # The lens glows through the warning line and while the laser fires.
    p.charge.lathe(LENS, 8, WHITE, Placement(shift(barrel, [0, 0, 27.5]), 0, QUARTER))
    p.muzzle(shift(barrel, [0, 0, 31.3]), "laser")


def draw_silo(p: Any, at: Vec3) -> None:
    """A missile silo (P16-R06): a swollen spore pod on the shell's rear, a grafted collar round its
    mouth and four missile tips standing in it like seeds, a vein ring at its foot."""
    base = shift(at, [0, BASE_TOP, 0])
    organ(p.flesh, 12.5, 7, F.purple, Placement(shift(base, [0, -4, 0])), 0.4)
    p.neon.ring(12.7, 0.8, 7, N, Placement(shift(base, [0, 0.6, 0])))
    sac(p, shift(base, [0, 0, 0]), 9, F.crimson, {"stretch": 0.3})
    hatch = shift(base, [0, 5, 0])
    graft(p, polygon(6, 8.5), [4.6, 5.4], base, {"color": M.base})
    p.charge.slab(polygon(6, 6.5), [4.8, 5.6], WHITE, Placement(base))
    missile_tips(p, shift(hatch, [0, 0.4, 0]), [2, 2], [5.6, 1.9])
    barbs(p, shift(base, [0, 3, -10]), {"count": 3, "spacing": 4, "size": 3, "dir": [0, 0.6, -1]})
