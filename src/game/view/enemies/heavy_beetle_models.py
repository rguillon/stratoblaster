# Copyright (c) 2026 Renaud Guillon
"""The Bulwark and the Splitter, Cyber-Organic (ENM-35) Logical pixels, nose +Z, Y up."""

import math

from game.config.enemies import ENEMY_CONFIG
from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies.enemy_mesh import build_enemy_model
from game.view.enemies.enemy_shapes import around, radial
from render.geometry.organic import (
    organ,
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


def splitter_pod_outline(offset: float, inner: float, outer: float) -> list[list[float]]:
    """Return a Splitter pod: a wedge fitted around the core.

    It runs from `inner` to `outer` from the core's centre, outwards along +Z, around its own centre
    `offset` out.
    """

    def rim(a: float) -> list[float]:
        return [outer * math.sin(a), outer * math.cos(a) - offset]

    return [[-4, inner - offset], rim(-0.42), rim(-0.21), rim(0.21), rim(0.42), [4, inner - offset]]


def pod(flesh: Any, hull: Any, neon: Any, veins: Any, place: Any) -> None:
    """ENM-SPLITTER-03: a pod of the Splitter, a curled flesh grub.

    It has a swollen body, a metal plate grafted on its back, a neon seam along its inner side and a
    vein across it.
    """
    offset = ENEMY_CONFIG.splitter.podOffset
    inner = 8.3
    body = splitter_pod_outline(offset, inner, 16.4)
    flesh.bevel_slab(body, [-2.2, 0.4, 2.4], [0.8, 1.6], F.slate, place, F.graphite)
    hull.bevel_slab(
        splitter_pod_outline(offset, 10.4, 14.4), [2.2, 2.2, 3], [0, 0.6], H.panel, place
    )
    z0 = inner - offset - 0.45
    seam = [[-4.3, z0], [4.3, z0], [4.3, z0 + 0.4], [-4.3, z0 + 0.4]]
    neon.slab(seam, [-1.6, 1.8], N.splitter, place)
    z = 15.6 - offset
    vein_tube(
        veins,
        [[-5, 2.4, z - 1], [0, 2.6, z], [5, 2.4, z - 1]],
        0.8,
        N.splitter,
        place,
    )


def build_splitter(scene: Any) -> Any:
    """ENM-SPLITTER-01: a body visibly made of the three grubs it splits into.

    They are curled around a small flesh heart with a neon ring (yellow, ENM-SPLITTER-04), its eye
    charging before it dives, and one reactor (ENM-SPLITTER-02).
    """
    offset = ENEMY_CONFIG.splitter.podOffset

    def draw(p: Any) -> None:
        flesh = p.flesh
        hull = p.hull
        neon = p.neon
        charge = p.charge
        reactor = p.reactor
        organ(flesh, 8.6, 6, F.graphite, Placement([0, -3, 0]), 0.4)
        neon.ring(8.4, 0.7, 6, N.splitter, Placement([0, 0.6, 0]))
        for a in around(3):
            pod(flesh, hull, neon, p.vein, Placement(radial(a, offset, 0), a))
        eye = [[0, 0], [2.2, 0.4], [0, 1.4]]
        charge.lathe(eye, 6, WHITE, Placement([0, 4, 0]))
        reactor([0, 0, -7.8], 1.6)

    return build_enemy_model("splitter", scene, N.splitter, draw)


def build_splitter_pod(scene: Any) -> Any:
    """ENM-SPLITTER-03: a grub broken off a Splitter, diving outer side first."""
    pod_offset = ENEMY_CONFIG.splitter.podOffset

    def draw(p: Any) -> None:
        pod(p.flesh, p.hull, p.neon, p.vein, None)
        p.reactor([0, 0, 8.3 - pod_offset], 1)

    return build_enemy_model("splitter-pod", scene, N.splitter, draw)
