# Copyright (c) 2026 Renaud Guillon
"""The Spinner, the Lancer and the Rocketeer, Cyber-Organic (ENM-35).

Swollen flesh bodies and organs, metal grafted on for armour, nozzles and guns. Logical pixels, nose
+Z, Y up. The Bulwark and the Splitter are in `heavy_beetle_models.py`.
"""

import math

from game.config.enemies import ENEMY_CONFIG
from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies.basic_parts import eye_pair, sinew
from game.view.enemies.enemy_mesh import build_enemy_model
from game.view.enemies.enemy_shapes import (
    LOBE_SECTION,
    SIDES,
    angry_eyes,
    around,
    decal,
    radial,
)
from render.geometry.organic import (
    SegmentedBody,
    curve,
    organ,
    segmented_body,
    tendril,
)
from render.geometry.organic import (
    vein as vein_tube,
)
from render.geometry.solids import Placement

# isort: split
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
F = ENEMY_LOOK.flesh
N = ENEMY_LOOK.neon
WHITE = [1, 1, 1]  # type: list[float]
QUARTER = math.pi / 2

# ENM-SPINNER-02: the Spinner's pod muzzles, lit while it fires.
SPINNER_MUZZLE = [[-1.5, 2.2], [1.5, 2.2], [1.3, 3.1], [-1.3, 3.1]]  # type: list[list[float]]


def build_spinner(scene: Any) -> Any:
    """ENM-SPINNER-01: a spiral turret, an organic core spinning four sinew arms.

    The arms are curled the same way round, with a flesh pod at the end of each with a metal muzzle
    collar, and a neon heart (yellow, ENM-SPINNER-03).
    """
    pod_radius = ENEMY_CONFIG.spinner.podRadius

    def draw(p: Any) -> None:
        flesh = p.flesh
        hull = p.hull
        neon = p.neon
        charge = p.charge
        muzzle = p.muzzle
        organ(flesh, 5, 6, F.graphite, Placement([0, -1.6, 0]), 0.35)
        for a in around(4):
            # Each arm leaves the core a quarter turn behind its pod: a spiral.
            arm = curve(radial(a - 0.9, 4.2, 0), radial(a, pod_radius - 3.4, 0), [0, 0.5, 0], 3)
            bowed = []
            for i, q in enumerate(arm):
                k = math.sin((math.pi * i) / 3) * 2.2
                bowed.append([q[0] + math.cos(a) * k, q[1], q[2] - math.sin(a) * k])
            tendril(flesh, bowed, [1.3, 1], 3, F.sinew)
            organ(
                flesh,
                2.4,
                5,
                F.slate,
                Placement(radial(a, pod_radius - 3.6, -0.2), a, QUARTER),
                1.1,
            )
            hull.ring(1.6, 1, 5, H.panel, Placement(radial(a, pod_radius + 1.2, 0), a, QUARTER))
            # The pods' muzzles light up while it fires.
            charge.slab(SPINNER_MUZZLE, [-0.7, 0.7], WHITE, Placement(radial(a, pod_radius, 0), a))
            muzzle(radial(a, pod_radius + 3.1, 0), "gun")
        core = [[0, -1.5], [3.2, -0.6], [0, 2.6]]
        neon.lathe(core, 6, N.spinner, None)

    return build_enemy_model("spinner", scene, N.spinner, draw)


# ENM-LANCER-02: the Lancer's right fin, a flesh blade at its tail.
LANCER_FIN = [[2.5, -6], [10, -17], [9.5, -20], [2.5, -15]]  # type: list[list[float]]


def build_lancer(scene: Any) -> Any:
    """ENM-LANCER-01: a laser lance, a long body of swollen segments.

    A metal lance is grafted on its head, ending in the glowing emitter; two flesh fins and three
    reactors (ENM-LANCER-02); veins run along its back (yellow, ENM-LANCER-04).
    """
    nose = ENEMY_CONFIG.lancer.emitterOffset

    def draw(p: Any) -> None:
        flesh = p.flesh
        hull = p.hull
        neon = p.neon
        charge = p.charge
        reactor = p.reactor
        muzzle = p.muzzle
        body = SegmentedBody(-21, 9, 4, 3.2, -1.5, 2.4)
        segmented_body(flesh, body, F.graphite, None, LOBE_SECTION)
        hull.cylinder(1.5, nose - 6, 5, H.panel, Placement([0, 0, 5], 0, QUARTER), 0.6)
        eye_pair(p, [0, 1.6, 6], 1, 0.5, N.lancer)
        reactor([0, 0, -21], 1.6)
        for s in SIDES:
            neon.box([0.5, 0.4, 14], N.lancer, Placement([s * 1.6, 2.1, -6]))
            fin = [[s * pt[0], pt[1]] for pt in LANCER_FIN]
            flesh.bevel_slab(fin, [-0.5, 0, 0.5], [0.3, 0.5], F.membrane, None, F.sinew)
            reactor([s * 6.5, 0, -17.8], 0.9)
        emitter = [[0, -1.4], [1.8, 0], [0, 1.4]]
        # Brightens through the warning (its `charge`), full while the laser fires (ENM-LANCER-03).
        charge.lathe(emitter, 6, WHITE, Placement([0, 0, nose]))
        muzzle([0, 0, nose + 1.8], "laser")

    return build_enemy_model("lancer", scene, N.lancer, draw)


# ENM-ROCKETEER-01: the Rocketeer's armour plate, grafted on its back.
ROCKETEER_ARMOUR = [[0, 9], [4.5, 5], [4.5, -8], [-4.5, -8], [-4.5, 5]]  # type: list[list[float]]


def build_rocketeer(scene: Any) -> Any:
    """ENM-ROCKETEER-01: a bulky flesh body with an armour plate on its back.

    On sinews it carries a long egg sac on each side: its missiles, their tips glowing when loaded
    (ENM-ROCKETEER-02). Two reactors (ENM-ROCKETEER-03), in yellow (ENM-ROCKETEER-04).
    """
    pod = ENEMY_CONFIG.rocketeer.podOffset

    def draw(p: Any) -> None:
        flesh = p.flesh
        hull = p.hull
        neon = p.neon
        charge = p.charge
        reactor = p.reactor
        body = SegmentedBody(-15, 14, 3, 9, -2.2, 3.4)
        segmented_body(flesh, body, F.slate, None, LOBE_SECTION)
        hull.bevel_slab(ROCKETEER_ARMOUR, [2.4, 2.4, 3.6], [0, 1], H.panel, None, H.base)
        for eye in angry_eyes([0, 6.2], 0.8, [2.4, 0.6], 0.4):
            decal(neon, eye, 3.62, N.rocketeer)
        for s in SIDES:
            sinew(p, [s * 7, 0.5, 6], [s * (pod - 3), 0.5, 4], [0, 1, 1], 1.4)
            sinew(p, [s * 7, 0.5, -8], [s * (pod - 3), 0.5, -6], [0, 1, -1], 1.4)
            # The egg sac: a long organ lying along Z, its missile tip at the front.
            organ(flesh, 4, 6, F.membrane, Placement([s * pod, 0, -11], 0, QUARTER), 2.75)
            vein_tube(
                p.vein,
                curve([s * pod, 3.6, -8], [s * pod, 3.6, 6], [0, 0.8, 0], 3),
                0.9,
                N.rocketeer,
            )
            charge.cylinder(2.4, 3.5, 6, WHITE, Placement([s * pod, 0, 11], 0, QUARTER), 0)
            p.muzzle([s * pod, 0, 14.5], "missile")
            reactor([s * 2.4, 0, -15], 1.6)

    return build_enemy_model("rocketeer", scene, N.rocketeer, draw)


__all__ = [
    "build_lancer",
    "build_rocketeer",
    "build_spinner",
]
