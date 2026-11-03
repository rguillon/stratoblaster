# Copyright (c) 2026 Renaud Guillon
"""ENM-BROODMOTHER-01: the Broodmother, a brood carrier, Cyber-Organic (tier 3, ENM-35).

Logical pixels, nose +Z, Y up (towards the camera).
"""

from game.config.enemy_broodmother import BROODMOTHER_CONFIG
from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies.enemy_mesh import build_enemy_model
from game.view.enemies.enemy_shapes import LOBE_SECTION, SIDES, flip_x
from game.view.enemies.organic_parts import eyes, reactor_sac
from render.geometry.organic import (
    SegmentedBody,
    carapace,
    curve,
    organ,
    plate,
    segmented_body,
    vein,
)
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
F = ENEMY_LOOK.flesh
N = ENEMY_LOOK.neon
CFG = BROODMOTHER_CONFIG
WHITE = [1, 1, 1]  # type: list[float]

# ENM-BROODMOTHER-01: the swollen brood body, tail to nose, and the ridged shell over its back.
BODY = SegmentedBody(-30, 28, 4, 17, -4, 10)
SHELL = SegmentedBody(-24, 20, 3, 12.5, 4, 13, None, None, [False, False])
# The armour plates on its back, right half (the middle one is whole): outlines (x, z).
PLATE_MIDDLE = [[-5, 8], [5, 8], [6, -2], [-6, -2]]  # type: list[list[float]]
PLATE_SIDE = [[4, 14], [11, 10], [11, 2], [4, 4]]  # type: list[list[float]]
PLATE_HEIGHT = [11.5, 13]  # type: list[float]
# The egg sacs along each flank: along Z, out from the centre, up.
EGG_ZS = [-14, -2, 10]  # type: list[float]
EGG_OUT = 15.5
EGG_UP = 2.5
EGG_RADIUS = 3
# The hatch on its belly, where `CFG.port` puts it: the collar's size and how low it hangs.
HATCH = [10, 3, 5]  # type: list[float]
HATCH_DROP = -3.6


def hatch(p: Any) -> None:
    """Add the hatch on its belly: a dark collar with a mouth glowing as a launch comes."""
    z = -CFG.port[1]
    p.hull.box(HATCH, H.dark, Placement([0, HATCH_DROP, z]), H.panel)
    p.charge.box([6, 1.2, 0.4], WHITE, Placement([0, HATCH_DROP + 0.8, z + HATCH[2] / 2 + 0.1]))
    p.muzzle([0, HATCH_DROP, z], "launch")


def egg_sacs(p: Any) -> None:
    """Add the egg sacs: a metal cradle on each flank with an egg glowing as a launch nears."""
    for s in SIDES:
        for z in EGG_ZS:
            at = [s * EGG_OUT, EGG_UP, z]
            p.hull.cylinder(EGG_RADIUS + 1.1, 1.6, 4, H.panel, Placement([at[0], at[1] - 1, z]))
            organ(p.charge, EGG_RADIUS, 4, WHITE, Placement(at), 1.15)


def draw_broodmother(p: Any) -> None:
    """Draw the brood body, its armour, egg sacs, hatch and reactors."""
    flesh = p.flesh
    hull = p.hull
    segmented_body(flesh, BODY, F.slate, None, LOBE_SECTION)
    carapace(flesh, SHELL, [F.sinew, F.slate])
    plate(hull, PLATE_MIDDLE, PLATE_HEIGHT, [H.panel, H.dark])
    for s in SIDES:
        side = PLATE_SIDE if s > 0 else flip_x(PLATE_SIDE)
        hull.bevel_slab(side, [PLATE_HEIGHT[0], PLATE_HEIGHT[0], PLATE_HEIGHT[1]], [0, 0.8], H.base)
        vein(p.vein, curve([s * 4, 11, -22], [s * 5, 11.5, 16], [s * 2, 1, 0], 3), 1, N.broodmother)
        reactor_sac(p, [s * 8, 1, -30.5], 2.2, N.broodmother)
    eyes(p, [0, 8.5, 21], {"count": 2, "size": 0.7, "spacing": 3.4}, N.broodmother)
    egg_sacs(p)
    hatch(p)


def build_broodmother(scene: Any) -> Any:
    """ENM-BROODMOTHER-01: a huge, swollen brood body under armour plates.

    Egg sacs glow along its flanks as the next launch nears and a hatch hangs on its belly, within
    the tier 3 triangle budget (ENM-BROODMOTHER-05).
    """
    return build_enemy_model("broodmother", scene, N.broodmother, draw_broodmother)
