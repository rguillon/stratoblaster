# Copyright (c) 2026 Renaud Guillon
"""FB-OVERLORD-03: the Overlord's destroyable parts: wing laser cannons, missile batteries.

Shield generators, each drawn around its centre `at` (model space: logical pixels, nose +Z, Y up).
"""

import math

from game.config.enemy_look import ENEMY_LOOK
from game.view.bosses.overlord_city import OVERLORD_DECK, OVERLORD_NEON
from game.view.bosses.world_1_organic_kit import F, tentacle, vein_line
from game.view.enemies.enemy_shapes import around, radial, side_stripe
from render.geometry.organic import ROUND_SECTION
from render.geometry.solids import LoftOptions, Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


H = ENEMY_LOOK.hull

# Height of the wings' top, where the laser cannons sit.
WING_TOP = 2

# A laser cannon's pod (loft stations around its centre).
LASER_POD = [
    [-15, 5, -2, 5],
    [-6, 8, -3, 8],
    [8, 7, -2.5, 7],
    [15, 4, -1, 4.5],
]


def draw_laser(p: Any, at_point: Vec3) -> None:
    """FB-OVERLORD-03: a wing laser cannon: a swollen gland on the wing.

    Its laser (its mount, BOSS-58) sits on the gland's front.
    """
    neon = p.neon
    x = at_point[0]
    y = at_point[1]
    z = at_point[2]
    at = [x, y + WING_TOP - 1, z]
    p.flesh.loft(ROUND_SECTION, LASER_POD, F.slate, Placement(at))
    for side in [1, 3]:
        stripe = side_stripe(ROUND_SECTION, side, [0.25, 0.55])
        neon.loft(stripe, LASER_POD[0:3], OVERLORD_NEON, Placement(at), LoftOptions(True))
    # Bone fins on the gland's back, a vein between them.
    for s in [-1, 1]:
        tentacle(
            p,
            [x + s * 3.2, at[1] + 7, z - 10],
            [x + s * 4, at[1] + 10, z - 2],
            [0, 1, 0],
            [1.2, 0.2],
            F.bone,
            3,
        )
    vein_line(p, [x, at[1] + 8, z - 12], [x, at[1] + 8, z + 2], [0, 0.6, 0], 1.2, OVERLORD_NEON)


# A missile battery's block.
BATTERY = [
    [-10, -13],
    [10, -13],
    [12.5, -9],
    [12.5, 10],
    [8.5, 13.5],
    [-8.5, 13.5],
    [-12.5, 10],
    [-12.5, -9],
]


def draw_battery(p: Any, at_point: Vec3) -> None:
    """FB-OVERLORD-03: a missile brood on the mantle: a swollen mound under a grafted plate.

    Its six missile ports (its mount, BOSS-58) stand on the plate.
    """
    hull = p.hull
    neon = p.neon
    x = at_point[0]
    y = at_point[1]
    z = at_point[2]
    base = y + OVERLORD_DECK["top"]
    top = base + 8
    p.flesh.bevel_slab(
        BATTERY,
        [base - 1, base, top - 1],
        [0, 3],
        F.slate,
        Placement([x, 0, z]),
        F.sinew,
    )
    hull.bevel_slab(
        BATTERY,
        [top - 1.2, top - 1.2, top],
        [0, 1],
        H.base,
        Placement([x, 0, z]),
        H.panel,
    )
    vein_line(p, [x, base, z - 13], [x, base - 2, z - 22], [0, 1.5, 0], 1.1, OVERLORD_NEON)
    for s in [-1, 1]:
        neon.box([0.6, 1.4, 16], OVERLORD_NEON, Placement([x + s * 11.7, base + 3.2, z]))


# A shield generator's pedestal and glowing dome (lathe profiles, bottom to top).
PEDESTAL = [
    [12, 0],
    [12.5, 2],
    [10.5, 4.5],
    [0, 4.5],
]
DOME = [
    [8.5, 0],
    [7.5, 3.5],
    [4.5, 6],
    [0, 7],
]


def draw_generator(p: Any, at_point: Vec3) -> None:
    """FB-OVERLORD-03: a shield generator: a glowing neon gland in a ring of grafted coil.

    Swelling out of a flesh mound, three bone horns around it tipped with neon.
    """
    hull = p.hull
    neon = p.neon
    x = at_point[0]
    y = at_point[1]
    z = at_point[2]
    base = y + OVERLORD_DECK["top"]
    p.flesh.lathe(PEDESTAL, 8, F.graphite, Placement([x, base, z], math.pi / 8))
    neon.ring(12.6, 0.8, 8, OVERLORD_NEON, Placement([x, base + 0.6, z], math.pi / 8))
    neon.lathe(DOME, 8, OVERLORD_NEON, Placement([x, base + 4, z]))
    hull.ring(9.2, 1.6, 8, H.dark, Placement([x, base + 5.2, z]))
    for a in around(3):
        r = radial(a + math.pi / 3, 10.5, 0)
        horn = [x + r[0] * 1.1, base + 15, z + r[2] * 1.1]
        tentacle(p, [x + r[0], base + 3, z + r[2]], horn, [0, 0, 0], [1.6, 0.4], F.bone, 4)
        neon.box([1, 1, 1], OVERLORD_NEON, Placement(horn))
