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
    CANOPY_SECTION,
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
)
from render.geometry.organic import (
    vein as vein_tube,
)
from render.geometry.solids import LoftOptions, Placement

# isort: split
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
F = ENEMY_LOOK.flesh
N = ENEMY_LOOK.neon
QUARTER = math.pi / 2


# ENM-SPINNER-01: its outer ring, kept low. A lathe profile faces outwards when it runs from the
# outside in: outer wall up, lip in, inner wall down.
SPINNER_RING = [  # type: list[list[float]]
    [15, -1.6],
    [15, 0.2],
    [14.4, 0.8],
    [12.6, 0.8],
    [12, 0.2],
    [12, -1.6],
]
SPINNER_SIDES = 16
# A gun's mount on the ring (`[w, h, d]`, standing on its base) and how far out its centre is.
SPINNER_MOUNT = [3.4, 2.2, 3.6]  # type: list[float]
SPINNER_MOUNT_AT = 15
# The guns' barrels (length, radius), and the collar each comes out of at the mount's face.
SPINNER_GUN = [3.6, 0.8]  # type: list[float]
SPINNER_COLLAR = [1.25, 0.9]  # type: list[float]
# The hub under the body the ring's spokes turn on, and the spokes' height.
SPINNER_HUB = 3.2
SPINNER_SPOKE_Y = -1.2
# The inner body, raised over the ring so its reactors' flames pass over it, not through it.
SPINNER_LIFT = 2.4
SPINNER_BODY = SegmentedBody(-8, 9.5, 3, 4.6, -1.6, 1.8)
# Its cockpit: a canopy on its back, ahead of the middle (loft stations `[z, w, bottom, top]`).
SPINNER_CANOPY = [  # type: list[list[float]]
    [0, 0.6, 1.4, 1.8],
    [2.2, 2.1, 1.3, 2.9],
    [5.2, 1.8, 1.0, 2.6],
    [7.4, 0.4, 0.6, 0.9],
]
# Its two engines either side of the tail: across, where their nozzles open (Z), their length
# forward and their radius; the reactor's in them.
SPINNER_ENGINE = {"x": 3.4, "back": -9.6, "length": 7, "radius": 1.8}
SPINNER_REACTOR = 1.4


def spinner_body(p: Any) -> None:
    """Draw the Spinner's inner body (ENM-SPINNER-01): it faces the player, the ring turns round it.

    A swollen flesh body raised over the ring, a dark cockpit canopy with a lit visor, a metal
    armour plate, and two engine pods at its tail, each with a reactor (ENM-SPINNER-03).
    """
    lift = Placement([0, SPINNER_LIFT, 0])
    segmented_body(p.flesh, SPINNER_BODY, F.graphite, lift, LOBE_SECTION)
    p.hull.loft(CANOPY_SECTION, SPINNER_CANOPY, H.dark, lift, LoftOptions(True))
    p.neon.box([2.6, 0.3, 0.4], N.spinner, Placement([0, SPINNER_LIFT + 2.3, 6.3]))
    p.hull.box([3.6, 0.6, 5], H.base, Placement([0, SPINNER_LIFT + 1.3, -4]), H.panel)
    engine = SPINNER_ENGINE
    for s in SIDES:
        x = s * engine["x"]
        at = Placement([x, SPINNER_LIFT, engine["back"]], 0, QUARTER)
        p.hull.cylinder(engine["radius"], engine["length"], 6, H.base, at, engine["radius"] * 0.7)
        p.neon.box(
            [0.3, 0.3, engine["length"] - 1.5],
            N.spinner,
            Placement([x + s * 1.2, SPINNER_LIFT + 1.2, engine["back"] + 3.6]),
        )
        p.reactor([x, SPINNER_LIFT, engine["back"]], SPINNER_REACTOR)


def spinner_ring(piece: Any) -> None:
    """Draw the Spinner's outer ring (ENM-SPINNER-02), all of which turns with its spin.

    The ring, its edges glowing with the highlight (ENM-SPINNER-03), four spokes under the body to
    the hub it turns on, and four gun mounts on its outside, each with a collar its barrel comes
    out of.
    """
    metal = piece.bare
    # The ring itself is the trimmed metal: its edges glow with the highlight (GFX-TRIM-06).
    piece.hull.lathe(SPINNER_RING, SPINNER_SIDES, H.panel, None, False)
    metal.cylinder(SPINNER_HUB, 0.8, 8, H.dark, Placement([0, SPINNER_SPOKE_Y - 0.4, 0]))
    outer = SPINNER_MOUNT_AT + SPINNER_MOUNT[2] / 2
    for a in around(4):
        spoke = Placement(radial(a, (SPINNER_HUB + 12) / 2, SPINNER_SPOKE_Y - 0.3), a)
        metal.box([1.2, 0.6, 12 - SPINNER_HUB + 0.4], H.dark, spoke)
        mount = Placement(radial(a, SPINNER_MOUNT_AT, -1.6), a)
        metal.box(SPINNER_MOUNT, H.base, mount, H.panel)
        collar = Placement(radial(a, outer - 0.1, 0), a, QUARTER)
        metal.cylinder(SPINNER_COLLAR[0], SPINNER_COLLAR[1], 6, H.dark, collar)


def build_spinner(scene: Any) -> Any:
    """ENM-SPINNER-01: an inner body inside an outer gun ring that spins round it.

    The body (cockpit, two reactors) faces the player; the ring, its spokes, its four gun mounts and
    their barrels turn with the Spinner's spin (`Spinner.turret`), the barrels recoiling as they
    fire (ENM-SPINNER-02, WPN-03).
    """

    def draw(p: Any) -> None:
        spinner_body(p)
        # The ring turns about the centre with the spin, as the barrels do (its own recoil: none).
        p.slide([0, 0, 0], [0, -1], 0, 0, spinner_ring, True)
        gun = SPINNER_GUN
        config_barrels(p, ENEMY_CONFIG.spinner.muzzles, gun[0], gun[1], True, [0, 0, 0], False)

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
