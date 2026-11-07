# Copyright (c) 2026 Renaud Guillon
"""The lighter enemies (Gnat, Hornet, Scout, Strafer, Weaver), Cyber-Organic (ENM-35).

Swollen flesh bodies, membrane wings that flutter, metal only where grafted on (ducts, stingers,
guns, nozzles): one body with a few grafts, a basic kind's look (GFX-ART-16). Logical pixels, nose
+Z, Y up (towards the camera).

As every basic model (here, in `heavy_enemy_models.py`, `heavy_beetle_models.py`
"""

import math

from game.config.enemies import ENEMY_CONFIG
from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies.basic_parts import (
    config_barrels,
    recoil_barrel,
    wing_pair,
)
from game.view.enemies.enemy_mesh import build_enemy_model
from game.view.enemies.enemy_shapes import (
    CANOPY_SECTION,
    FIGHTER_SECTION,
    LOBE_SECTION,
    POD_SECTION,
    SIDES,
    decal,
    flip_x,
)
from render.geometry.organic import (
    SegmentedBody,
    curve,
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


# The Hornet's abdomen, hidden under its wings: a plain low section (`[x, y]`, counter-clockwise
# seen from the nose) and its stations (`[z, half width, bottom, top]`), tail to where the head's
# lobe covers it. Its head is the one detailed lobe, in front of the wings.
HORNET_ABDOMEN_SECTION = [[0, 0], [1, 0.4], [0, 1], [-1, 0.4]]  # type: list[list[float]]
HORNET_ABDOMEN = [  # type: list[list[float]]
    [-9, 0, 0.55, 0.55],
    [-4, 2.6, -1.3, 2.4],
    [4, 1.8, -0.8, 2],
]


def hornet_body(flesh: Any, place: Placement | None = None) -> None:
    """Add a Hornet's body: a plain abdomen under its wings and a swollen head lobe."""
    flesh.loft(HORNET_ABDOMEN_SECTION, HORNET_ABDOMEN, F.slate, place)
    head = SegmentedBody(3, 10.5, 1, 2.6, -1.3, 2.4)
    segmented_body(flesh, head, F.slate, place, LOBE_SECTION)


def build_hornet(scene: Any) -> Any:
    """ENM-HORNET-01: a stinger diver, a wasp of three swollen segments.

    A metal stinger at its nose under a single eye, and swept, serrated membrane wings that flutter
    (ENM-HORNET-02); one reactor in a flesh sac, yellow (ENM-HORNET-03).
    """

    def draw(p: Any) -> None:
        flesh = p.flesh
        hull = p.hull
        hornet_body(flesh)
        hull.cylinder(0.9, 3.2, 4, H.panel, Placement([0, 0.4, 9.3], 0, QUARTER), 0)
        vein_tube(p.vein, curve([0, 2.3, -7], [0, 2.4, 6], [0, 0.6, 0], 3), 0.6, N.hornet)
        wing_pair(
            p,
            {
                "root": [1.6, 2],
                "tips": [[11.5, -11], [8, -11], [3, -7]],
                "y": 1.6,
                "strut": 0.45,
            },
            N.hornet,
        )
        # Its reactor alone: the sac it sat in was hidden under the wings.
        p.reactor([0, 0.1, -9], 1.2)

    return build_enemy_model("hornet", scene, N.hornet, draw)


# ENM-SCOUT-02: the Scout's airplane wing (right side, `[x, z]`), tailplane and the neon edge light
# along the wing's leading edge.
SCOUT_WING = [[3.5, 4], [14, -4], [14, -7.5], [3.5, -6.5]]  # type: list[list[float]]
SCOUT_WING_LIGHT = [[4.6, 3], [13, -3.6], [12.6, -4.4], [4.2, 2.2]]  # type: list[list[float]]
SCOUT_TAILPLANE = [[2.5, -9], [7.5, -13], [7.5, -14.5], [2.5, -12.5]]  # type: list[list[float]]
# The gun turret: a ring on the fuselage's back at the gun's pivot (`ENEMY_CONFIG.scout.turret`).
SCOUT_TURRET = {"radius": 3.6, "height": 1.4, "y": 3.3, "z": -ENEMY_CONFIG.scout.turret.y}
# The fuselage, tail to nose (`[z, half width, y0, y1]`): widest in the middle, where the wings,
# the nacelles and the turret are faired in, closing to a point at the nose.
SCOUT_FUSELAGE = [  # type: list[list[float]]
    [-13.5, 2.6, -0.6, 2.2],
    [-9, 4, -1.2, 3],
    [-3, 5, -1.6, 3.5],
    [3, 4.8, -1.5, 3.4],
    [8, 3.4, -1.1, 2.8],
    [12, 1.8, -0.6, 1.6],
    [14.5, 0, 0.4, 0.4],
]
# The flesh canopy ahead of the turret (open at the bottom, sitting on the fuselage).
SCOUT_CANOPY = [  # type: list[list[float]]
    [2.5, 0.6, 3.2, 3.6],
    [4.5, 1.8, 3.1, 4.4],
    [8, 1.5, 2.6, 3.9],
    [10.5, 0.3, 2, 2.3],
]
# A wing root's fairing (right side, `[x, z]`): from the nose's flank back along the wing's root.
SCOUT_FAIRING = [[1.5, 11], [4.6, 4], [5.2, -4], [3.5, -6.5], [2, 6]]  # type: list[list[float]]
# An engine nacelle: across from the centre, where its nozzle opens (Z), its length forward into the
# fuselage, and its radius round the 1.5 nozzle.
SCOUT_NACELLE = {"x": 3.4, "back": -12.8, "length": 9, "radius": 1.9}
# The gun's barrel: its length (from the pivot to its tip light) and radius.
SCOUT_GUN = {"length": 9, "radius": 1}


def build_scout(scene: Any) -> Any:
    """ENM-SCOUT-01: a light fighter, one blended airframe.

    A metal fighter fuselage, wide in the middle, into which the swept wings' roots, the tailplane
    and the two engine nacelles are faired (ENM-SCOUT-02): nothing stands apart from the body. A
    flesh canopy on its back with a neon visor, a neon spine line, and a gun turret behind the
    canopy (ENM-SCOUT-03); green (ENM-SCOUT-04).
    """

    def draw(p: Any) -> None:
        flesh = p.flesh
        hull = p.hull
        neon = p.neon
        reactor = p.reactor
        hull.loft(FIGHTER_SECTION, SCOUT_FUSELAGE, H.base)
        # The flesh canopy ahead of the turret, a neon visor across its front.
        flesh.loft(CANOPY_SECTION, SCOUT_CANOPY, F.teal, None, LoftOptions(True))
        neon.box([2.4, 0.4, 0.5], N.scout, Placement([0, 3.7, 7.8]))
        for s in SIDES:
            wing = SCOUT_WING if s > 0 else flip_x(SCOUT_WING)
            light = SCOUT_WING_LIGHT if s > 0 else flip_x(SCOUT_WING_LIGHT)
            tail = SCOUT_TAILPLANE if s > 0 else flip_x(SCOUT_TAILPLANE)
            fairing = SCOUT_FAIRING if s > 0 else flip_x(SCOUT_FAIRING)
            hull.bevel_slab(wing, [-0.5, 0, 0.6], [0.2, 0.3], H.base, None, H.panel)
            decal(neon, light, 0.65, N.scout)
            hull.bevel_slab(tail, [-0.3, 0, 0.4], [0.2, 0.2], H.base, None, H.panel)
            # The wing root's fairing, from the nose's flank back along the wing.
            hull.bevel_slab(fairing, [-0.9, 0.2, 1.4], [0.4, 0.8], H.base, None, H.panel)
            # ENM-SCOUT-02: each engine is a nacelle faired into the fuselage's flank, from the
            # wing root back to its nozzle.
            hull.loft(
                POD_SECTION, scout_nacelle(), H.panel, Placement([s * SCOUT_NACELLE["x"], 0, 0])
            )
            reactor([s * SCOUT_NACELLE["x"], 0.3, SCOUT_NACELLE["back"]], 1.5)
        # The turret: a metal ring the gun pivots on (WPN-02), its barrel recoiling (WPN-03).
        hull.cylinder(
            SCOUT_TURRET["radius"],
            SCOUT_TURRET["height"],
            8,
            H.panel,
            Placement([0, SCOUT_TURRET["y"], SCOUT_TURRET["z"]]),
            SCOUT_TURRET["radius"] * 0.8,
        )
        config_barrels(
            p, ENEMY_CONFIG.scout.muzzles, SCOUT_GUN["length"], SCOUT_GUN["radius"], True
        )

    return build_enemy_model("scout", scene, N.scout, draw)


def scout_nacelle() -> list[list[float]]:
    """Return the loft stations of an engine nacelle about its own axis (`[z, half width, y0, y1]`).

    Round the nozzle at the back, swelling forward, then sinking into the fuselage at the wing root.
    """
    r = SCOUT_NACELLE["radius"]
    back = SCOUT_NACELLE["back"]
    return [
        [back, r, 0.3 - r, 0.3 + r],
        [back + 4, r * 1.1, 0.3 - r * 1.1, 0.3 + r * 1.1],
        [back + SCOUT_NACELLE["length"], r * 0.5, 0.3 - r * 0.5, 0.3 + r * 0.5],
    ]


def edge_light(
    a: list[float], b: list[float], t: float, inward: float, span: list[float]
) -> list[list[float]]:
    """Return a light along an edge from `a` to `b`, at `t` of it.

    The light is `inward` away from the edge and `length` long (`span` is `[length, width]`).
    """
    length = span[0]
    width = span[1]
    dx = b[0] - a[0]
    dz = b[1] - a[1]
    d = math.hypot(dx, dz)
    ux = dx / d
    uz = dz / d
    # The side of the edge behind it, towards the trailing edge.
    if ux < 0:
        nx = -uz
        nz = ux
    else:
        nx = uz
        nz = -ux
    cx = a[0] + dx * t + nx * inward
    cz = a[1] + dz * t + nz * inward

    def along(k: float, w: float) -> list[float]:
        return [cx + (ux * (k * length)) / 2 + nx * w, cz + (uz * (k * length)) / 2 + nz * w]

    return [along(-1, 0), along(1, 0), along(1, width), along(-1, width)]


# The strafer's reactors at this distance out sit a little further back (ENM-STRAFER-03).
STRAFER_INNER_X = 4
# Its guns' barrels (length, radius) and the pod on each flank that holds them (`[w, h, d]`).
STRAFER_GUN = [5, 0.8]  # type: list[float]
STRAFER_POD = [4.2, 3, 8]  # type: list[float]


def build_strafer(scene: Any) -> Any:
    """ENM-STRAFER-01: a fan shooter, a wide pair of membrane wings out of a squat flesh body.

    A row of neon glands runs along each leading edge (ENM-STRAFER-02), with four reactors and a gun
    on each flank (ENM-STRAFER-03); yellow (ENM-STRAFER-04).
    """

    def draw(p: Any) -> None:
        flesh = p.flesh
        reactor = p.reactor
        body = SegmentedBody(-6.5, 10.5, 2, 4.2, -1.3, 2.3)
        segmented_body(flesh, body, F.graphite, None, LOBE_SECTION)
        lights = [edge_light([3, 6], [20.5, -1.5], k / 4, 1.6, [2.4, 0.7]) for k in [1, 2, 3]]
        wing_pair(
            p,
            {
                "root": [3, 4],
                "tips": [[20.5, -1.5], [20.5, -5], [7, -4]],
                "y": 0.2,
                "strut": 0.6,
                "lights": lights,
                # Its wings are held still.
                "fixed": True,
            },
            N.strafer,
        )
        for x in [-12, -4, 4, 12]:
            reactor([x, 0, -4.3 if abs(x) == STRAFER_INNER_X else -4.1], 1)
        # A gun pod on each flank, out of the body to the barrels' housings, so they are held to it.
        for s in SIDES:
            p.hull.box(STRAFER_POD, H.dark, Placement([s * 4.2, 0, 1.6]), H.panel)
        # Three guns on each side of the body, pointing out sideways, fanned: it flies across the
        # screen and fires down it from the side facing down (phase 7 review, WPN-04). They are the
        # config's barrels, tip and angle.
        for i, (x, y, height, angle) in enumerate(ENEMY_CONFIG.strafer.muzzles):
            recoil_barrel(p, [x, height, -y], angle, STRAFER_GUN[0], i, STRAFER_GUN[1])

    return build_enemy_model("strafer", scene, N.strafer, draw)
