# Copyright (c) 2026 Renaud Guillon
"""The Hydra (specs/enemies/hydra.md) Logical pixels, nose +Z, Y up (towards the camera)."""

import math

from game.config.enemies_elite import ELITE_CONFIG
from game.config.enemy_look import ENEMY_LOOK
from game.config.enemy_look_elite import ELITE_NEON
from game.view.bosses.boss_limbs import boss_point
from game.view.enemies.elite_shapes import QUARTER, WHITE, H, ahead
from game.view.enemies.enemy_shapes import SIDES
from game.view.enemies.jointed_model import build_jointed_model
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import (
    SegmentedBody,
    carapace,
    curve,
    plate,
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


CFG = ELITE_CONFIG.hydra
NEON = ELITE_NEON.hydra
F = ENEMY_LOOK.flesh


def _shell_girth(t: float) -> float:
    return 0.5 + 0.5 * math.sin(math.pi * min(1, t * 1.15))


# ENM-HYDRA-02: the broad, armoured shell (tail to front) and the bone ridge along its back.
SHELL = SegmentedBody(-21.5, 8, 4, 22, -4, 6, None, _shell_girth, [False, False])
# The metal plates grafted on its shoulders (right side).
PLATES = [  # type: list[list[list[float]]]
    [[6, 4], [17, 0], [16, -8], [6, -6]],
    [[5, -10], [14, -12], [10, -19], [4, -17]],
]
# How high the necks and heads ride.
NECK_Y = 1.5
# A head around its centre, along +Z: a swollen skull closing towards its eye.
HEAD = SegmentedBody(-5, 6.5, 2, 4.8, -2.4, 3.2)
# The right mandible, beside the skull (mirrored for the left).
JAW = [[2.5, -1], [4.6, 1], [3.6, 6.5], [2.4, 3]]  # type: list[list[float]]
# The missile tube on a head's brow (ENM-HYDRA-15): its radius and length, mouth at the eye.
TUBE = [1.5, 6]  # type: list[float]


def body(p: Any) -> None:
    """Add the shell: its plates, ridge and veins (ENM-HYDRA-03).

    The reactors in sacs at its tail (ENM-HYDRA-04).
    """
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    vein = p.vein
    carapace(flesh, SHELL, [F.teal, F.graphite])
    tendril(flesh, curve([0, 5.5, -19], [0, 6, 4], [0, 2.5, 0], 3), [1.6, 0.8], 4, F.bone)
    for s in SIDES:
        for i, pl in enumerate(PLATES):
            outline = [[s * pt[0], pt[1]] for pt in pl]
            # The front plates riveted, the back ones plain (lean on triangles).
            if i == 0:
                plate(hull, outline, [4.4, 5.6], [H.panel, H.dark])
            else:
                hull.bevel_slab(outline, [4.4, 4.4, 5.6], [0, 0.6], H.panel)
        vein_tube(vein, curve([s * 3, 5.6, -17], [s * 5, 5.4, 4], [s * 3, 1, 0], 3), 0.9, NEON)
        reactor_sac(p, [s * 8, 0.5, -21.5], 2.2, NEON, F.teal)
    # Teal lights along the front edge, where the necks grow out.
    neon.box([30, 0.6, 1.2], NEON, Placement([0, 4.2, 6.2]))


def neck(head: Any) -> Any:
    """Return a neck from its joint to its head (ENM-HYDRA-05).

    A flesh tendril ringed with teal and metal collars.
    """
    px = head.pivot[0]
    py = head.pivot[1]
    hx = head.head[0]
    hy = head.head[1]
    aim = head.aim
    length = math.hypot(hx - px, hy - py) - 3
    at = boss_point(px, py, NECK_Y)

    def draw(p: Any) -> None:
        hull = p.hull
        flesh = p.flesh
        neon = p.neon
        path = [ahead(at, aim, t * length) for t in [0, 0.33, 0.66, 1]]
        tendril(flesh, path, [3, 2], 5, F.teal)
        for t in [0.35, 0.7]:
            pt = ahead(at, aim, t * length)
            r = 3.3 - 1.1 * t
            hull.ring(r, 1.2, 5, H.panel, Placement([pt[0], NECK_Y - 0.6, pt[2]], aim, QUARTER))
            neon.box([2 * r, 0.4, 0.6], NEON, Placement([pt[0], NECK_Y + r - 0.2, pt[2]], aim))

    return draw


def head(spec: Any) -> Any:
    """Return a head on its neck: a skull with bone mandibles and a missile tube on its brow.

    The tube's mouth is the eye, where the missile leaves, with a charge light in it (ENM-HYDRA-15).
    """
    at = boss_point(spec.head[0], spec.head[1], NECK_Y)
    aim = spec.aim
    eye = boss_point(spec.muzzle[0], spec.muzzle[1], spec.muzzle[2])

    def draw(p: Any) -> None:
        hull = p.hull
        flesh = p.flesh
        neon = p.neon
        muzzle = p.muzzle
        segmented_body(flesh, HEAD, F.teal, Placement(at, aim))
        tube = Placement(ahead(eye, aim, -TUBE[1]), aim, QUARTER)
        hull.cylinder(TUBE[0], TUBE[1], 5, H.dark, tube)
        p.charge.cylinder(
            TUBE[0] * 1.1, 0.6, 5, WHITE, Placement(ahead(eye, aim, -0.6), aim, QUARTER)
        )
        for s in SIDES:
            jaw = [[s * pt[0], pt[1]] for pt in JAW]
            flesh.bevel_slab(jaw, [-1.2, 0, 1], [0.2, 0.4], F.bone, Placement(at, aim))
        lens = [[0, -0.8], [1.5, 0], [0, 0.8]]
        neon.lathe(lens, 6, NEON, Placement([eye[0], eye[1] - 0.6, eye[2]]))
        muzzle(eye, "gun")

    return draw


def build_hydra(scene: Any) -> Any:
    """ENM-HYDRA-01: a broad, plated hydra with three long flesh necks forward.

    Each neck ends in a teal-eyed head, within the elite triangle budget (ENM-HYDRA-06).
    """
    limbs = {}
    parts = {}
    for h in CFG.heads:
        limbs[h.joint] = neck(h)
        parts[h.id] = head(h)
    return build_jointed_model(
        "hydra", scene, NEON, CFG.design, {"body": body, "limbs": limbs, "parts": parts}
    )
