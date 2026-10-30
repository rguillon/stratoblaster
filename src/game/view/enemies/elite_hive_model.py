"""P05-R23, P16-R04: the Hive, ported from `enemies/elite-hive-model.ts`. Logical pixels, nose +Z,
Y up (towards the camera).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemies_elite import ELITE_CONFIG  # noqa: E402
from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.config.enemy_look_elite import ELITE_NEON  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.enemies.elite_shapes import WHITE, H, barrel  # noqa: E402
from game.view.enemies.enemy_shapes import around, radial  # noqa: E402
from game.view.enemies.jointed_model import build_jointed_model  # noqa: E402
from game.view.enemies.organic_parts import reactor_sac  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

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
    """The swollen flesh dome, its glowing brood cells, the vents round its rim, reactor sacs."""
    hull = p.hull
    flesh = p.flesh
    vein = p.vein
    # P16-R04: a living hive, metal only where grafted on (vents, ring, plates, nozzles).
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
        reactor_sac(p, [x, 0, -31], 2.4, NEON, F.crimson)


def ring(p: Any) -> None:
    """The launch ring with its hatch, glowing as the next Wasp comes."""
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
    """P05-R23, P16-R04: a huge swollen hive of flesh, a metal launch ring turning on its back,
    glowing honey-amber brood cells, armour plates and vents grafted on."""
    return build_jointed_model(
        "hive", scene, NEON, CFG.design, {"body": body, "ring": ring, "parts": {}}
    )
