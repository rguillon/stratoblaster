# Copyright (c) 2026 Renaud Guillon
"""FB-AERIAL-ARK-03, FB-AERIAL-ARK-05, FB-AERIAL-ARK-11: the Aerial Ark's armour and parts.

Logical pixels, nose +Z, Y up (towards the camera). Its armour regions' drawings (the fairing
over each wing joint, shed as the wing splits; the plating of its wing roots and of its nose,
shed as it becomes a halo; the hatch over its tail rotor) and its parts' drawings: the armoured
gun sections round its engines' nacelles (turrets and lasers stand on them) and the saddles on
its middle engines (their missile blocks).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.aerial_ark import (
    FAIRING_Y,
    FUSE_TOP,
    JOINT_FAIRING,
    JOINT_X,
    NACELLE_AXIS,
    NACELLE_R,
    NACELLE_TOP,
    NOSE_PLATING,
    NOSE_Y,
    PLATING_Y,
    ROOT_PLATING,
    ROTOR_AT,
    STRUT_TOP,
    STRUT_X,
    STRUT_Y,
    WING_Y,
)
from game.view.bosses.lab.aerial_ark_rig import flat, pt
from game.view.bosses.mini_boss_greebles import lamps, seam
from game.view.bosses.world_1_organic_kit import M
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["aerial-ark"]
QUARTER = math.pi / 2
GLASS = [0.06, 0.08, 0.1]


def _outline(points: list[Any], side: float) -> list[Any]:
    return [flat(side * q[0], q[1]) for q in points]


def draw_joint(p: Any) -> None:
    """Draw the fairing over each wing joint (FB-AERIAL-ARK-05): a long blister across the split.

    Plated, its seam lit along the line the wing splits at, bolts either side of it.
    """
    for s in [-1, 1]:
        p.hull.bevel_slab(
            _outline(JOINT_FAIRING, s),
            [FAIRING_Y[0], FAIRING_Y[1] - 1.6, FAIRING_Y[1]],
            [0, 2.2],
            M.panel,
            None,
            M.base,
        )
        p.neon.box([0.6, 0.4, 13], N, Placement(pt(s * JOINT_X, -2, FAIRING_Y[1] - 0.1)))
        lamps(
            p.neon,
            [pt(s * (JOINT_X + dx), y, FAIRING_Y[1] - 0.3) for dx in [-3, 3] for y in [-6, 2]],
            0.8,
            N,
        )


def draw_joint_frame(p: Any) -> None:
    """Draw what each fairing leaves (BOSS-44): the joint's dark socket, a lit collar on the sleeve.

    The orb stands on the sleeve, in the collar.
    """
    for s in [-1, 1]:
        socket = [[37, -10], [JOINT_X, -10], [JOINT_X, 6], [37, 6]]
        p.hull.slab(_outline(socket, s), [WING_Y[2] - 0.4, WING_Y[2] + 0.4], M.dark)
        p.neon.ring(6.6, 0.4, 10, N, Placement(pt(s * JOINT_X, STRUT_Y, STRUT_TOP - 0.3)))
        for x in [STRUT_X[0] + 1, JOINT_X - 1.5]:
            p.bare.box([0.8, 0.5, 14], M.base, Placement(pt(s * x, -2, WING_Y[2] + 0.3)))


def draw_root_plating(p: Any) -> None:
    """Draw the plating of the wing roots (FB-AERIAL-ARK-11): thick slabs, seams, a lit slit."""
    for s in [-1, 1]:
        p.hull.bevel_slab(
            _outline(ROOT_PLATING, s),
            [PLATING_Y[0], PLATING_Y[1] - 1, PLATING_Y[1]],
            [0, 1],
            M.panel,
            None,
            M.base,
        )
        top = PLATING_Y[1]
        seam(p.hull, flat(s * 21, -24), flat(s * 21, -7), [top, 0.5, 0.3])
        seam(p.hull, flat(s * 14, -15), flat(s * 29.5, -15), [top, 0.5, 0.3])
        p.neon.box([0.6, 0.4, 8], N, Placement(pt(s * 27, -12, top - 0.2), s * 0.2))


def draw_nose_plating(p: Any) -> None:
    """Draw the nose plating (FB-AERIAL-ARK-11): the armoured command deck over the nose.

    A tapering slab over the fuselage, its windscreen of smoked glass at its front, side windows
    and a light down its middle.
    """
    p.hull.bevel_slab(
        [flat(q[0], q[1]) for q in NOSE_PLATING],
        [NOSE_Y[0], NOSE_Y[1] - 1.5, NOSE_Y[1]],
        [0, 1.6],
        M.panel,
        None,
        M.base,
    )
    top = NOSE_Y[1]
    screen = [flat(0, -64.5), flat(5, -61), flat(6, -57), flat(-6, -57), flat(-5, -61)]
    p.bare.slab(screen, [top - 1.2, top + 0.15], GLASS)
    for s in [-1, 1]:
        p.bare.box([0.6, 0.8, 8], GLASS, Placement(pt(s * 8.4, -48, top - 1.6), s * 0.05))
    p.neon.box([0.6, 0.4, 14], N, Placement(pt(0, -47, top)))


def draw_hatch(p: Any) -> None:
    """Draw the hatch over the tail rotor (BOSS-58): an octagonal cap, a lit seam round it."""
    at = pt(ROTOR_AT[0], ROTOR_AT[1], FUSE_TOP)
    p.hull.cylinder(6.4, 1.4, 8, M.panel, Placement(at, math.pi / 8), 5.6)
    p.hull.box([6.6, 0.5, 1.2], M.dark, Placement([at[0], FUSE_TOP + 1.3, at[2]]))
    p.neon.ring(6.1, 0.25, 8, N, Placement([at[0], FUSE_TOP + 1, at[2]], math.pi / 8))


def draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a lit collar round the opening the rotor rises from."""
    at = pt(ROTOR_AT[0], ROTOR_AT[1], FUSE_TOP)
    p.neon.ring(5.9, 0.4, 12, N, Placement(at))


def ark_armour() -> Any:
    """Return the Aerial Ark's armour drawings by region id (`drawing.armour`, D-254)."""
    return {
        "joint": {"whole": draw_joint, "frame": draw_joint_frame},
        "root-plating": {"whole": draw_root_plating},
        "nose-plating": {"whole": draw_nose_plating},
        "rotor-hatch": {"whole": draw_hatch, "frame": draw_hatch_frame},
    }


def _collar(p: Any, x: float, z: float, length: float, color: Any) -> None:
    """Add an armoured collar round a nacelle at `x`, from `z` forwards `length` px."""
    r = NACELLE_R
    p.hull.lathe(
        [[r + 1.3, 0], [r + 1.6, 0.8], [r + 1.6, length - 0.8], [r + 1.3, length]],
        10,
        color,
        Placement([x, NACELLE_AXIS, z], 0, QUARTER),
    )


def barbette(p: Any, at: Vec3) -> None:
    """Add an engine's gun section (FB-AERIAL-ARK-03): armour round its nacelle, a gun seat on top.

    Collars fore and aft round the nacelle, armour cheeks down its sides, the seat its turret or
    laser stands on (its mount, BOSS-58) between them, lit round its foot.
    """
    x = at[0]
    z = at[2]
    _collar(p, x, z - 6, 4, M.panel)
    _collar(p, x, z + 8, 2, M.base)
    p.neon.ring(NACELLE_R + 1.7, 0.4, 10, N, Placement([x, NACELLE_AXIS, z - 2.4], 0, QUARTER))
    for s in [-1, 1]:
        p.hull.box([1.4, 6, 14], M.base, Placement([x + s * (NACELLE_R + 0.8), 9, z + 2]))
    seat = [x, NACELLE_TOP - 1.4, z + 4]
    p.hull.cylinder(4.4, 1.4, 8, M.panel, Placement(seat, math.pi / 8), 4)
    p.neon.ring(4.5, 0.3, 8, N, Placement([x, NACELLE_TOP - 0.9, z + 4], math.pi / 8))


def saddle(p: Any, at: Vec3) -> None:
    """Add a middle engine's saddle (FB-AERIAL-ARK-03): an armoured deck over its nacelle.

    Its missile block stands on it (its mount, BOSS-58); cheeks down the nacelle's sides, a
    collar at its front, lit along its edges.
    """
    x = at[0]
    z = at[2]
    deck = [[x - 6.8, z - 6], [x + 6.8, z - 6], [x + 6.8, z + 8], [x - 6.8, z + 8]]
    p.hull.bevel_slab(
        deck, [NACELLE_TOP - 2.4, NACELLE_TOP - 0.6, NACELLE_TOP], [0, 0.6], M.panel, None, M.base
    )
    for s in [-1, 1]:
        p.hull.box([1.2, 7, 14], M.base, Placement([x + s * 6.2, NACELLE_TOP - 9, z + 1]))
        p.neon.box([0.4, 0.4, 12], N, Placement([x + s * 6.9, NACELLE_TOP - 0.5, z + 1]))
    _collar(p, x, z - 9, 3, M.panel)
