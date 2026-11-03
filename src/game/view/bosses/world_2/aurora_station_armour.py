# Copyright (c) 2026 Renaud Guillon
"""The Aurora Station's armour (FB-AURORA-STATION-07, 2-3): the plating it sheds, drawn apart.

Two regions (D-254): the `flanks`, its two frilled fins behind the spine (the old radiator wings),
and the `bell`, the cap of its bell (the top of the hub's drum, the rime on it, the veins out from
the collar and the crystals). Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from game.view.bosses.mini_boss_greebles import seam
from game.view.bosses.world_2.aurora_station_parts import AURORA_GREEN
from game.view.bosses.world_2.w2_organic import ICE_FLESH, crystals, glow_vein, sinew
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import TYPE_CHECKING

from game.view.enemies.enemy_mesh import EnemyParts

if TYPE_CHECKING:
    from render.geometry.outline import OutlinePoint
# __pragma__ ("noskip")


# An eighth of a turn: the octagons' flat faces to the front.
EIGHTH = math.pi / 8
# The bell's drum (a lathe profile): the core keeps it up to `DRUM_TOP`; its cap, the armour, goes
# on from there (sunk `CAP_SINK` into the drum) up to `BELL_TOP`.
DRUM_TOP = 3.0
CAP_SINK = 0.2
BELL_TOP = 7.0
BELL_CAP = [  # type: list[list[float]]
    [25.0, DRUM_TOP - CAP_SINK],
    [25.0, DRUM_TOP],
    [21.0, BELL_TOP],
    [0.0, BELL_TOP],
]
# The collar grafted round the crown: its radius, where the veins start (at its foot on the cap).
COLLAR_RADIUS = 11.0
# A radiator wing behind the truss (the right one; mirrored for the left): a frilled fin.
RADIATOR = [  # type: list[list[float]]
    [20.0, -24.0],
    [76.0, -26.0],
    [84.0, -32.0],
    [84.0, -46.0],
    [20.0, -48.0],
]
# The fin's heights: its membrane from `FIN_BOTTOM` to `FIN_TOP`.
FIN_BOTTOM = -0.6
FIN_TOP = 1.0


def bell_armour(p: EnemyParts) -> None:
    """Draw the bell's cap (FB-AURORA-STATION-07, region `bell`): the plating over the drum.

    The top of the drum from `DRUM_TOP` up to `BELL_TOP`, rimed, the six green veins from the
    collar's foot out to its rim and the crystals on it. The racks lie folded under it, at its
    front.
    """
    flesh = p.flesh
    flesh.lathe(BELL_CAP, 8, ICE_FLESH.graphite, Placement(None, EIGHTH))
    flesh.cylinder(20.5, 0.3, 8, ICE_FLESH.rime, Placement([0.0, BELL_TOP, 0.0], EIGHTH))
    for a in [0, 1, 2, 3, 4, 5]:
        yaw = a * math.pi / 3 + 0.3
        glow_vein(
            p,
            [math.sin(yaw) * COLLAR_RADIUS, BELL_TOP + 0.4, math.cos(yaw) * COLLAR_RADIUS],
            [math.sin(yaw) * 23.0, DRUM_TOP, math.cos(yaw) * 23.0],
            1.0,
            AURORA_GREEN,
        )
    for s in SIDES:
        crystals(flesh, [s * 16.0, BELL_TOP - 0.5, -8.0], 3.5)


def flank_armour(p: EnemyParts) -> None:
    """Draw the fins (FB-AURORA-STATION-07, region `flanks`): the plating of both rear flanks.

    Frilled membrane fins on bone rays, a green edge light on each, where the radiators were. The
    lances lie folded under them.
    """
    flesh = p.flesh
    for s in SIDES:
        # FB-AURORA-STATION-02: frilled membrane fins on bone rays, where the radiators were.
        outline: list[OutlinePoint] = [[s * p0[0], p0[1]] for p0 in RADIATOR]
        flesh.bevel_slab(
            outline,
            [FIN_BOTTOM, 0.0, FIN_TOP],
            [0.4, 0.6],
            ICE_FLESH.membrane,
            None,
            ICE_FLESH.teal,
        )
        for x in [30.0, 42.0, 54.0, 66.0, 78.0]:
            sinew(
                flesh,
                [s * (x - 4.0), FIN_TOP, -25.0],
                [s * x, FIN_TOP, -46.5],
                0.6,
                ICE_FLESH.bone,
                [0.0, 0.4, 0.0],
            )
        seam(p.neon, [s * 84.2, -32.0], [s * 84.2, -46.0], [0.2, 0.5, 0.6], AURORA_GREEN)
