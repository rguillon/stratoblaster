# Copyright (c) 2026 Renaud Guillon
"""MB-MAGMA-SALAMANDER-13, 4-3: the Magma Salamander's scale plates and its shed plating (D-254).

Logical pixels, nose +Z, Y up (towards the camera). The body's overlapping armour plates lie over
its belly; the three over its back (`SHED_PLATES`) are the back plating it sheds at its
transformation: shells drawn as pieces of their own over the belly, which is flattened under them,
with the molten seams between them, the flank lights, the vent, a gland and the spine's vein on
them. The two plates over its neck stay on the body.
"""

from game.view.bosses.mini_boss_greebles import vent
from game.view.bosses.world_4.living_forge import SKIN, glands, magma_vein
from game.view.bosses.world_4.magma_salamander_parts import (
    MOLTEN,
    SALAMANDER_NEON,
    SCORCH,
    molten_seam,
)
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# The armour plates over the body, back to front: from and to (z), half width, top.
PLATES = [
    [-26.0, -18.0, 8.0, 8.0],
    [-17.0, -4.0, 13.5, 11.0],
    [-2.0, 10.0, 14.5, 12.0],
    [12.0, 24.0, 13.0, 11.5],
    [26.0, 35.0, 10.0, 10.0],
]
# How many plates, from the tail, are the back plating it sheds (MB-MAGMA-SALAMANDER-13).
SHED_PLATES = 3
# The shed shells' flat underside, and the belly's flattened top under them (sunk into them).
SHELL_FOOT = 2.8
BELLY_FLAT = SHELL_FOOT + 0.4
# A shell's section (counter-clockwise seen from the nose): the fighter section's upper part, from
# chine to chine over the ridge, closed flat underneath.
SHELL_SECTION = [
    [1, 0],
    [0.6, 0.43],
    [0.3, 0.79],
    [0, 1],
    [-0.3, 0.79],
    [-0.6, 0.43],
    [-1, 0],
]


def plate_colour(i: int) -> Any:
    """Return the shade of plate `i`: the plates alternate dark and sinew."""
    return SKIN.dark if i % 2 == 0 else SKIN.panel


def plate_stations(i: int, foot: Any = None) -> list[Any]:
    """Return the loft stations of plate `i`: a ring swelling from its back edge to its front one.

    With `foot`, the plate's bottom is flat at that height (a shed shell); else it reaches down
    around the belly.
    """
    entry = PLATES[i]
    z0 = entry[0]
    z1 = entry[1]
    half = entry[2]
    top = entry[3]
    low = [1, 0.5, 0.5, 1] if foot == None else [foot, foot, foot, foot]
    return [
        [z0, half * 0.85, low[0], top - 1.2],
        [z0 + 2, half, low[1], top],
        [z1 - 2, half, low[2], top],
        [z1, half * 0.88, low[3], top - 1],
    ]


def plate_seam(neon: Any, i: int) -> None:
    """Add the molten seam glowing between plate `i` and the one behind it."""
    entry = PLATES[i]
    molten_seam(neon, [entry[2] * 1.5, entry[3] - 1.6, entry[0] - 0.5])


def draw_plating(p: Any) -> None:
    """Draw the back plating (MB-MAGMA-SALAMANDER-13): the armour it sheds at its transformation.

    The three scale plates over its back as shells on the flattened belly, the molten seams between
    them, the orange lights along their flanks, a vent, a gland and the spine's magma vein on them.
    """
    hull = p.hull
    neon = p.neon
    for i in range(SHED_PLATES):
        p.flesh.loft(SHELL_SECTION, plate_stations(i, SHELL_FOOT), plate_colour(i))
        if i > 0:
            plate_seam(neon, i)
    for s in SIDES:
        neon.box([0.6, 0.5, 26], SALAMANDER_NEON, Placement([s * 13.6, 6.2, -4], s * 0.04))
    hull.box([4, 0.5, 6], SCORCH, Placement([6, 11.6, 6]))
    vent(hull, [-6, 12.2, 3], [5, 6], 3)
    glands(p, [[4, 12, -11]], 1.6, MOLTEN)
    magma_vein(
        p,
        [
            [0, 9, -20],
            [0, 11, -8],
            [0, 12, 8],
        ],
        1,
    )
