# Copyright (c) 2026 Renaud Guillon
"""The Glacier Colossus's armour (FB-GLACIER-COLOSSUS-07, 2-4): the plating it sheds, drawn apart.

Two regions (D-254): the `flanks`, the plating of the stern deck either side of the upper deck,
and the `wings`, the ridged shell along the upper deck. Logical pixels, nose +Z, Y up (towards the
camera); the left side of the boss is at +X.
"""

from game.view.bosses.mini_boss_greebles import vent
from game.view.bosses.world_2.avalanche_frost import FROST, snow_cap
from game.view.bosses.world_2.glacier_colossus_parts import COLOSSUS_NEON
from game.view.bosses.world_2.w2_organic import (
    ICE_FLESH,
    crystals,
    glow_vein,
    shell,
    spine_row,
)
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.organic import SegmentedBody
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import TYPE_CHECKING

from game.view.enemies.enemy_mesh import EnemyParts

if TYPE_CHECKING:
    from render.geometry.outline import OutlinePoint
# __pragma__ ("noskip")


N = COLOSSUS_NEON
# Heights of the hull's deck and of the upper deck's top (`glacier_colossus_model.HULL_Y`,
# `UPPER_Y`).
DECK = 10.0
UPPER_DECK = 16.0
# The stern deck's plating: a plate lying on the deck, from just under it (the frame it leaves lies
# 0.6 over the armour's lowest point) to `PLATE_TOP`; the right one, mirrored for the left.
PLATE_Y = [DECK - 0.3, DECK, DECK + 2.2]
PLATE_TOP = PLATE_Y[2]
FLANK_PLATE = [  # type: list[list[float]]
    [31.0, -34.0],
    [58.0, -34.0],
    [44.0, -66.0],
    [21.0, -77.0],
    [10.0, -77.0],
    [10.0, -61.0],
    [24.0, -57.0],
]
# The ridged shell along the upper deck, sunk a little into it (its lowest point decides where the
# frame lies).
SHELL = SegmentedBody(-58, 6, 5, 26, UPPER_DECK - 0.2, 24)
# The heat vent on each stern plate (its centre along Z, on the right at +X).
VENT_Z = -40
VENT_X = 45


def flank_armour(p: EnemyParts) -> None:
    """Draw the stern flanks' plating (FB-GLACIER-COLOSSUS-07, region `flanks`).

    A teal plate on the stern deck either side of the upper deck, the aft heat vent, the glacier
    ice and a snow cap on it, the aft veins out from the shell to the rim. The ring emitters lie
    folded under them.
    """
    flesh = p.flesh
    for s in SIDES:
        outline: list[OutlinePoint] = [[s * q[0], q[1]] for q in FLANK_PLATE]
        flesh.bevel_slab(outline, PLATE_Y, [0, 1], ICE_FLESH.sinew, None, ICE_FLESH.teal)
        at = [s * VENT_X, PLATE_TOP - 0.2, VENT_Z]
        p.neon.box([8, 0.5, 8.5], N, Placement([at[0], at[1] + 0.1, at[2]]))
        vent(p.hull, at, [10, 10], 4)
        # Glacier ice grown through the flesh on the stern.
        crystals(flesh, [s * 38, PLATE_TOP, -57], 9, 4)
        glow_vein(p, [s * 30, PLATE_TOP + 2, -48], [s * 58, PLATE_TOP, -54], 1.3, N)
    snow_cap(
        flesh,
        [
            [48, -46],
            [56, -44],
            [54, -58],
            [48, -60],
        ],
        PLATE_TOP,
        1.2,
        FROST,
    )


def wings_armour(p: EnemyParts) -> None:
    """Draw the shell (FB-GLACIER-COLOSSUS-07, region `wings`): the ridged shell on the upper deck.

    Teal plates with dark seams along the upper deck, the row of ice spines down its ridge and the
    crystals over it. The sweepers lie folded under its flanks.
    """
    flesh = p.flesh
    shell(flesh, SHELL, ICE_FLESH.teal)
    spine_row(flesh, [0, 24, -6], [0, 22, -50], 5, 5)
    for s in SIDES:
        crystals(flesh, [s * 20, UPPER_DECK + 4, -20], 5)
