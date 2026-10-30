"""P07-R05, P16-R05, 1-3: the Dust Devil: a desert
whirl-jelly with amber veins, a swollen fleshy bell and a slowly turning ring of sinew carrying
three clinging sand rays. Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.bosses.mini_bosses import DUST_DEVIL  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.mini_boss_shapes import WHITE, scaled  # noqa: E402
from game.view.bosses.world_1_organic_kit import (  # noqa: E402
    F,
    graft,
    polygon,
    tentacle,
    vein_line,
)
from game.view.enemies.enemy_shapes import SIDES, around  # noqa: E402
from game.view.enemies.organic_parts import eyes, reactor_sac  # noqa: E402
from render.geometry.organic import organ  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[Any]
__pragma__("noskip")

AMBER = BOSS_LOOK.neon["dust-devil"]

# The core: a gyro disc (a lathe profile), domed on top, and its ring emitter on the dome.
GYRO_DISC = [
    [0, -4],
    [14, -4],
    [18, -1],
    [18, 1.5],
    [15, 4],
    [9, 7],
    [0, 8],
]
EMITTER = [
    [3.6, 7.6],
    [2.4, 9.4],
    [0, 10],
]
# The turning ring: its collar round the bell and its rim carrying the pods (lathe profiles).
HUB = [
    [18.5, -3],
    [22, -3],
    [22.5, 0],
    [21, 1.5],
    [18.5, 1.5],
    [18.5, -3],
]
RIM = [
    [38, -2],
    [41.5, -2.5],
    [43, 0],
    [41.5, 2],
    [38, 1.5],
    [38, -2],
]
# A swept membrane fin between two spokes.
BLADE = [
    [-3, 21],
    [4, 21],
    [1, 39],
    [-6, 39],
]
# A blade pod around its centre, outwards along +Z, across along X: a swept airfoil whose two tips
# carry the muzzles (it fires both ways along the ring), and the muzzles' outlines.
POD = [
    [-14, -1],
    [-9, 5],
    [3, 8],
    [12, 4],
    [14, 0],
    [7, -6],
    [-7, -7],
]
MUZZLES = [
    [
        [-14.6, -1.2],
        [-12, 2.6],
        [-11, 0.6],
    ],
    [
        [14.6, 0],
        [12.4, 3.6],
        [11.6, 1],
    ],
]
# The amber light along a pod's back, and its canopy (a lathe profile).
POD_LIGHT = [
    [-9, 1],
    [9, 2.2],
    [9, 3.2],
    [-9, 2],
]
POD_DOME = [
    [4, 0],
    [3, 2.2],
    [0, 3],
]
POD_TOP = 3.5
# The pods are drawn this much bigger than their outlines.
POD_SCALE = 1.15


def _draw_core(p: Any) -> None:
    """The core (P16-R05): a swollen fleshy bell (the gyro disc grown over), plated ribs radiating
    across it, the amber charge gland on its crown (the ring emitter), eyes at its front, its
    reactors in sacs behind."""
    p.flesh.lathe(GYRO_DISC, 10, F.sinew, Placement(None, math.pi / 10))
    p.neon.ring(18.2, 1.2, 10, AMBER, Placement([0, -0.4, 0], math.pi / 10))
    organ(p.flesh, 9, 8, F.crimson, Placement([0, 4, 0]), 0.25)
    for a in around(8):
        x = math.sin(a)
        z = math.cos(a)
        tentacle(p, [x * 5, 8, z * 5], [x * 18, 1.6, z * 18], [0, 2.2, 0], [1.1, 0.6], F.bone, 3)
        if abs(z) < 0.95:  # noqa: PLR2004
            graft(
                p,
                polygon(4, 2.6, [0.8, 1.4]),
                [4.4, 5.6],
                [x * 13, 0, z * 13],
                {"yaw": a},
            )
    for s in SIDES:
        vein_line(p, [s * 4, 7.5, -3], [s * 15, 3, -10], [0, 1.5, 0], 0.9, AMBER)
        reactor_sac(p, [s * 6, 4, -23], 2.6, AMBER)
        tentacle(p, [s * 5, 3, -14], [s * 6, 4, -21], [0, 1, 0], [3, 2.6], F.crimson, 5)
    eyes(p, [0, 4.5, 16], {"count": 3, "size": 1, "spacing": 3}, AMBER)
    graft(p, polygon(5, 4, [1.2, 0.8]), [3, 4.4], [0, 0, 13])
    # Brightens as the core's next volley charges; its bullets leave from its top.
    p.charge.lathe(EMITTER, 6, WHITE, None)
    p.muzzle([0, 10, 0], None)


def _draw_ring(p: Any) -> None:
    """The turning ring (P07-R05, P16-R05): a sinew collar round the bell, a fleshy rim, three
    tentacle spokes out to the pods and membrane fins between them."""
    p.flesh.lathe(HUB, 10, F.purple, None, False)
    p.flesh.lathe(RIM, 15, F.sinew, None, False)
    p.neon.ring(43.1, 0.8, 15, AMBER, Placement([0, -0.4, 0]))
    for a in around(3):
        x = math.sin(a)
        z = math.cos(a)
        tentacle(p, [x * 20, 0, z * 20], [x * 39, 0, z * 39], [0, 1.5, 0], [2.2, 1.6], F.crimson, 4)
        p.flesh.bevel_slab(
            BLADE,
            [-0.6, 0, 0.6],
            [0.4, 0.6],
            F.membrane,
            Placement(None, a + math.pi / 3),
        )
        fin = a + math.pi / 3
        tentacle(
            p,
            [math.sin(fin) * 21, 0.6, math.cos(fin) * 21],
            [math.sin(fin) * 38, 0.6, math.cos(fin) * 38],
            [0, 0, 0],
            [0.6, 0.3],
            F.bone,
            3,
        )
        vein_line(p, [x * 21, 1.8, z * 21], [x * 38, 1.6, z * 38], [0, 0.8, 0], 0.7, AMBER)


def _blade_pod(p: Any, at: Vec3) -> None:
    """A blade pod on the ring (P07-R05, P16-R05): a sand ray clinging to the rim, its wide fleshy
    wings plated at the front, a bone barb at each wing tip carrying a muzzle."""
    yaw = math.atan2(at[0], at[2])
    place = Placement(at, yaw)
    p.flesh.bevel_slab(
        scaled(POD, POD_SCALE),
        [-3, 0, POD_TOP - 1],
        [1, 2.4],
        F.sinew,
        place,
        F.crimson,
    )
    organ(p.flesh, 5, 6, F.crimson, Placement([at[0], POD_TOP - 2.5, at[2]]), 0.45)
    p.vein.slab(POD_LIGHT, [POD_TOP - 0.6, POD_TOP - 0.3], AMBER, place)
    p.neon.lathe(POD_DOME, 5, AMBER, Placement([at[0], POD_TOP + 1.6, at[2]]))
    for muzzle in MUZZLES:
        p.charge.slab(scaled(muzzle, POD_SCALE), [-1.6, 2.2], WHITE, place)
    graft(p, scaled(POD[1:4], 0.8, 0, 0), [POD_TOP - 1.2, POD_TOP], at, {"yaw": yaw})

    def put(x: float, z: float) -> Vec3:
        return [
            at[0] + x * math.cos(yaw) + z * math.sin(yaw),
            POD_TOP,
            at[2] - x * math.sin(yaw) + z * math.cos(yaw),
        ]

    # Its bullets leave from the tips, both ways along the ring.
    for side in [-1, 1]:
        tip = put(side * 14.6 * POD_SCALE, -1.2 * POD_SCALE if side < 0 else 0)
        p.muzzle([tip[0], 0.3, tip[2]], None)


def build_dust_devil(scene: Any) -> Any:
    """P07-R05, P16-R05: the Dust Devil, a desert whirl-jelly with amber veins: a swollen fleshy
    bell, and a slowly turning ring of sinew carrying three clinging sand rays."""
    return build_boss_model(
        DUST_DEVIL,
        scene,
        AMBER,
        {
            "core": _draw_core,
            "ring": _draw_ring,
            "parts": {"blade-1": _blade_pod, "blade-2": _blade_pod, "blade-3": _blade_pod},
        },
    )
