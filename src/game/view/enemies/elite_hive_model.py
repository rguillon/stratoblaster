# Copyright (c) 2026 Renaud Guillon
"""The Hive (specs/enemies/hive.md).

Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from game.config.enemies_elite import ELITE_CONFIG
from game.config.enemy_look import ENEMY_LOOK
from game.config.enemy_look_elite import ELITE_NEON
from game.view.bosses.boss_limbs import boss_point
from game.view.enemies.elite_shapes import WHITE, H, barrel
from game.view.enemies.enemy_shapes import around, radial
from game.view.enemies.jointed_model import build_jointed_model
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.solids import Placement

# isort: split
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


CFG = ELITE_CONFIG.hive
NEON = ELITE_NEON.hive
F = ENEMY_LOOK.flesh

# The rounded hull, a lathe profile from its belly up to its back under the ring.
DOME = [
    [20, -4.5],
    [30, -2],
    [32, 0.5],
    [30, 3.5],
    [24, 6.5],
    [16, 8.5],
    [0, 8.8],
]
# The honey-amber cells on the dome's shoulder: their distance out, height and tilt.
CELLS = {"count": 10, "radius": 26.8, "y": 4.9, "tilt": 0.46, "size": 2.6}
# An armour plate on the dome's back, out along +Z (turned round it).
ARMOUR = [
    [-4, 17],
    [4, 17],
    [5.5, 23],
    [-5.5, 23],
]
# The launch ring on its back (a lathe profile, closed), turning with the enemy's spin.
RING = [
    [12, 8.4],
    [16.5, 8.4],
    [16, 10.6],
    [12.5, 10.6],
    [12, 8.4],
]


def body(p: Any) -> None:
    """Add the swollen flesh dome.

    Its glowing brood cells (ENM-HIVE-03), the vents round its rim (ENM-HIVE-04), reactor sacs
    (ENM-HIVE-06).
    """
    hull = p.hull
    flesh = p.flesh
    vein = p.vein
    # ENM-HIVE-02: a living hive, metal only where grafted on (vents, ring, plates, nozzles).
    flesh.lathe(DOME, 12, F.sinew)
    # The brood cells: hexagons on the shoulder, tilted with it, pulsing.
    for a in around(int(CELLS["count"])):
        place = Placement(radial(a, CELLS["radius"], CELLS["y"]), a, CELLS["tilt"])
        vein.cylinder(CELLS["size"], 0.6, 5, NEON, place)
    # Armour plates between the cells and the ring.
    for a in around(3):
        hull.bevel_slab(
            ARMOUR, [8.4, 8.4, 9.4], [0, 0.8], H.panel, Placement(None, a + math.pi / 3)
        )
    # The vents its rings of bullets leave from, pointing out.
    for k, m in enumerate(CFG.ringMuzzles):
        barrel(
            p,
            boss_point(m[0], m[1], m[2]),
            (-2 * math.pi * k) / CFG.ringCount,
            [1.2, 2.5],
            "ring",
        )
    for x in [-9, 9]:
        reactor_sac(p, [x, 0, -31], 2.4, NEON, F.slate)


def ring(p: Any) -> None:
    """Add the launch ring with its hatch (ENM-HIVE-04).

    Glowing as the next Wasp comes (ENM-HIVE-05).
    """
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    hull.lathe(RING, 12, H.panel, None, False)
    for a in around(6):
        neon.box([1, 0.4, 3], NEON, Placement(radial(a + math.pi / 6, 14.2, 10.6), a + math.pi / 6))
    hatch = boss_point(CFG.port[0], CFG.port[1], CFG.port[2])
    hull.box([6, 2.2, 5], H.dark, Placement([hatch[0], 9.2, hatch[2]]))
    charge.box([4.2, 0.4, 3.2], WHITE, Placement([hatch[0], 11.4, hatch[2]]))
    muzzle(hatch, "launch")


def build_hive(scene: Any) -> Any:
    """ENM-HIVE-01: a huge swollen hive of flesh.

    A metal launch ring turning on its back, glowing honey-amber brood cells, armour plates and
    vents grafted on, within the elite triangle budget (ENM-HIVE-07).
    """
    return build_jointed_model(
        "hive", scene, NEON, CFG.design, {"body": body, "ring": ring, "parts": {}}
    )
