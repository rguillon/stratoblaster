# Copyright (c) 2026 Renaud Guillon
"""ENM-SWEEPER-01: the Sweeper, Cyber-Organic (ENM-35), a tier 2 kind.

A flat disc platform with a long emitter barrel. Logical pixels, nose +Z (the barrel), Y up
(towards the camera). The whole model turns with the enemy's heading, so the barrel swings with the
beam.
"""

import math

from game.config.enemy_look import ENEMY_LOOK
from game.config.enemy_sweeper import SWEEPER_CONFIG
from game.view.enemies.enemy_mesh import build_enemy_model
from game.view.enemies.enemy_shapes import around, radial
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
F = ENEMY_LOOK.flesh
N = ENEMY_LOOK.neon
WHITE = [1, 1, 1]  # type: list[float]
QUARTER = math.pi / 2

# ENM-SWEEPER-01: the disc's profile (radius, height), from its belly up to its top.
SWEEPER_DISC = [[0, -1], [20, -1], [21, 1.5], [17, 4], [8, 5.5], [0, 5.5]]  # type: list[list[float]]
DISC_SIDES = 10
# The turret hub on top of the disc, and the height of the barrel's axis above the disc.
HUB_HEIGHT = 3
BARREL_HEIGHT = 7
# A glowing bead of flesh (8 triangles) on the disc.
BEAD = [[0, -0.6], [1.4, 0], [0, 0.8]]  # type: list[list[float]]


def build_sweeper(scene: Any) -> Any:
    """ENM-SWEEPER-01: a hovering laser platform, the laser of tier 2.

    A flat armoured disc over a flesh belly, a turret hub and a long emitter barrel (ENM-SWEEPER-02)
    with a charge light at its tip that brightens through the warning (ENM-SWEEPER-03), three
    reactors at the rear (ENM-SWEEPER-04), lime neon (ENM-SWEEPER-04).
    """
    barrel = SWEEPER_CONFIG.barrelOffset

    def draw(p: Any) -> None:
        hull = p.hull
        neon = p.neon
        charge = p.charge
        hull.lathe(SWEEPER_DISC, DISC_SIDES, H.base, None)
        neon.ring(19.7, 0.8, DISC_SIDES, N.sweeper, Placement([0, 1.6, 0]))
        hull.cylinder(7, HUB_HEIGHT, 8, H.panel, Placement([0, 5.5, 0]), 5)
        hull.cylinder(2.2, barrel, 6, H.panel, Placement([0, BARREL_HEIGHT, 0], 0, QUARTER), 1.6)
        neon.box([0.7, 0.5, 14], N.sweeper, Placement([0, BARREL_HEIGHT + 1.7, barrel / 2 + 1]))
        # Brightens through the warning (its `charge`), full while the laser fires.
        charge.cylinder(1.9, 1.8, 6, WHITE, Placement([0, BARREL_HEIGHT, barrel], 0, QUARTER), 1.4)
        p.muzzle([0, BARREL_HEIGHT, barrel + 1.8], "laser")
        for a in around(4):
            p.vein.lathe(BEAD, 4, N.sweeper, Placement(radial(a + math.pi / 4, 12, 4.9)))
        reactor_sac(p, [0, 1, -20.5], 1.6, N.sweeper, F.sinew, 3)
        for s in [-1, 1]:
            p.reactor([s * 10, 1, -18.5], 1.2)

    return build_enemy_model("sweeper", scene, N.sweeper, draw)
