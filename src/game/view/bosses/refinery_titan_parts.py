# Copyright (c) 2026 Renaud Guillon
"""The Refinery Titan's destroyable parts (FB-REFINERY-TITAN-03).

Fuel bladders, rotary turrets and a missile brood, each drawn around its centre `at` (model space:
logical pixels, nose +Z, Y up).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.enemy_look import ENEMY_LOOK
from game.view.bosses.world_1_organic_kit import F, graft, polygon, vein_line
from game.view.enemies.enemy_shapes import decal
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
QUARTER = math.pi / 2
# Orange: the boss's neon (BOSS-50, FB-REFINERY-TITAN-04).
TITAN_NEON = BOSS_LOOK.neon["refinery-titan"]

# Heights the parts stand on: the tank beam, the turret sponson, the hull's back.
TITAN_DECK = {"beam": 3, "sponson": 8, "back": 13}


def rect(w: float, d: float, at: Any = None) -> list[Any]:
    """Return a rectangle `w` wide and `d` long around (x, z)."""
    x = 0 if at == None else at[0]
    z = 0 if at == None else at[1]
    return [
        [x - w / 2, z - d / 2],
        [x + w / 2, z - d / 2],
        [x + w / 2, z + d / 2],
        [x - w / 2, z + d / 2],
    ]


# A fuel tank lying along Z (a lathe profile along its axis): a capsule of octagonal section, a
# flat on top, ringed with glowing bands.
TANK_PROFILE = [
    [0, -22],
    [8, -21],
    [12.5, -17],
    [14, -10],
    [14, 10],
    [12.5, 17],
    [8, 21],
    [0, 22],
]
TANK_RADIUS = 14
# Where the bands sit along the tank, and the lit windows between them.
TANK_BANDS = [-13.2, -1.2, 10.8]
TANK_WINDOWS = [-6, 6]


def draw_tank(parts: Any, at_point: Vec3) -> None:
    """FB-REFINERY-TITAN-03: a big fuel bladder held in the limbs, a swollen sac of flesh.

    Orange bands of neon and glowing veins on it, grafted valves at its ends.
    """
    hull = parts.hull
    flesh = parts.flesh
    neon = parts.neon
    vein = parts.vein
    x = at_point[0]
    y = at_point[1]
    z = at_point[2]
    axis = y + TITAN_DECK["beam"] + 9

    # Pitched, the lathe's axis runs along +Z; rolled by an eighth of a turn, a flat faces up.
    def along(dz: float) -> Any:
        return Placement([x, axis, z + dz], 0, QUARTER, math.pi / 8)

    flesh.lathe(TANK_PROFILE, 8, F.slate, along(0))
    for dz in TANK_BANDS:
        neon.ring(TANK_RADIUS * 1.04, 2.4, 8, TITAN_NEON, along(dz))
    # The top flat of the octagon, a little above it: two lit windows and a valve.
    top = axis + TANK_RADIUS * math.cos(math.pi / 8)
    for dz in TANK_WINDOWS:
        decal(vein, rect(3.2, 7, [x, z + dz]), top + 0.05, TITAN_NEON)
    hull.cylinder(2.6, 3.2, 6, H.dark, Placement([x, top - 1.2, z + 15]), 1.8)
    hull.cylinder(2.6, 3.2, 6, H.dark, Placement([x, top - 1.2, z - 15]), 1.8)


# A rotary turret's base: a low faceted dome, its armoured barrel housing.
TURRET_BASE = [
    [12.5, 0],
    [13, 2.5],
    [10.5, 5.5],
    [6, 8],
    [0, 8.6],
]


def draw_turret(p: Any, at_point: Vec3) -> None:
    """FB-REFINERY-TITAN-03: a rotary turret's base on the front apron.

    A swollen growth plated round its crown, under its rotor (its mount, drawn by
    `build_boss_model`, BOSS-58).
    """
    x = at_point[0]
    y = at_point[1]
    z = at_point[2]
    base = y + TITAN_DECK["sponson"]
    p.flesh.lathe(TURRET_BASE, 8, F.graphite, Placement([x, base, z]))
    p.neon.ring(13.3, 0.9, 8, TITAN_NEON, Placement([x, base + 1, z]))
    graft(p, polygon(8, 9), [base + 5.6, base + 7], [x, 0, z], {"color": H.base})


# The block under the missile battery's ports.
BLOCK = [
    [-11, -13],
    [11, -13],
    [13.5, -9],
    [13.5, 10],
    [9, 13.5],
    [-9, 13.5],
    [-13.5, 10],
    [-13.5, -9],
]


def draw_missile_battery(p: Any, at_point: Vec3) -> None:
    """FB-REFINERY-TITAN-03: a missile brood on the body's back.

    A swollen mound under a grafted plate, its block of six missile ports on it (its mount, drawn by
    `build_boss_model`, BOSS-58).
    """
    hull = p.hull
    neon = p.neon
    x = at_point[0]
    y = at_point[1]
    z = at_point[2]
    base = y + TITAN_DECK["back"]
    top = base + 8
    p.flesh.bevel_slab(
        BLOCK,
        [base - 2, base, top - 1],
        [0, 3],
        F.slate,
        Placement([x, 0, z]),
        F.sinew,
    )
    hull.bevel_slab(
        BLOCK,
        [top - 1.2, top - 1.2, top],
        [0, 1],
        H.base,
        Placement([x, 0, z]),
        H.panel,
    )
    # Neon strips down both flanks of the block.
    for s in [-1, 1]:
        neon.box([0.6, 1.4, 16], TITAN_NEON, Placement([x + s * 12.6, base + 3.2, z]))
        vein_line(
            p,
            [x + s * 13, base, z - 12],
            [x + s * 22, base - 4, z - 20],
            [0, 2, 0],
            1,
            TITAN_NEON,
        )
