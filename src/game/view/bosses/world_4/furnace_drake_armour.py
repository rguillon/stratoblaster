# Copyright (c) 2026 Renaud Guillon
"""MB-FURNACE-DRAKE-13, 4-4: the Furnace Drake's torso and the back plating it sheds (D-254).

Logical pixels, nose +Z, Y up (towards the camera). The torso is flattened to a deck under its back
plating: a carapace drawn as a piece of its own over it, from its foot (sunk into the deck) up to
the torso's old back, with the molten seams, the soot streaks, the vents, the glands, the magma vein
and the bone spines of the back on it.
"""

from game.view.bosses.mini_boss_greebles import seam, vent
from game.view.bosses.world_4.furnace_drake_parts import (
    DRAKE_ORANGE,
    DRAKE_RED,
    SOOT,
    spike,
)
from game.view.bosses.world_4.living_forge import SKIN, glands, magma_vein
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# The torso along the centre line (loft stations: z, half width, bottom, top), as drawn whole.
TORSO = [
    [-22.0, 6.0, -1.0, 6.0],
    [-12.0, 11.0, -3.0, 10.0],
    [0.0, 13.0, -4.0, 12.0],
    [10.0, 11.0, -3.0, 10.5],
    [17.0, 7.0, -1.0, 8.0],
]
# The deck the torso is flattened to under its plating, and the plating's foot, sunk into it.
DECK = 2.2
PLATE_FOOT = 1.9
# The torso flattened to the deck (the core), and the plating's stations over it (the armour).
TORSO_DECK = [[st[0], st[1], st[2], DECK] for st in TORSO]
PLATING = [[st[0], st[1], PLATE_FOOT, st[3]] for st in TORSO]
# The plating's section (counter-clockwise seen from the nose): the hull section's upper part, from
# chine to chine over the flat back, closed flat underneath.
PLATING_SECTION = [
    [0.9, 0],
    [1, 0.18],
    [0.6, 1],
    [-0.6, 1],
    [-1, 0.18],
    [-0.9, 0],
]


def _draw_back_gear(p: Any) -> None:
    """Add what the back carries: the seams, soot, vents and glands."""
    hull = p.hull
    neon = p.neon
    for s in SIDES:
        seam(neon, [s * 9, -14], [s * 10.5, 9], [9.3, 0.5, 0.3], DRAKE_ORANGE)
        seam(neon, [s * 11.8, -6], [s * 12.4, 4], [6.5, 0.4, 0.4], DRAKE_RED)
        seam(hull, [s * 5, -18], [s * 6, 14], [11.4, 2.2, 0.3], SOOT)
        vent(hull, [s * 6.5, 10.4, 10], [3.4, 4], 3)
    glands(
        p,
        [
            [7, 11.2, 2],
            [-7, 11.2, 2],
        ],
        1.5,
        DRAKE_RED,
    )
    hull.box([8, 1, 3], SOOT, Placement([0, 11, -12]))


def draw_plating(p: Any) -> None:
    """Draw the back plating (MB-FURNACE-DRAKE-13): the armour it sheds at its transformation.

    A carapace over the flattened torso, the molten seams between its plates, soot, the vents, the
    glands, the magma vein down its back and the bone spines on it.
    """
    p.flesh.loft(PLATING_SECTION, PLATING, SKIN.base)
    _draw_back_gear(p)
    magma_vein(
        p,
        [
            [0, 10.8, -16],
            [3, 11, -4],
            [-2, 10.8, 6],
            [0, 10, 16],
        ],
        1,
        DRAKE_ORANGE,
    )
    for z in [12, -12, -18]:
        spike(p.flesh, [0, 11, z], [1.6, 4], SKIN.bone, 0.7)
