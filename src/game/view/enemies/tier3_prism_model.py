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
QUARTER = math.pi / 2
N = ENEMY_LOOK.neon
CFG = PRISM_CONFIG

# The faceted crystal hull, tail to nose: [z, half width, bottom, top]; both ends close to points.
CRYSTAL = [  # type: list[list[float]]
    [-22, 0, 0, 0],
    [-9, 9.5, 0, 7],
    [5, 9.5, 0, 7],
    [24, 0, 0, 0],
]
# The right wing's outline (x, z), mirrored for the left: wide, so it shows well past the laser
# lying along it.
WING = [[7, 10], [30, 4], [33, -8], [27, -16], [7, -12]]  # type: list[list[float]]
# Two armour facets on the crystal's back (x, z).
FACET = [[0, 14], [5, 4], [5, -8], [-5, -8], [-5, 4]]  # type: list[list[float]]
# The core crystal glowing on its back: radius profile, bottom to top.
CORE = [[0, -1.6], [2.6, 1.5], [0, 5.5]]  # type: list[list[float]]
# The yaw the right wing's neon edge is laid at, along its leading edge (x +23, z -6).
EDGE_YAW = math.atan2(23, -6)
# ENM-PRISM-01: each wing's laser, almost as long as the ship: its straight barrel (radius,
# length), then the engine pod it ends in, with the reactor at its back.
LASER = [2, 25]  # type: list[float]
LASER_REACTOR = 1.6
# The engine pod's lathe profile (radius, along the pod from its back): out of the nozzle, swelling
# to its widest, then narrowing into the barrel it overlaps.
ENGINE_POD = [  # type: list[list[float]]
    [1.9, 0],
    [3, 1.4],
    [3.5, 4.5],
    [3.3, 9],
    [2.3, 13],
    [2.1, 14.5],
]
# Its length (the profile's last point; no negative index: Transcrypt does not wrap them).
ENGINE_LENGTH = ENGINE_POD[len(ENGINE_POD) - 1][1]
ENGINE_SIDES = 8
# The fin standing on the pod's back (`[z, y]` from the pod's back and its axis, side view).
ENGINE_FIN = [[2, 2.8], [9, 2.8], [5.5, 5.6], [0.5, 5.6]]  # type: list[list[float]]


def engine_pod(p: Any, at: list[float]) -> None:
    """Draw a laser's engine pod, its back at `at`: swollen, a fin on top, a light band round it.

    Its reactor at its back (ENM-PRISM-01).
    """
    along = Placement(at, 0, QUARTER)
    p.hull.lathe(ENGINE_POD, ENGINE_SIDES, H.base, along)
    widest = Placement([at[0], at[1], at[2] + 5.6], 0, QUARTER)
    p.neon.ring(3.6, 0.5, ENGINE_SIDES, N.prism, widest)
    # The fin, rolled a quarter turn to stand up: the slab's height becomes -X.
    fin = [[at[1] + q[1], at[2] + q[0]] for q in ENGINE_FIN]
    p.hull.slab(fin, [-at[0] - 0.2, -at[0] + 0.2], H.panel, Placement([0, 0, 0], 0, 0, QUARTER))
    p.reactor([at[0], at[1], at[2] - 0.2], LASER_REACTOR)


def draw_prism(p: Any) -> None:
    """Draw the hull, the core crystal, the two winged lasers and the reactors.

    A reactor at the back of each laser, none at the tail.
    """
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
        strip(neon, [s * 18.5, 2.6, 6.4], s * EDGE_YAW, [0, 22, 0.9], N.prism)
        hull.box([5, 1.8, 7], H.dark, Placement([s * 13, 2.4, -6]))
        # The laser along the wing tip, almost as long as the ship: its mouth charges as the beam
        # comes (ENM-PRISM-04), a collar along it, and its engine pod behind.
        tip = CFG.emitters[0 if s < 0 else 1]
        at = [tip[0], tip[2], -tip[1]]
        barrel(p, at, 0, LASER, "laser")
        hull.ring(
            LASER[0] + 0.35, 1.6, 6, H.panel, Placement([at[0], at[1], at[2] - 9], 0, QUARTER)
        )
        # The pod overlaps the barrel's back by a little.
        back = at[2] - 0.5 - LASER[1] - ENGINE_LENGTH + 1.2
        engine_pod(p, [at[0], at[1], back])


def build_prism(scene: Any) -> Any:
    """ENM-PRISM-01: an angular crystal hull with a glowing core and two emitters on its wings.

    Faceted metal armour, within the tier 3 triangle budget (ENM-PRISM-03).
    """
    return build_enemy_model("prism", scene, N.prism, draw_prism)
