# Copyright (c) 2026 Renaud Guillon
"""The heavier veteran kinds, the Mortar and the Minelayer (specs/enemies/mortar.md, minelayer.md).

Logical pixels, nose +Z, Y up (to the camera).
"""

import math

from game.config.enemies_veteran import VETERAN_CONFIG
from game.config.enemies_veteran import VETERAN_NEON as N
from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies.enemy_mesh import build_enemy_model
from game.view.enemies.enemy_shapes import SIDES, flip_x
from game.view.enemies.organic_parts import eyes
from game.view.enemies.weapon_ports import port_radius
from render.geometry.organic import (
    SegmentedBody,
    carapace,
    organ,
)
from render.geometry.solids import Placement

# isort: split
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
F = ENEMY_LOOK.flesh
WHITE = [1, 1, 1]  # type: list[float]
QUARTER = math.pi / 2


def _mortar_girth(t: float) -> float:
    return 0.55 + 0.45 * math.sin(math.pi * t)


# ENM-MORTAR-01: the Mortar's squat, ridged shell, wider than long (tail to front).
MORTAR_SHELL = SegmentedBody(-14, 12, 3, 17.5, -2.2, 3.4, None, _mortar_girth, [False, False])
# The armour plates grafted on its front shoulders (right side).
MORTAR_PLATE = [[6, 11], [12, 8], [12.5, 4], [7, 6]]  # type: list[list[float]]


def mortar_sac(p: Any, s: float) -> None:
    """Add a side sac on side `s`, swollen with shells, a running light along it (ENM-MORTAR-03)."""
    organ(p.flesh, 3, 5, F.slate, Placement([s * 18, 0.6, -9], 0, QUARTER), 0.95)
    p.neon.box([0.8, 0.3, 4], N.mortar, Placement([s * 18.2, 3.6, -4]))


def build_mortar(scene: Any) -> Any:
    """ENM-MORTAR-02: a squat, armoured beetle with a short, wide launcher tube.

    The tube is grafted on a raised mount in its middle, with shell sacs on its flanks and
    olive-green neon (ENM-MORTAR-03), and two reactors at its back (ENM-MORTAR-05), within the
    veteran triangle budget (ENM-MORTAR-06). The barrel's mouth glows as the next shell charges
    (ENM-MORTAR-04).
    """
    muzzle_cfg = VETERAN_CONFIG.mortar.muzzles[0]
    mouth_height = muzzle_cfg[2]
    mouth = -muzzle_cfg[1]

    def draw(p: Any) -> None:
        hull = p.hull
        flesh = p.flesh
        neon = p.neon
        charge = p.charge
        muzzle = p.muzzle
        carapace(flesh, MORTAR_SHELL, [F.sinew, F.slate])
        # The raised mount: a squat drum, a cradle on it, then the barrel.
        hull.cylinder(7, 3, 8, H.panel, Placement([0, 2.4, 0]), 6)
        hull.box([6, 2.6, 9], H.dark, Placement([0, 5.4, 1.5]))
        neon.ring(6.6, 0.5, 8, N.mortar, Placement([0, 3.6, 0]))
        # The launcher tube, as wide as its port all along, which is wider than its heavy rocket
        # (WPN-07); a band round it, and the port at its mouth, its rim the charge light
        # (ENM-MORTAR-04), its rocket seen in the well once reloaded.
        missile = VETERAN_CONFIG.mortar.missile.radius
        tube = port_radius(missile)
        hull.cylinder(tube, mouth - 4, 6, H.dark, Placement([0, mouth_height, 4], 0, QUARTER))
        hull.ring(tube + 0.3, 1.5, 6, H.panel, Placement([0, mouth_height, mouth - 7], 0, QUARTER))
        band = Placement([0, mouth_height, mouth - 7.3], 0, QUARTER)
        neon.ring(tube + 0.35, 0.4, 6, N.mortar, band)
        charge.ring(
            tube + 0.35, 0.3, 6, WHITE, Placement([0, mouth_height, mouth - 5.6], 0, QUARTER)
        )
        muzzle([0, mouth_height, mouth], "missile", "forward", missile)
        eyes(p, [0, 1.6, 11.4], {"count": 2, "size": 0.6, "spacing": 3}, N.mortar)
        for s in SIDES:
            p.reactor([s * 8, 0, -14], 1.6)
            plate = MORTAR_PLATE if s == 1 else flip_x(MORTAR_PLATE)
            hull.bevel_slab(plate, [2, 2.6, 3.6], [0, 0.4], H.panel)
            mortar_sac(p, s)

    return build_enemy_model("mortar", scene, N.mortar, draw)
