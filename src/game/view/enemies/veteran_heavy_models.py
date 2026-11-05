# Copyright (c) 2026 Renaud Guillon
"""The heavier veteran kinds, the Mortar and the Minelayer (specs/enemies/mortar.md, minelayer.md).

Logical pixels, nose +Z, Y up (to the camera).
"""

import math

from game.config.enemies_veteran import VETERAN_CONFIG
from game.config.enemies_veteran import VETERAN_NEON as N
from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies.enemy_mesh import build_enemy_model
from game.view.enemies.enemy_shapes import SIDES, angry_eyes, decal, flip_x
from game.view.enemies.weapon_ports import port_depth, port_radius
from render.geometry.organic import (
    SegmentedBody,
    carapace,
)
from render.geometry.solids import Placement

# isort: split
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
F = ENEMY_LOOK.flesh
WHITE = [1, 1, 1]  # type: list[float]
QUARTER = math.pi / 2


def _mortar_girth(t: float) -> float:
    return 0.6 + 0.4 * math.sin(math.pi * t)


# ENM-MORTAR-01: the Mortar's lower hull, a wide armoured slab (`[x, z]`, nose +Z), its heights
# (bottom, widest, top) and its bevels (bottom, top).
MORTAR_HULL = [  # type: list[list[float]]
    [0, 13],
    [10, 11.5],
    [14, 7],
    [14, -11],
    [10, -15.5],
    [-10, -15.5],
    [-14, -11],
    [-14, 7],
    [-10, 11.5],
]
MORTAR_HULL_HEIGHTS = [-2.6, 0.6, 3.2]  # type: list[float]
# The ram across its front, low and wide.
MORTAR_RAM = [[0, 15.5], [11, 13.5], [12, 10.5], [-12, 10.5], [-11, 13.5]]  # type: list[list[float]]
# A shoulder pod on each side (right side), the armoured block its ammunition drum lies on.
MORTAR_POD = [[13, 9], [20.5, 6], [20.5, -10], [17, -14], [13, -13]]  # type: list[list[float]]
# The swollen flesh hump on its back, behind the gun.
MORTAR_HUMP = SegmentedBody(-14, 5, 2, 9.5, 1.2, 7, None, _mortar_girth)
# The casemate the launcher tube comes out of, high on the hull (its front holds the tube's base).
MORTAR_CASEMATE = [[0, 6.5], [6.4, 5], [7, -5], [4.5, -8], [-4.5, -8], [-7, -5], [-6.4, 5]]  # type: list[list[float]]
# A shoulder pod's ammunition drum: across, height, its back and length along Z, radius.
MORTAR_DRUM = {"x": 16.8, "y": 7.2, "back": -11, "length": 13, "radius": 2.2}


def mortar_pod(p: Any, s: float) -> None:
    """Add the shoulder pod on side `s`: an armoured block, its ammunition drum, a light along it.

    ENM-MORTAR-02, ENM-MORTAR-03.
    """
    pod = MORTAR_POD if s > 0 else flip_x(MORTAR_POD)
    p.hull.bevel_slab(pod, [-1.6, 2.4, 5], [1, 1.2], H.base, None, H.panel)
    drum = MORTAR_DRUM
    x = s * drum["x"]
    along = Placement([x, drum["y"], drum["back"]], 0, QUARTER)
    p.hull.cylinder(drum["radius"], drum["length"], 8, H.dark, along)
    for z in [drum["back"] + 2, drum["back"] + drum["length"] - 2]:
        p.hull.ring(
            drum["radius"] + 0.25, 0.8, 8, H.panel, Placement([x, drum["y"], z], 0, QUARTER)
        )
    # Its running light along the pod's outer top edge.
    outer = s * 19.2
    decal(
        p.neon,
        [[outer - 0.5, 4], [outer + 0.5, 4], [outer + 0.5, -8], [outer - 0.5, -8]],
        5.05,
        N.mortar,
    )
    p.reactor([x, 1, -14.2], 1.5)


def build_mortar(scene: Any) -> Any:
    """ENM-MORTAR-02: a super bulky armoured gunship with a short, wide launcher tube.

    A wide, bevelled metal hull with a ram across its front, a swollen flesh hump on its back, a
    high casemate the tube comes out of, and on each side a shoulder pod with an ammunition drum
    on it. Angry eyes on its front, lights along its pods and round the casemate (ENM-MORTAR-03),
    two big reactors and one on each pod (ENM-MORTAR-05), within the veteran triangle budget
    (ENM-MORTAR-06). The barrel's mouth glows as the next shell charges (ENM-MORTAR-04).
    """
    muzzle_cfg = VETERAN_CONFIG.mortar.muzzles[0]
    mouth_height = muzzle_cfg[2]
    mouth = -muzzle_cfg[1]

    def draw(p: Any) -> None:
        hull = p.hull
        neon = p.neon
        charge = p.charge
        muzzle = p.muzzle
        # The bulk: the armoured hull, the ram, and the flesh hump swelling out of its back.
        hull.bevel_slab(MORTAR_HULL, MORTAR_HULL_HEIGHTS, [1.6, 2], H.base, None, H.panel)
        hull.bevel_slab(MORTAR_RAM, [-2, 0.4, 2.2], [0.8, 1], H.dark, None, H.base)
        carapace(p.flesh, MORTAR_HUMP, [F.sinew, F.slate])
        # The casemate, high on the hull, holding the base of the tube; a light band round it.
        hull.bevel_slab(MORTAR_CASEMATE, [2.8, 9, 12], [0.4, 1.6], H.base, None, H.panel)
        band = [[-6.6, 5.6], [6.6, 5.6], [6.6, 4.8], [-6.6, 4.8]]
        decal(neon, band, 9.05, N.mortar)
        for eye in angry_eyes([0, 9.6], 1.2, [3.2, 0.8], 0.45):
            decal(neon, eye, MORTAR_HULL_HEIGHTS[2] + 0.05, N.mortar)
        # The launcher tube, as wide as its port all along, which is wider than its heavy rocket
        # (WPN-07); a band round it, and the port at its mouth, its rim the charge light
        # (ENM-MORTAR-04), its rocket seen in the well once reloaded.
        missile = VETERAN_CONFIG.mortar.missile.radius
        tube = port_radius(missile)
        # The tube stops where its port's well starts, so nothing closes the hole.
        length = mouth - port_depth(missile) - 4
        hull.cylinder(tube, length, 6, H.dark, Placement([0, mouth_height, 4], 0, QUARTER))
        hull.ring(tube + 0.3, 1.5, 6, H.panel, Placement([0, mouth_height, mouth - 7], 0, QUARTER))
        band_at = Placement([0, mouth_height, mouth - 7.3], 0, QUARTER)
        neon.ring(tube + 0.35, 0.4, 6, N.mortar, band_at)
        charge.ring(
            tube + 0.35, 0.3, 6, WHITE, Placement([0, mouth_height, mouth - 5.6], 0, QUARTER)
        )
        muzzle([0, mouth_height, mouth], "missile", "forward", missile)
        for s in SIDES:
            mortar_pod(p, s)
            # A big reactor each side of the tail, in an armoured housing.
            hull.box([5.6, 4.6, 3], H.dark, Placement([s * 6.5, -1.6, -16]), H.base)
            p.reactor([s * 6.5, 0.7, -17.5], 2.2)

    return build_enemy_model("mortar", scene, N.mortar, draw)
