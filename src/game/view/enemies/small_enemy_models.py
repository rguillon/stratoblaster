# Copyright (c) 2026 Renaud Guillon
"""The lighter enemies (Gnat, Hornet, Scout, Strafer, Weaver), Cyber-Organic (ENM-35).

Swollen flesh bodies, membrane wings that flutter, metal only where grafted on (ducts, stingers,
guns, nozzles): one body with a few grafts, a basic kind's look (GFX-ART-16). Logical pixels, nose
+Z, Y up (towards the camera).

As every basic model (here, in `heavy_enemy_models.py`, `heavy_beetle_models.py`
"""

import math

from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies.basic_parts import (
    eye_pair,
    gun_barrel,
    wing_pair,
)
from game.view.enemies.enemy_mesh import build_enemy_model
from game.view.enemies.enemy_shapes import (
    LOBE_SECTION,
    SIDES,
)
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import (
    SegmentedBody,
    curve,
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
QUARTER = math.pi / 2


def build_hornet(scene: Any) -> Any:
    """ENM-HORNET-01: a stinger diver, a wasp of three swollen segments.

    A metal stinger at its nose under a single eye, and swept, serrated membrane wings that flutter
    (ENM-HORNET-02); one reactor in a flesh sac, yellow (ENM-HORNET-03).
    """

    def draw(p: Any) -> None:
        flesh = p.flesh
        hull = p.hull
        neon = p.neon
        body = SegmentedBody(-9, 10.5, 3, 2.6, -1.3, 2.4)
        segmented_body(flesh, body, F.slate, None, LOBE_SECTION)
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
        reactor_sac(p, [0, 0.1, -9], 1.2, N.hornet, F.sinew, 3)
        eye = [[0, -0.5], [0.9, 0], [0, 0.6]]
        neon.lathe(eye, 5, N.hornet, Placement([0, 1.4, 7.4]))

    return build_enemy_model("hornet", scene, N.hornet, draw)


# ENM-SCOUT-02: the Scout's neon strip along each tail boom.
SCOUT_STRIP = [[-0.35, -14], [0.35, -14], [0.35, -5], [-0.35, -5]]  # type: list[list[float]]


def build_scout(scene: Any) -> Any:
    """ENM-SCOUT-01: a light winged scout with a slim flesh body.

    Broad membrane wings that flutter, two bone tail booms with a neon strip and a reactor each
    (ENM-SCOUT-02), and a nose gun grafted on (ENM-SCOUT-03); green (ENM-SCOUT-04).
    """

    def draw(p: Any) -> None:
        flesh = p.flesh
        neon = p.neon
        reactor = p.reactor
        body = SegmentedBody(-9, 12.5, 2, 2.5, -1, 2.3)
        segmented_body(flesh, body, F.teal, None, LOBE_SECTION)
        eye_pair(p, [0, 1.6, 8], 0.8, 0.4, N.scout)
        wing_pair(
            p,
            {
                "root": [1.8, 6],
                "tips": [[13, -8], [10, -9], [5, -6]],
                "y": 0.6,
                "strut": 0.5,
            },
            N.scout,
        )
        for s in SIDES:
            tendril(
                flesh,
                curve([s * 2, 0.4, 2], [s * 7, 0.6, -15], [s * 1.5, 0, 0], 3),
                [1.3, 1],
                4,
                F.bone,
            )
            neon.slab(SCOUT_STRIP, [1.3, 1.7], N.scout, Placement([s * 7, 0, 0]))
            reactor([s * 7, 0.3, -15], 1.1)
        # Its nose gun (phase 7 review).
        gun_barrel(p, [0, 1.3, 6], 6.5)

    return build_enemy_model("scout", scene, N.scout, draw)


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
        eye_pair(p, [0, 1.5, 7], 1, 0.5, N.strafer)
        lights = [edge_light([3, 6], [20.5, -1.5], k / 4, 1.6, [2.4, 0.7]) for k in [1, 2, 3]]
        wing_pair(
            p,
            {
                "root": [3, 4],
                "tips": [[20.5, -1.5], [20.5, -5], [7, -4]],
                "y": 0.2,
                "strut": 0.6,
                "lights": lights,
            },
            N.strafer,
        )
        for x in [-12, -4, 4, 12]:
            reactor([x, 0, -4.3 if abs(x) == STRAFER_INNER_X else -4.1], 1)
        for s in SIDES:
            # A gun on each side of the body, pointing out sideways: it flies across the screen
            # and fires down it from the one facing down (phase 7 review).
            gun_barrel(p, [s * 4.6, 1.5, 1.5], 3.6, s * QUARTER)

    return build_enemy_model("strafer", scene, N.strafer, draw)
