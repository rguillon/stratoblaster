# Copyright (c) 2026 Renaud Guillon
"""FB-CRESCENT-HALO-01 to FB-CRESCENT-HALO-04, Lab L-5: the Crescent Halo.

Logical pixels, nose +Z, Y up (towards the camera). A living station shaped as a crescent open at
its front: a thick ring of flesh under shell plates and bone ribs, pale gold veins round its rims,
its core a floating organ in the hollow tethered to the ring by three sinews. Its horns, its flank
plates and its crest are drawn as pieces of their own (`crescent_halo_parts`).
"""

import math

from game.config.bosses.lab.crescent_halo import (
    CRESCENT_HALO,
    EYE_AT,
    EYE_HEIGHT,
    HALO_ARC,
    HALO_AXIS,
    HALO_GIRTH,
    HALO_RADIUS,
    ORGAN_CROWN,
    ORGAN_RADIUS,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.crescent_halo_parts import (
    RING_TOP,
    N,
    arc,
    back_growth,
    flank_gland,
    halo_armour,
    horn_growth,
    ring_model,
    tangent_yaw,
    tether,
)
from game.view.bosses.mini_boss_shapes import offset
from game.view.bosses.world_1_organic_kit import F, M, gland, graft, polygon
from game.view.enemies.organic_parts import eyes, reactor_sac
from render.geometry.organic import tendril, vein
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


# The ring's stretches, round the back from one end to the other, in alternate shades.
STRETCH = 30
# Where the shell plates and the bone ribs lie on the ring (degrees from the nose, right side;
# mirrored), clear of the parts' growths.
SHELLS = [135, 163]
RIBS = [110, 140, 166]
# The organ's profile (radius, height), from its underside up to its crown.
ORGAN = [
    [0, 2],
    [ORGAN_RADIUS * 0.6, 3],
    [ORGAN_RADIUS * 0.92, 7],
    [ORGAN_RADIUS, 12],
    [ORGAN_RADIUS * 0.92, 17],
    [ORGAN_RADIUS * 0.7, 22],
    [ORGAN_RADIUS * 0.38, ORGAN_CROWN - 0.3],
    [0, ORGAN_CROWN],
]


def _mirrored(angles: list[Any]) -> list[float]:
    """Return `angles` and their mirror images across the centre line."""
    result: list[float] = []
    for a in angles:
        result.append(a)
        result.append(360 - a)
    return result


def _draw_ring(p: Any) -> None:
    """Draw the ring (FB-CRESCENT-HALO-02): a thick tube of flesh round the back.

    Shell plates over it, bone ribs arching over it, pale gold veins round its inner and outer rims.
    """
    start = HALO_ARC[0]
    end = 360 - HALO_ARC[0]
    count = math.ceil((end - start) / STRETCH)
    for k in range(count):
        a0 = start + (end - start) * k / count
        a1 = start + (end - start) * (k + 1) / count
        path = arc([a0, a1], HALO_RADIUS, HALO_AXIS, 6)
        tendril(p.flesh, path, [HALO_GIRTH, HALO_GIRTH], 8, F.slate if k % 2 == 0 else F.graphite)
    for a in _mirrored(SHELLS):
        p.flesh.bevel_slab(
            polygon(6, HALO_GIRTH + 0.4, [1, 0.85]),
            [RING_TOP - 4, RING_TOP - 1, RING_TOP + 1],
            [0, 1.4],
            F.membrane,
            Placement(ring_model(a, HALO_RADIUS, 0), tangent_yaw(a)),
            F.graphite,
        )
    for a in _mirrored(RIBS):
        rib = [
            ring_model(a, HALO_RADIUS - HALO_GIRTH - 0.5, HALO_AXIS),
            ring_model(a, HALO_RADIUS - HALO_GIRTH * 0.6, RING_TOP - 0.5),
            ring_model(a, HALO_RADIUS + HALO_GIRTH * 0.6, RING_TOP - 0.5),
            ring_model(a, HALO_RADIUS + HALO_GIRTH + 0.5, HALO_AXIS),
        ]
        tendril(p.flesh, rib, [1, 1], 4, F.bone)
    for radius in [HALO_RADIUS - HALO_GIRTH + 1.2, HALO_RADIUS + HALO_GIRTH - 1.2]:
        rim = arc([start + 2, end - 2], radius, HALO_AXIS + 6.4, 8)
        vein(p.vein, rim, 1.1, N)


def _draw_organ(p: Any) -> None:
    """Draw the core (FB-CRESCENT-HALO-02): a floating organ in the hollow.

    A swollen heart of flesh under a dark metal cage band, pale gold veins running down from its
    crown, the seats of its rotor (on its crown) and of its eye turret (on its front), eyes either
    side of it, and the three sinews tethering it to the ring.
    """
    p.flesh.lathe(ORGAN, 10, F.sinew, Placement([0, 0, 0], math.pi / 10))
    p.hull.ring(ORGAN_RADIUS + 0.3, 2.4, 10, M.base, Placement([0, 10.8, 0], math.pi / 10))
    p.neon.ring(ORGAN_RADIUS + 0.45, 0.5, 10, N, Placement([0, 11.8, 0], math.pi / 10))
    for k in range(6):
        a = 2 * math.pi * (k + 0.5) / 6
        c = math.cos(a)
        s = math.sin(a)
        path = [[c * r, h + 0.4, s * r] for r, h in [[6.5, 24.4], [12, 22.6], [16.5, 18.6]]]
        vein(p.vein, path, 1, N)
    p.hull.cylinder(7, 1.6, 10, M.base, Placement([0, ORGAN_CROWN - 1.6, 0]))
    p.neon.ring(7.1, 0.4, 10, N, Placement([0, ORGAN_CROWN - 0.9, 0]))
    eye = boss_point(EYE_AT[0], EYE_AT[1], EYE_HEIGHT - 2.2)
    p.hull.cylinder(5.6, 2.2, 8, M.base, Placement(eye))
    graft(p, polygon(5, 4.5, [1.4, 1]), [EYE_HEIGHT - 2.6, EYE_HEIGHT - 2], offset(eye, 0, 0, -3))
    for s in [-1, 1]:
        eyes(p, [s * 8, 18.5, 14.8], {"count": 2, "size": 1.1, "spacing": 3}, N)
        gland(p, [s * 14, 19, -6], 1.3, N)
    for a in [115, 180, 245]:
        tether(p, a, ORGAN_RADIUS)


def _draw_organs(p: Any) -> None:
    """Draw the reactor sacs on the ring's outer rim, behind the flanks, and its glands."""
    for a in _mirrored([138]):
        reactor_sac(p, ring_model(a, HALO_RADIUS + HALO_GIRTH - 1, HALO_AXIS + 2), 3, N, F.graphite)
    for a in _mirrored([108, 175]):
        gland(p, ring_model(a, HALO_RADIUS + 5, RING_TOP - 1.6), 1.2, N)
    p.reactor(ring_model(180, HALO_RADIUS + HALO_GIRTH, HALO_AXIS), 3)


def build_crescent_halo(scene: Any) -> Any:
    """FB-CRESCENT-HALO-01, FB-CRESCENT-HALO-04: the Crescent Halo.

    A crescent-shaped living station 4.5 L across, open at its front, pale gold veins round its
    rims; its six growths round the crescent carry its rotors, lasers and turrets, its floating
    organ the core's rotor and eye turret (their mounts, BOSS-58). Its horns swing closed into a
    full halo at its first transformation (FB-CRESCENT-HALO-05).
    """

    def core(p: Any) -> None:
        _draw_ring(p)
        _draw_organ(p)
        _draw_organs(p)

    return build_boss_model(
        CRESCENT_HALO,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "horn-left": horn_growth,
                "horn-right": horn_growth,
                "flank-left": flank_gland,
                "flank-right": flank_gland,
                "back-left": back_growth,
                "back-right": back_growth,
            },
            "armour": halo_armour(),
        },
    )
