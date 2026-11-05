# Copyright (c) 2026 Renaud Guillon
"""The Spinner, the Lancer and the Rocketeer, Cyber-Organic (ENM-35).

Swollen flesh bodies and organs, metal grafted on for armour, nozzles and guns. Logical pixels, nose
+Z, Y up. The Bulwark and the Splitter are in `heavy_beetle_models.py`.
"""

import math

from game.config.enemies import ENEMY_CONFIG
from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies.basic_parts import config_barrels, eye_pair
from game.view.enemies.enemy_mesh import build_enemy_model
from game.view.enemies.enemy_shapes import (
    LOBE_SECTION,
    SIDES,
    angry_eyes,
    around,
    decal,
    flip_x,
    radial,
)
from game.view.enemies.weapon_ports import port_radius
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
        # Each pod's barrel recoils (WPN-03).
        config_barrels(p, ENEMY_CONFIG.spinner.muzzles, 2.2, 0.7)
        core = [[0, -1.5], [3.2, -0.6], [0, 2.6]]
        neon.lathe(core, 6, N.spinner, None)

    return build_enemy_model("spinner", scene, N.spinner, draw)


# ENM-LANCER-02: the Lancer's right fin, a flesh blade at its tail.
LANCER_FIN = [[4, -6], [12, -17], [11.5, -20], [4, -15]]  # type: list[list[float]]
# ENM-LANCER-01: its body's half width, and the Z of its eyes; the gun starts just in front of them.
LANCER_WIDTH = 5.2
LANCER_EYES_Z = 6
LANCER_GUN_BASE = 7
LANCER_GUN_RADIUS = 3


def build_lancer(scene: Any) -> Any:
    """ENM-LANCER-01: a laser lance, a wide body of swollen segments.

    The laser gun is its whole head, from just in front of its eyes to the glowing emitter; two
    flesh fins and three reactors (ENM-LANCER-02); veins run along its back (yellow, ENM-LANCER-04).
    """
    mouth = ENEMY_CONFIG.lancer.emitterOffset + 1.8

    def draw(p: Any) -> None:
        flesh = p.flesh
        neon = p.neon
        reactor = p.reactor
        body = SegmentedBody(-21, 10, 4, LANCER_WIDTH, -1.8, 2.6)
        segmented_body(flesh, body, F.graphite, None, LOBE_SECTION)
        eye_pair(p, [0, 1.8, LANCER_EYES_Z], 1.8, 0.7, N.lancer)
        reactor([0, 0, -21], 1.6)
        for s in SIDES:
            neon.box([0.5, 0.4, 14], N.lancer, Placement([s * 2.6, 2.2, -6]))
            fin = [[s * pt[0], pt[1]] for pt in LANCER_FIN]
            flesh.bevel_slab(fin, [-0.5, 0, 0.5], [0.3, 0.5], F.membrane, None, F.sinew)
            reactor([s * 8, 0, -17.8], 0.9)
        # The gun is the whole tip of the ship: a wide barrel from the eyes to the mouth, its coils
        # and lens brightening through the warning (its `charge`), full while it fires
        # (ENM-LANCER-03).
        gun = mouth - LANCER_GUN_BASE
        p.muzzle([0, 0, mouth], "laser", "forward", LANCER_GUN_RADIUS, None, True, gun)

    return build_enemy_model("lancer", scene, N.lancer, draw)


# ENM-ROCKETEER-02: the radius of a missile sac, and how far a wing reaches past the pod's centre.
SAC_RADIUS = 4
# A launcher: its mouth (the config's muzzle, model Z), and its length back into the sac.
ROCKETEER_MOUTH = 14.5
ROCKETEER_LAUNCHER = 7
WING_PAST_POD = 7


# The right wing's leading edge, from the body's flank (`[x, z]`) out to its tip's Z.
WING_ROOT = [5, 7]  # type: list[float]
WING_TIP_Z = 4


def rocketeer_wing(pod: float) -> list[list[float]]:
    """Return the right wing (`[x, z]`): from the body's flank, through the pod, out past it."""
    tip = pod + WING_PAST_POD
    return [WING_ROOT, [tip, WING_TIP_Z], [tip, 0], [pod + 2, -3.5], [WING_ROOT[0], -9]]


def leading_edge_z(pod: float, x: float) -> float:
    """Return the Z of the right wing's leading edge at `x`."""
    tip = pod + WING_PAST_POD
    t = (x - WING_ROOT[0]) / (tip - WING_ROOT[0])
    return WING_ROOT[1] + (WING_TIP_Z - WING_ROOT[1]) * t


def rocketeer_wing_light(pod: float) -> list[list[float]]:
    """Return the neon light just behind the right wing's leading edge, out past the pod."""
    a = pod + SAC_RADIUS + 0.3
    b = pod + WING_PAST_POD - 0.4
    za = leading_edge_z(pod, a)
    zb = leading_edge_z(pod, b)
    return [[a, za - 0.3], [b, zb - 0.3], [b, zb - 1.1], [a, za - 1.1]]


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
        reactor = p.reactor
        body = SegmentedBody(-15, 14, 3, 9, -2.2, 3.4)
        segmented_body(flesh, body, F.slate, None, LOBE_SECTION)
        hull.bevel_slab(ROCKETEER_ARMOUR, [2.4, 2.4, 3.6], [0, 1], H.panel, None, H.base)
        for eye in angry_eyes([0, 6.2], 0.8, [2.4, 0.6], 0.4):
            decal(neon, eye, 3.62, N.rocketeer)
        for s in SIDES:
            # One swept wing joins the body to the pod, runs through it and comes out past its
            # outer side, a neon light along its leading edge.
            wing = rocketeer_wing(pod) if s > 0 else flip_x(rocketeer_wing(pod))
            light = rocketeer_wing_light(pod) if s > 0 else flip_x(rocketeer_wing_light(pod))
            hull.bevel_slab(wing, [-0.5, 0, 0.6], [0.2, 0.3], H.base, None, H.panel)
            decal(neon, light, 0.65, N.rocketeer)
            # The egg sac: a long organ lying along Z, its missile tip at the front.
            organ(flesh, SAC_RADIUS, 6, F.membrane, Placement([s * pod, 0, -11], 0, QUARTER), 2.75)
            # Its lights run along its flanks, not along the top of the launcher.
            for side in [-1, 1]:
                x = s * pod + side * (SAC_RADIUS - 0.5)
                vein_tube(
                    p.vein,
                    curve([x, 0.9, -7], [x, 0.9, 6], [side * 0.9, 0, 0], 3),
                    0.6,
                    N.rocketeer,
                )
            # The launcher is its port all along (WPN-07): a dark hexagonal tube out of the sac,
            # hollow to its floor so the rocket is seen in it and leaving it, with no edge trim
            # (drawn bare: nothing glows at its mouth) and a highlight line along each side edge.
            missile = ENEMY_CONFIG.rocketeer.missile.radius
            tube = port_radius(missile)
            mouth = ROCKETEER_MOUTH
            for side in [-1, 1]:
                edge = Placement([s * pod + side * tube, 0, mouth - ROCKETEER_LAUNCHER / 2])
                neon.box([0.3, 0.3, ROCKETEER_LAUNCHER - 0.4], N.rocketeer, edge)
            # The model's +X is the screen's left: the config's first pod (launcher 0).
            p.muzzle(
                [s * pod, 0, mouth],
                "missile",
                "forward",
                missile,
                0 if s > 0 else 1,
                False,
                ROCKETEER_LAUNCHER,
            )
            reactor([s * 2.4, 0, -15], 1.6)

    return build_enemy_model("rocketeer", scene, N.rocketeer, draw)


__all__ = [
    "build_lancer",
    "build_rocketeer",
    "build_spinner",
]
