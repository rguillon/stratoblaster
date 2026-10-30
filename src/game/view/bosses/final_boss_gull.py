"""P07-R05, P16-R06: the Gull Mothership's destroyable parts, its brood pouches and flak growths,
ported from `bosses/final-boss-gull.ts`. Logical pixels, nose +Z, Y up.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.view.bosses.final_boss_shapes import edge_strips, shift, sided  # noqa: E402
from game.view.bosses.world_1_organic_kit import (  # noqa: E402
    F,
    M,
    barbs,
    graft,
    growth,
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

N = BOSS_LOOK.neon["gull-mothership"]
WHITE = [1, 1, 1]

# Height of the mantle's top.
DECK_TOP = 4
# The right pouch around its centre, its outer side to +X, its inner side on the mantle.
HANGAR = [
    [-17, 20],
    [17, 20],
    [21, 14],
    [21, -16],
    [17, -21],
    [-17, -21],
]
HANGAR_TOP = 10
# The pouch's birth slit, glowing as the next launch charges (around the slit's centre).
SLIT = [
    [-6, 13],
    [6, 13],
    [8, 0],
    [6, -13],
    [-6, -13],
    [-8, 0],
]


def _sign_or_one(x: float) -> float:
    """`Math.sign(x) || 1`."""
    return -1 if x < 0 else 1


def draw_hangar(p: Any, at: Vec3) -> None:
    """A hangar bay (P16-R06): a swollen brood pouch on the mantle's flank, a glowing birth slit in
    its top between fleshy lips, green glands down both sides, a grafted brace on its outer side.
    """
    s = _sign_or_one(at[0])
    p.flesh.bevel_slab(
        sided(HANGAR, s),
        [-6, -1, HANGAR_TOP - 3],
        [2, 4],
        F.crimson,
        Placement(at),
        F.purple,
    )
    organ(p.flesh, 16, 8, F.purple, Placement(shift(at, [0, -1, -1]), math.pi / 8), 0.32)
    hatch = shift(at, [s * 2, HANGAR_TOP, -2])
    p.charge.slab(SLIT, [HANGAR_TOP - 1.2, HANGAR_TOP - 0.4], WHITE, Placement(hatch))
    for dx in [-1, 1]:
        tentacle(
            p,
            shift(hatch, [dx * 8, -0.6, -13]),
            shift(hatch, [dx * 8, -0.6, 13]),
            [dx * 1.5, 1.5, 0],
            [1.8, 1.8],
            F.sinew,
            4,
        )
        for k in range(4):
            p.vein.box(
                [1.6, 0.8, 2.4],
                N,
                Placement(shift(hatch, [dx * 11.5, -2.4, -10.5 + k * 7])),
            )
    x = hatch[0]
    z = hatch[2]
    front = [
        [x - 8, z + 16],
        [x + 8, z + 16],
    ]
    edge_strips(p.neon, front, 1.4, [HANGAR_TOP - 2.4, HANGAR_TOP - 1.6], N)
    graft(
        p,
        polygon(4, 6, [0.7, 2.2]),
        [HANGAR_TOP - 3.5, HANGAR_TOP - 2.2],
        shift(at, [s * 16, 0, -2]),
        {"color": M.base},
    )
    vein_line(p, shift(at, [-s * 18, 2, 4]), shift(at, [-s * 34, -1, 10]), [0, 2, 0], 1.1, N)
    barbs(
        p,
        shift(at, [s * 15, 4, -14]),
        {"count": 2, "spacing": 6, "size": 3, "dir": [s, 0.3, -0.5]},
    )


def draw_flak(p: Any, at: Vec3) -> None:
    """A flak growth on the front of the mantle (P16-R06): a swollen, plated mound under its turret,
    a feeding sac behind it."""
    growth(p, shift(at, [0, DECK_TOP - 2.5, 0]), 12, N, {"flesh": F.crimson, "height": 0.38})
    sac(
        p,
        shift(at, [_sign_of(at[0]) * 7, DECK_TOP, -9]),
        3.5,
        F.purple,
        {"stretch": 0.6},
    )


def _sign_of(x: float) -> float:
    """`Math.sign(x)`."""
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0
