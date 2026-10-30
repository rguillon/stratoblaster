"""P05-R20, P16-R04: the Orbiter Logical pixels,
nose +Z, Y up (towards the camera).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemies_elite import ELITE_CONFIG  # noqa: E402
from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.config.enemy_look_elite import ELITE_NEON  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.enemies.elite_shapes import WHITE, H, ahead, barrel  # noqa: E402
from game.view.enemies.jointed_model import build_jointed_model  # noqa: E402
from render.geometry.organic import SegmentedBody, curve, segmented_body  # noqa: E402
from render.geometry.organic import vein as vein_tube
from render.geometry.solids import Placement  # noqa: E402

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

CFG = ELITE_CONFIG.orbiter
NEON = ELITE_NEON.orbiter
F = ENEMY_LOOK.flesh

# The core: a sphere squashed a little (it flies low), as a lathe profile, bottom to top.
SQUASH = 0.72


def _core_point(deg: float) -> list[float]:
    a = (deg * math.pi) / 180
    return [CFG.coreRadius * math.cos(a), CFG.coreRadius * SQUASH * math.sin(a)]


CORE = [_core_point(deg) for deg in [-90, -60, -30, 0, 30, 60, 90]]
# A drone's flesh pod around its centre, along +Z, under its shell.
POD = SegmentedBody(-3.6, 3.4, 2, 3.8, -1.8, 1.4)
# A drone's armour shell around its centre, its nose (+Z) out from the core.
DRONE = [  # type: list[list[float]]
    [-3.6, -3.4],
    [3.6, -3.4],
    [4.4, 0.8],
    [2, 3.6],
    [-2, 3.6],
    [-4.4, 0.8],
]


def _vein_point(a: float, r: float, y: float) -> list[float]:
    return [math.sin(a) * r, y, math.cos(a) * r]


def body(p: Any) -> None:
    """The core: a flesh heart in metal bands, its glowing equator, veins and its pole light."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    vein = p.vein
    charge = p.charge
    muzzle = p.muzzle
    flesh.lathe(CORE, 12, F.purple)
    # P16-R04: armour bands above and below the equator, metal grafted on the heart.
    for y in [-5.2, 3.6]:
        hull.ring(CFG.coreRadius * 0.86, 1.6, 12, H.dark, Placement([0, y, 0]))
    neon.ring(CFG.coreRadius + 0.3, 1.8, 12, NEON, Placement([0, -0.9, 0]))
    # Veins over its top, from the pole down to the upper band.
    top = CFG.coreRadius * SQUASH
    for k in range(4):
        a = (k * math.pi) / 2 + math.pi / 4
        vein_tube(
            vein,
            curve(
                _vein_point(a, 2.5, top),
                _vein_point(a, CFG.coreRadius * 0.82, 5.2),
                [0, 1.5, 0],
                2,
            ),
            0.9,
            NEON,
        )
    # A light on top, brightening as the next ring of bullets comes.
    pole = [[0, 0], [3.2, 0.4], [0, 1.6]]
    charge.lathe(pole, 8, WHITE, Placement([0, top - 0.4, 0]))
    for m in CFG.ringMuzzles:
        muzzle(boss_point(m[0], m[1], m[2]), "ring")


def drone(spec: Any) -> Any:
    """A drone: a flesh pod under a metal shell, an eye slit and a gun on its nose."""
    at = boss_point(spec.centre[0], spec.centre[1], 0)
    yaw = spec.aim
    tip = boss_point(spec.muzzle[0], spec.muzzle[1], spec.muzzle[2])

    def draw(p: Any) -> None:
        hull = p.hull
        neon = p.neon
        vein = p.vein
        segmented_body(p.flesh, POD, F.crimson, Placement(at, yaw))
        hull.bevel_slab(DRONE, [0.6, 1.2, 2.6], [0.2, 1], H.panel, Placement(at, yaw), H.base)
        eye = ahead(at, yaw, -0.6)
        neon.box([4.6, 0.5, 1], NEON, Placement([eye[0], 2.6, eye[2]], yaw))
        # A gland at its back, pulsing.
        gland = ahead(at, yaw, -3.2)
        vein.box([1.4, 0.6, 1.2], NEON, Placement([gland[0], 1.6, gland[2]], yaw))
        barrel(p, tip, yaw, [0.8, 2.2])

    return draw


def build_orbiter(scene: Any) -> Any:
    """P05-R20, P16-R04: a flesh heart in armour bands with a white-gold equator, three armoured
    drone pods orbiting it."""
    parts = {}
    for d in CFG.drones:
        parts[d.id] = drone(d)
    return build_jointed_model("orbiter", scene, NEON, CFG.design, {"body": body, "parts": parts})
