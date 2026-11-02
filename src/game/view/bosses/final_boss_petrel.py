# Copyright (c) 2026 Renaud Guillon
"""FB-STORM-PETREL-03: the Storm Petrel's destroyable parts, growths on its wings.

Tail and breast Logical pixels, nose +Z, Y up.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.final_boss_shapes import barrels, edge_strips, missile_tips, shift
from game.view.bosses.world_1_organic_kit import (
    F,
    M,
    barbs,
    graft,
    growth,
    polygon,
    sac,
    vein_line,
)
from render.geometry.organic import (
    SegmentedBody,
    carapace,
    organ,
    segmented_body,
)
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["storm-petrel"]


def draw_pod(p: Any, at: Vec3) -> None:
    """Draw a wing gun pod (FB-STORM-PETREL-03): a swollen gun gland on the wing.

    A grafted collar at its front and twin barrels at its nose, a vein along each flank.
    """
    growth(p, shift(at, [0, 8, -2]), 13, N, {"flesh": F.slate, "height": 0.3, "armour": False})
    pod = shift(at, [0, 10, 0])
    segmented_body(
        p.flesh,
        SegmentedBody(-16, 14, 3, 7, 0, 9),
        F.graphite,
        Placement(pod),
    )
    graft(p, polygon(6, 5), [7.5, 9.3], shift(pod, [0, 0, 10]))
    for s in [-1, 1]:
        vein_line(p, shift(pod, [s * 6.6, 5, -10]), shift(pod, [s * 6.4, 5, 8]), [s, 0.5, 0], 1, N)
    p.neon.box([1, 0.4, 10], N, Placement(shift(pod, [0, 9.2, -4])))
    barrels(p, shift(pod, [0, 4.3, 14]), [2, 5], [1.3, 7])


def draw_rack(p: Any, at: Vec3) -> None:
    """Draw the tail missile rack (FB-STORM-PETREL-03): a brood sac on the tail.

    A grafted rim round six missile tips standing in it like eggs, a neon lip along its front.
    """
    organ(p.flesh, 13, 8, F.slate, Placement(shift(at, [0, 6, 0]), math.pi / 8), 0.25)
    sac(p, shift(at, [0, 8, -2]), 10, F.graphite, {"stretch": 0.25})
    graft(p, polygon(8, 11, [1, 1.1]), [11.6, 12.6], at, {"color": M.base})
    missile_tips(p, shift(at, [0, 12.6, 0]), [2, 3], [6.2, 1.8])
    x = at[0]
    z = at[2]
    edge_strips(
        p.neon,
        [
            [x - 10, z + 13.6],
            [x + 10, z + 13.6],
        ],
        1,
        [9.4, 10.6],
        N,
    )
    for s in [-1, 1]:
        vein_line(p, shift(at, [s * 12, 8, -4]), shift(at, [s * 4, 4, -14]), [0, 1, 0], 1, N)


def draw_plate(p: Any, at: Vec3) -> None:
    """Draw the belly plate (FB-STORM-PETREL-03): a bony breast shell wrapped over the body's front.

    Its plates seamed, magenta veins along its shoulders, a riveted plate and bone barbs on its
    keel.
    """
    z = at[2]
    shell = SegmentedBody(z - 17, z + 18, 4, 15, -1, 16.5)
    carapace(p.flesh, shell, [F.bone, F.sinew], Placement([at[0], 0, 0]))
    for s in [-1, 1]:
        vein_line(
            p,
            [at[0] + s * 12, 12, z - 12],
            [at[0] + s * 8, 9, z + 12],
            [s * 2, 2, 0],
            1.2,
            N,
        )
    graft(p, polygon(5, 4, [1.4, 1.4]), [15.6, 17], [at[0], 0, z - 4])
    barbs(p, [at[0], 4, z + 16], {"count": 3, "spacing": 4, "size": 3, "dir": [0, -0.3, 1]})
