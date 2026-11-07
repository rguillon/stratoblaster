# Copyright (c) 2026 Renaud Guillon
"""FB-AERIAL-ARK-01 to FB-AERIAL-ARK-04: the Aerial Ark, the Lab's L-20 final boss.

Logical pixels, nose +Z, Y up (towards the camera). A gigantic six-engine flying-wing mothership
seen from above: a long command fuselage down its middle under a raised bridge, the centre
section of its swept wing round it (a sawtooth trailing edge, its inner and middle engines podded
on it), the struts' sleeves at its joints. Its outer wing segments (tiles, rods, cables) are its
rig (`aerial_ark_rig`); its armour (the joints' fairings, the wing roots' and the nose's plating,
the tail hatch) and its parts' drawings are in `aerial_ark_parts`. A machine, not a creature: the
Lab's fourth round builds gigantic airplanes (user request, 2026-11-06).
"""

import math

from game.config.bosses.lab.aerial_ark import (
    AERIAL_ARK,
    BRIDGE,
    BRIDGE_GUN_AT,
    BRIDGE_HALF,
    BRIDGE_TOP,
    CENTRE_WING,
    FUSE_TOP,
    INNER_ENGINE,
    JOINT_X,
    MID_ENGINE,
    NOSE,
    ROTOR_AT,
    STRUT_HALF,
    STRUT_TOP,
    STRUT_X,
    STRUT_Y,
    TAIL,
    WING_Y,
)
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_shapes import edge_strips
from game.view.bosses.lab.aerial_ark_parts import N, ark_armour, barbette, saddle
from game.view.bosses.lab.aerial_ark_rig import ark_triangles, build_ark_rig, flat, nacelle, pt
from game.view.bosses.mini_boss_greebles import lamps, seam, vent
from game.view.bosses.world_1_organic_kit import F, M
from game.view.enemies.enemy_shapes import FIGHTER_SECTION
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


GLASS = [0.06, 0.08, 0.1]
# The fuselage's loft stations along Z (model: nose +Z), `[z, half width, bottom, top]`: its nose
# low under the nose plating (armour), its back at `FUSE_TOP`.
FUSELAGE: list[Any] = [
    [-TAIL, 5, 4, 10],
    [-46, 9, 1, 14.4],
    [-30, 11, 0, FUSE_TOP],
    [10, 12, 0, FUSE_TOP],
    [38, 11, 0, 13.6],
    [44, 10, 0.5, 10],
    [62, 6, 2, 9],
    [70, 3, 4, 7],
    [-NOSE, 0, 5.5, 5.5],
]


def _mirrored(right: list[list[float]]) -> list[list[Any]]:
    """Return a whole outline (model XZ) from its right half (config)."""
    points = [flat(q[0], q[1]) for q in right]
    points.extend([flat(-q[0], q[1]) for q in reversed(right)])
    return points


def _fuselage(p: Any) -> None:
    """Draw the command fuselage (FB-AERIAL-ARK-02).

    A long, faceted hull of dark plating, a light down each shoulder, seams across its back, the
    raised bridge (a glazed band round it, the bridge gun's seat on its roof), the tail rotor's
    seat, two canted fins at its tail and a lit cargo ramp between them.
    """
    p.hull.loft(FIGHTER_SECTION, FUSELAGE, M.base)
    for s in [-1, 1]:
        edge_strips(
            p.neon, [[s * 6.4, -30], [s * 7, -10], [s * 7, 10], [s * 6.6, 34]], 0.6, [8.6, 9.3], N
        )
    for z in [-24, 0, 26]:
        p.bare.box([16, 0.3, 0.7], M.dark, Placement([0, FUSE_TOP - 0.2, z]))
    vent(p.hull, [0, FUSE_TOP - 0.2, 6], [6, 6], 4)
    # The bridge: a raised block, a band of smoked glass round it, its roof.
    bridge = [
        flat(-BRIDGE_HALF + 2, BRIDGE[0]),
        flat(BRIDGE_HALF - 2, BRIDGE[0]),
        flat(BRIDGE_HALF, BRIDGE[0] + 4),
        flat(BRIDGE_HALF, BRIDGE[1]),
        flat(-BRIDGE_HALF, BRIDGE[1]),
        flat(-BRIDGE_HALF, BRIDGE[0] + 4),
    ]
    p.hull.bevel_slab(
        bridge, [FUSE_TOP - 1, BRIDGE_TOP - 1, BRIDGE_TOP], [0, 0.8], M.panel, None, M.base
    )
    p.bare.slab(bridge, [BRIDGE_TOP - 3.4, BRIDGE_TOP - 1.8], GLASS)
    seat = pt(BRIDGE_GUN_AT[0], BRIDGE_GUN_AT[1], BRIDGE_TOP - 0.4)
    p.hull.cylinder(6.2, 0.6, 8, M.dark, Placement(seat, math.pi / 8))
    p.neon.box([BRIDGE_HALF * 2 - 3, 0.4, 0.6], N, Placement(pt(0, BRIDGE[1] - 1, BRIDGE_TOP)))
    rotor = pt(ROTOR_AT[0], ROTOR_AT[1], FUSE_TOP - 1.4)
    p.hull.cylinder(6.6, 1.4, 8, M.panel, Placement(rotor, math.pi / 8))
    # Its tail: two canted fins, the cargo ramp lit between them.
    for s in [-1, 1]:
        fin = [flat(s * 6, 42), flat(s * 6, 55), flat(s * 7.6, 56), flat(s * 7.6, 48)]
        p.hull.slab(fin, [9, 22], M.panel, None, M.base)
        p.neon.box([0.5, 0.5, 6], N, Placement(pt(s * 6.8, 52, 22)))
    p.bare.box([7, 0.3, 8], M.dark, Placement(pt(0, 50, 11.2)))
    for k in range(3):
        p.neon.box([6, 0.3, 0.4], N, Placement(pt(0, 47 + k * 3, 11.4)))


def _wing(p: Any) -> None:
    """Draw the centre section of the wing (FB-AERIAL-ARK-02).

    A wide, thick plate swept back from the fuselage to its joints, a light along each leading
    edge, a dark sawtooth trim along its trailing edge, panel lines and vents, the dark rib along
    each joint and the strut's sleeve out of it (the orb stands on it).
    """
    p.flesh.bevel_slab(_mirrored(CENTRE_WING), WING_Y, [0.6, 1.4], F.graphite, None, F.slate)
    top = WING_Y[2]
    for s in [-1, 1]:
        lead = [flat(s * q[0], q[1]) for q in CENTRE_WING[0:2]]
        edge_strips(
            p.neon,
            [[lead[0][0], lead[0][1] - 1.4], [lead[1][0], lead[1][1] - 1.4]],
            0.7,
            [top - 0.6, top + 0.1],
            N,
        )
        trail = [flat(s * q[0], q[1] - 1) for q in CENTRE_WING[2:6]]
        edge_strips(p.bare, trail, 1.2, [top - 0.3, top + 0.2], M.dark)
        seam(p.hull, flat(s * 14, -30), flat(s * 14, 34), [top, 0.5, 0.3])
        seam(p.hull, flat(s * 36, -22), flat(s * 36, 12), [top, 0.5, 0.3])
        vent(p.hull, pt(s * 26, 30, top - 0.2), [5, 3], 3, s * 0.3)
        # The joint: a dark rib along it.
        rib = [
            flat(s * (JOINT_X - 1.4), CENTRE_WING[1][1] + 0.6),
            flat(s * JOINT_X, CENTRE_WING[1][1] + 0.6),
            flat(s * JOINT_X, CENTRE_WING[2][1] - 0.6),
            flat(s * (JOINT_X - 1.4), CENTRE_WING[2][1] - 0.6),
        ]
        p.hull.slab(rib, [WING_Y[0] + 0.4, top + 0.6], M.dark)
        # The strut's sleeve, out of the joint: the orb stands on it.
        sleeve = [
            flat(s * STRUT_X[0], STRUT_Y - STRUT_HALF),
            flat(s * STRUT_X[1], STRUT_Y - STRUT_HALF),
            flat(s * STRUT_X[1], STRUT_Y + STRUT_HALF),
            flat(s * STRUT_X[0], STRUT_Y + STRUT_HALF),
        ]
        p.hull.bevel_slab(
            sleeve, [WING_Y[1] - 1.5, STRUT_TOP - 0.6, STRUT_TOP], [0, 0.6], M.panel, None, M.base
        )
        p.bare.box(
            [1.2, 3, STRUT_HALF * 2 - 2.4],
            M.dark,
            Placement(pt(s * (STRUT_X[1] - 0.4), STRUT_Y, WING_Y[1] - 0.6)),
        )
        lamps(p.neon, [pt(s * 40, -36 + 0.545 * 29 + 2.5, top)], 1.2, N)


def _engines(p: Any) -> None:
    """Draw the inner and middle engines' nacelles on the centre section (FB-AERIAL-ARK-02)."""
    for s in [-1, 1]:
        for engine in [INNER_ENGINE, MID_ENGINE]:
            nacelle(p, s * engine[0], engine[1], engine[2])


def build_aerial_ark(scene: Any) -> Any:
    """FB-AERIAL-ARK-01, FB-AERIAL-ARK-04: the Aerial Ark.

    A six-engine flying-wing mothership about 5.3 L across, near-white lights (shown yellow):
    its engines' turrets, lasers and missile blocks, its bridge gun and tail rotor (their mounts,
    drawn by `build_boss_model`, BOSS-58). Its wing splits, then comes round into a halo, as it
    transforms (FB-AERIAL-ARK-05, FB-AERIAL-ARK-11).
    """

    def core(p: Any) -> None:
        _fuselage(p)
        _wing(p)
        _engines(p)

    return build_boss_model(
        AERIAL_ARK,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "engine-outer-left": barbette,
                "engine-outer-right": barbette,
                "engine-inner-left": barbette,
                "engine-inner-right": barbette,
                "engine-mid-left": saddle,
                "engine-mid-right": saddle,
            },
            # FB-AERIAL-ARK-05, FB-AERIAL-ARK-11: its outer segments split, then form the halo.
            "rig": {"build": build_ark_rig, "triangles": ark_triangles},
            "armour": ark_armour(),
        },
    )
