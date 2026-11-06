# Copyright (c) 2026 Renaud Guillon
"""MB-DUST-DEVIL-01 to MB-DUST-DEVIL-04, 1-3: the Dust Devil.

A desert whirl-jelly with amber veins, a swollen fleshy bell and a slowly turning ring of sinew
carrying three clinging sand rays. Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.boss_guns import GUN_SHAPE
from game.config.bosses.mini_bosses import DUST_DEVIL
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.mini_boss_shapes import scaled
from game.view.bosses.world_1_organic_kit import (
    F,
    graft,
    polygon,
    tentacle,
    vein_line,
)
from game.view.enemies.enemy_shapes import SIDES, around
from game.view.enemies.organic_parts import eyes, reactor_sac
from render.geometry.organic import organ
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


AMBER = BOSS_LOOK.neon["dust-devil"]

# The core: a gyro disc (a lathe profile) flattened to `DISC_TOP`, a hub standing from its middle
# that carries the ring emitter; its domed cap is the plating it sheds (MB-DUST-DEVIL-05): a shell
# of revolution (a closed lathe profile) round the hub, from `CAP_RIM` at its rim (sunk into the
# disc) up to the hub's top.
DISC_TOP = 2.2
CAP_RIM = 2.0
GYRO_DISC = [
    [0, -4],
    [14, -4],
    [18, -1],
    [18, 1.5],
    [16, DISC_TOP],
    [4.6, DISC_TOP],
    [3.8, 7.6],
    [0, 7.8],
]
CAP = [
    [15.2, CAP_RIM],
    [15.4, 2.8],
    [13, 3.8],
    [10, 5.5],
    [7, 6.9],
    [4.4, 7.7],
    [4.4, 6.7],
    [7, 6.0],
    [10, 4.5],
    [13, 2.9],
    [15.2, CAP_RIM],
]
# Radius of the cap, and of the hub it leaves round (the `back` region's two half-rings).
CAP_RADIUS = 15.2
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
# A blade pod around its centre, outwards along +Z, across along X: a swept airfoil.
POD = [
    [-14, -1],
    [-9, 5],
    [3, 8],
    [12, 4],
    [14, 0],
    [7, -6],
    [-7, -7],
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
# The top of a pod's rotor's hub, its canopy on it (`DUST_DEVIL.mounts`, BOSS-58).
POD_ROTOR = DUST_DEVIL.mounts[0]
POD_ROTOR_TOP = POD_ROTOR.height + POD_ROTOR.size * GUN_SHAPE.domeHeight
# The pods are drawn this much bigger than their outlines.
POD_SCALE = 1.15


def _draw_core(p: Any) -> None:
    """Draw the core (MB-DUST-DEVIL-02): a swollen fleshy bell (the gyro disc grown over).

    The disc flattened under its cap (the plating it sheds, `_draw_plating`), the hub on its middle
    carrying its stacked guns (its rotor under its turret: its mounts, BOSS-58), eyes at its front,
    its reactors in sacs behind.
    """
    p.flesh.lathe(GYRO_DISC, 10, F.sinew, Placement(None, math.pi / 10))
    p.neon.ring(18.2, 1.2, 10, AMBER, Placement([0, -0.4, 0], math.pi / 10))
    for s in SIDES:
        reactor_sac(p, [s * 6, 4, -23], 2.6, AMBER)
        tentacle(p, [s * 5, 3, -14], [s * 6, 4, -21], [0, 1, 0], [3, 2.6], F.slate, 5)
    eyes(p, [0, DISC_TOP + 0.3, 16.6], {"count": 3, "size": 1, "spacing": 3}, AMBER)


def _draw_plating(p: Any) -> None:
    """Draw the bell's cap (MB-DUST-DEVIL-05): the armour it sheds at its transformation.

    A domed shell over the flattened disc, round the hub, the bone ribs radiating down it to its
    rim, the plated ribs and the nose plate grafted on it, a vein down each side.
    """
    p.flesh.lathe(CAP, 10, F.sinew, Placement(None, math.pi / 10), False)
    for a in around(8):
        x = math.sin(a)
        z = math.cos(a)
        tentacle(
            p, [x * 5, 7.6, z * 5], [x * 14.8, 3.1, z * 14.8], [0, 1.6, 0], [1.1, 0.6], F.bone, 3
        )
        if abs(z) < 0.95:
            graft(
                p,
                polygon(4, 2.6, [0.8, 1.4]),
                [3.9, 5.1],
                [x * 13, 0, z * 13],
                {"yaw": a},
            )
    for s in SIDES:
        vein_line(p, [s * 4, 7.5, -3], [s * 12, 3.4, -8.5], [0, 1.5, 0], 0.9, AMBER)
    graft(p, polygon(5, 4, [1.2, 0.8]), [3.9, 5.1], [0, 0, 13])


def _draw_ring(p: Any) -> None:
    """Draw the turning ring (MB-DUST-DEVIL-02): a sinew collar round the bell, a fleshy rim.

    Three tentacle spokes out to the pods and membrane fins between them.
    """
    p.flesh.lathe(HUB, 10, F.graphite, None, False)
    p.flesh.lathe(RIM, 15, F.sinew, None, False)
    p.neon.ring(43.1, 0.8, 15, AMBER, Placement([0, -0.4, 0]))
    for a in around(3):
        x = math.sin(a)
        z = math.cos(a)
        tentacle(p, [x * 20, 0, z * 20], [x * 39, 0, z * 39], [0, 1.5, 0], [2.2, 1.6], F.slate, 4)
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
    """Add a blade pod on the ring (MB-DUST-DEVIL-03): a sand ray clinging to the rim.

    Its wide fleshy wings plated at the front, its rotor on its back firing both ways along the
    ring (its mount, BOSS-58).
    """
    yaw = math.atan2(at[0], at[2])
    place = Placement(at, yaw)
    p.flesh.bevel_slab(
        scaled(POD, POD_SCALE),
        [-3, 0, POD_TOP - 1],
        [1, 2.4],
        F.sinew,
        place,
        F.slate,
    )
    organ(p.flesh, 5, 6, F.slate, Placement([at[0], POD_TOP - 2.5, at[2]]), 0.45)
    p.vein.slab(POD_LIGHT, [POD_TOP - 0.6, POD_TOP - 0.3], AMBER, place)
    # Its canopy crowns its rotor's hub (its mount, BOSS-58).
    p.neon.lathe(scaled(POD_DOME, 0.75), 5, AMBER, Placement([at[0], POD_ROTOR_TOP, at[2]]))
    graft(p, scaled(POD[1:4], 0.8, 0, 0), [POD_TOP - 1.2, POD_TOP], at, {"yaw": yaw})


def build_dust_devil(scene: Any) -> Any:
    """MB-DUST-DEVIL-01, MB-DUST-DEVIL-04: the Dust Devil, a desert whirl-jelly with amber veins.

    A swollen fleshy bell, and a slowly turning ring of sinew carrying three clinging sand rays.
    """
    return build_boss_model(
        DUST_DEVIL,
        scene,
        AMBER,
        {
            "core": _draw_core,
            "ring": _draw_ring,
            "parts": {"blade-1": _blade_pod, "blade-2": _blade_pod, "blade-3": _blade_pod},
            "armour": {"back": {"whole": _draw_plating}},
        },
    )
