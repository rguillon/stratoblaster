# Copyright (c) 2026 Renaud Guillon
"""ENM-PRISM-01: the Prism, a crystalline laser platform (tier 3, ENM-35).

Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from game.config.enemy_look import ENEMY_LOOK
from game.config.enemy_prism import PRISM_CONFIG
from game.view.enemies.elite_shapes import barrel, strip
from game.view.enemies.enemy_mesh import build_enemy_model
from game.view.enemies.enemy_shapes import HULL_SECTION, SIDES, flip_x
from render.geometry.organic import plate
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
N = ENEMY_LOOK.neon
CFG = PRISM_CONFIG

# The faceted crystal hull, tail to nose: [z, half width, bottom, top]; both ends close to points.
CRYSTAL = [  # type: list[list[float]]
    [-22, 0, 0, 0],
    [-9, 9.5, 0, 7],
    [5, 9.5, 0, 7],
    [24, 0, 0, 0],
]
# The right wing's outline (x, z), swept forward to its emitter (mirrored for the left).
WING = [[7, 8], [23, 2], [25, -7], [20, -13], [7, -11]]  # type: list[list[float]]
# Two armour facets on the crystal's back (x, z).
FACET = [[0, 14], [5, 4], [5, -8], [-5, -8], [-5, 4]]  # type: list[list[float]]
# The core crystal glowing on its back: radius profile, bottom to top.
CORE = [[0, -1.6], [2.6, 1.5], [0, 5.5]]  # type: list[list[float]]
# The yaw the right wing's neon edge is laid at, along its leading edge (x +16, z -6).
EDGE_YAW = math.atan2(16, -6)


def draw_prism(p: Any) -> None:
    """Draw the hull, the core crystal, the two winged emitters and the reactors."""
    hull = p.hull
    vein = p.vein
    neon = p.neon
    hull.loft(HULL_SECTION, CRYSTAL, H.base)
    plate(hull, FACET, [7, 8.2], [H.panel, H.dark])
    # The core crystal: a lit bipyramid on its back, pulsing like a vein.
    vein.lathe(CORE, 4, N.prism, Placement([0, 8.6, -1]))
    neon.box([1, 0.5, 18], N.prism, Placement([0, 7.1, -2]))
    for s in SIDES:
        wing = WING if s > 0 else flip_x(WING)
        hull.bevel_slab(wing, [0.4, 1.6, 2.4], [0.3, 0.9], H.panel, None, H.base)
        # A neon edge along the wing's leading edge, and a facet standing on it.
        strip(neon, [s * 15, 2.6, 5], s * EDGE_YAW, [0, 17, 0.9], N.prism)
        hull.box([5, 1.8, 7], H.dark, Placement([s * 14, 2.4, -6]))
        # The emitter on the wing tip: its mouth charges as the beam comes (ENM-PRISM-04).
        tip = CFG.emitters[0 if s < 0 else 1]
        barrel(p, [tip[0], tip[2], -tip[1]], 0, [1.5, 12], "laser")
        p.reactor([s * 9, 2.4, -12], 1.1)
    p.reactor([0, 2.5, -22], 1.5)


def build_prism(scene: Any) -> Any:
    """ENM-PRISM-01: an angular crystal hull with a glowing core and two emitters on its wings.

    Faceted metal armour, within the tier 3 triangle budget (ENM-PRISM-03).
    """
    return build_enemy_model("prism", scene, N.prism, draw_prism)
