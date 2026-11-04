# Copyright (c) 2026 Renaud Guillon
"""The Juggernaut (specs/enemies/juggernaut.md).

Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from game.config.enemies_elite import ELITE_CONFIG
from game.config.enemy_look import ENEMY_LOOK
from game.config.enemy_look_elite import ELITE_NEON
from game.view.bosses.boss_limbs import boss_point
from game.view.enemies.basic_parts import config_barrels
from game.view.enemies.elite_shapes import QUARTER, H, barrel
from game.view.enemies.enemy_shapes import SIDES, angry_eyes
from game.view.enemies.jointed_model import build_jointed_model
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import (
    SegmentedBody,
    carapace,
    curve,
    plate,
    segmented_body,
)
from render.geometry.organic import (
    vein as vein_tube,
)
from render.geometry.solids import Placement

# isort: split
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


CFG = ELITE_CONFIG.juggernaut
NEON = ELITE_NEON.juggernaut
F = ENEMY_LOOK.flesh


def _body_girth(t: float) -> float:
    return 0.7 + 0.3 * math.sin(math.pi * t)


# ENM-JUGGERNAUT-01: the massive, wide body (tail to front) and the ridged shell over it.
BODY = SegmentedBody(-24, 12, 3, 24, -4, 3, None, _body_girth, [False, False])
SHELL = SegmentedBody(-23, 11, 3, 19, 0, 4.8, None, None, [False, False])
# The metal plate bolted on its back, under the turret.
BACK_PLATE = [[-9, -14], [9, -14], [11, 4], [-11, 4]]  # type: list[list[float]]
# The back turret carrying the core's twin cannon.
TURRET = {"radius": 6.5, "z": -3, "y": 4.6, "height": 3.2}
# A cannon's flesh pod around its centre, along +Z.
POD = SegmentedBody(-6, 5, 2, 5.2, -2.5, 4.2)
# A front plate around its centre: a thick, chamfered slab.
PLATE = [  # type: list[list[float]]
    [-8.5, -6],
    [8.5, -6],
    [9.5, 1.5],
    [6.5, 7],
    [-6.5, 7],
    [-9.5, 1.5],
]


def body(p: Any) -> None:
    """Add the armoured beast: a flesh body under a plated shell, the turret, its eyes and strips.

    Its eyes and strips are ENM-JUGGERNAUT-03, its reactor sacs ENM-JUGGERNAUT-05.
    """
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    vein = p.vein
    # ENM-JUGGERNAUT-02: the swollen body, and the metal shell bolted over its back.
    segmented_body(flesh, BODY, F.sinew)
    carapace(flesh, SHELL, [F.slate, F.sinew])
    plate(hull, BACK_PLATE, [3.6, 5.2], [H.base, H.dark])
    for slit in angry_eyes([0, 6], 6, [8, 1.4], 0.25):
        neon.slab(slit, [4.5, 4.9], NEON)
    for x in [-15, 15]:
        neon.box([1.4, 0.4, 20], NEON, Placement([x, 4.5, -10]))
    for s in SIDES:
        vein_tube(vein, curve([s * 4, 5.4, -20], [s * 11, 4.8, 6], [s * 4, 0.6, 0], 2), 1, NEON)
    hull.cylinder(
        TURRET["radius"], TURRET["height"], 8, H.panel, Placement([0, TURRET["y"], TURRET["z"]])
    )
    # A bank of seven fixed barrels on the back turret, fanned (WPN-01, WPN-03).
    config_barrels(p, CFG.muzzles, 7, 0.6)
    for x in [-10, 10]:
        reactor_sac(p, [x, 0.5, -24.5], 2.4, NEON, None, 4)
    p.reactor([0, 0.5, -24.5], 2.4)


def shoulder(cannon: Any) -> Any:
    """Return a shoulder mount, a metal joint turning with its joint, a sinew into the body."""
    at = boss_point(cannon.pivot[0], cannon.pivot[1], -2.5)

    def draw(p: Any) -> None:
        p.hull.cylinder(5, 7, 6, H.dark, Placement(at))

    return draw


def cannon(spec: Any) -> Any:
    """Return a shoulder cannon (ENM-JUGGERNAUT-06): a flesh pod in a metal band.

    It has a steel-blue gland and a long barrel.
    """
    at = boss_point(spec.centre[0], spec.centre[1], 0)
    tip = boss_point(spec.muzzle[0], spec.muzzle[1], spec.muzzle[2])

    def draw(p: Any) -> None:
        segmented_body(p.flesh, POD, F.slate, Placement(at))
        p.hull.ring(4.9, 1.4, 6, H.panel, Placement([at[0], at[1] + 0.8, at[2] - 0.5], 0, QUARTER))
        p.vein.box([1.2, 0.5, 6], NEON, Placement([at[0], at[1] + 4.4, at[2]]))
        p.neon.box([0.6, 0.4, 3], NEON, Placement([at[0], at[1] + 4.6, at[2] - 4]))
        barrel(p, tip, 0, [1.4, 8])

    return draw


def front_plate(spec: Any) -> Any:
    """Return a front armour plate, riveted on, a steel-blue light along its edge."""
    at = boss_point(spec.x, spec.y, 0)

    def draw(p: Any) -> None:
        hull = p.hull
        neon = p.neon
        hull.bevel_slab(PLATE, [-3, 0, 5], [1, 2.2], H.panel, Placement(at), H.base)
        for xz in [[-5, 4], [5, 4], [-6, -3], [6, -3]]:
            hull.box([1, 0.6, 1], H.dark, Placement([at[0] + xz[0], 5.2, at[2] + xz[1]]))
        neon.box([10, 0.5, 1.2], NEON, Placement([at[0], 4.6, at[2] + 3.5]))

    return draw


def build_juggernaut(scene: Any) -> Any:
    """ENM-JUGGERNAUT-01: a massive, armoured beast with two riveted front plates.

    It has a flesh cannon pod on each shoulder, within the elite triangle budget
    (ENM-JUGGERNAUT-07).
    """
    limbs = {}
    parts = {}
    for c in CFG.cannons:
        limbs[c.joint] = shoulder(c)
        parts[c.id] = cannon(c)
    for pl in CFG.plates:
        parts[pl.id] = front_plate(pl)
    return build_jointed_model(
        "juggernaut", scene, NEON, CFG.design, {"body": body, "limbs": limbs, "parts": parts}
    )
