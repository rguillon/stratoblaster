# Copyright (c) 2026 Renaud Guillon
"""FB-TILTROTOR-BEHEMOTH-01 to -05: the Tiltrotor Behemoth, the Lab's L-19 final boss.

Logical pixels, nose +Z, Y up (towards the camera). A gigantic tiltrotor: a boxy fuselage with a
glazed nose, an upswept tail with an H tail over its rear ramp, gun sponsons low on its flanks, a
high wing across its back (its centre section on the roof; its outer halves are moving pieces that
stow along the fuselage), a forked cradle at each wingtip holding a rotor nacelle (the nacelles,
spinners, slats and ramp are its rig, `tiltrotor_behemoth_rig`). A machine, not a creature: the
Lab's fourth round builds gigantic airplanes (user request, 2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.tiltrotor_behemoth import (
    BELLY,
    CANNON_POD,
    CENTRE_H,
    CENTRE_X,
    CHORD,
    CRADLE,
    CRADLE_H,
    DORSAL_AT,
    FAIRING,
    FAIRING_TOP,
    GUN_H,
    HALF,
    NACELLE_AT,
    NACELLE_H,
    NACELLE_LENGTH,
    NOSE,
    NOSE_GUN_H,
    OUTER_H,
    ROOF,
    ROTOR_AT,
    SPONSON,
    SPONSON_H,
    TILTROTOR_BEHEMOTH,
    WING_GUN_H,
    WING_TIP_X,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.tiltrotor_behemoth_nacelle import docked_layers
from game.view.bosses.lab.tiltrotor_behemoth_rig import behemoth_triangles, build_behemoth_rig
from game.view.bosses.world_1_organic_kit import M, polygon
from render.geometry.mesh_triangles import append_triangles
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["tiltrotor-behemoth"]
QUARTER = math.pi / 2
GLASS = [0.05, 0.06, 0.08]
# The fuselage's section: a box with chamfered edges, counter-clockwise seen from the nose.
BOX = [
    [1, 0.1],
    [1, 0.84],
    [0.76, 1],
    [-0.76, 1],
    [-1, 0.84],
    [-1, 0.1],
    [-0.74, 0],
    [0.74, 0],
]
# Its stations from the tail to the nose: `[config y, half width, low, high]`.
STATIONS = [  # type: list[list[float]]
    [74, 3.5, 17, 21],
    [68, 8, 13.5, 21.5],
    [60, 12, 9, 21],
    [50, HALF, BELLY, ROOF],
    [NOSE + 26, HALF, BELLY, ROOF],
    [NOSE + 14, 12, 3.5, 18.5],
    [NOSE + 5, 7, 6, 15.5],
    [NOSE, 2, 9, 12.5],
]
# The H tail: the stabiliser across the tail `[y0, y1]`, its half span and heights; a fin at each
# end, `FIN_TOP` high.
STAB = [61, 72]
STAB_X = 27
STAB_H = [19.5, 21.2]
FIN_TOP = 34


def _model(x: float, y: float) -> list[Any]:
    """Return the playfield outline point `(x, y)` as a model outline point `[x, z]`."""
    return [-x, -y]


def _outline(points: list[Any], side: float = 1) -> list[list[float]]:
    """Return a playfield outline (its X times `side`) as a model outline."""
    return [_model(side * q[0], q[1]) for q in points]


def _box(x0: float, x1: float, y0: float, y1: float) -> list[list[float]]:
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _fuselage(p: Any) -> None:
    """Draw the fuselage (FB-TILTROTOR-BEHEMOTH-02): a long chamfered box, an upswept tail.

    Lit lines along its roof edges and a row of lit ports down each flank, a smoked glass cockpit
    over the nose framed in light, roof plating, the dorsal turret's seat and the spine rotor's
    well, intake grilles behind the wing.
    """
    stations = [[-s[0], s[1], s[2], s[3]] for s in STATIONS]
    p.hull.loft(BOX, stations, M.base)
    for side in [-1, 1]:
        p.neon.box([0.5, 0.4, 112], N, Placement(boss_point(side * 11.2, -5, ROOF - 0.1)))
        p.bare.box([4, 0.4, 120], M.panel, Placement(boss_point(side * 5.5, -8, ROOF - 0.15)))
        for k in range(10):
            y = -52 + k * 10.5
            p.neon.box([0.4, 1.6, 3], N, Placement(boss_point(side * (HALF + 0.05), y, 12)))
    p.hull.box([18, 1.4, 12], GLASS, Placement(boss_point(0, NOSE + 13, 17.2), 0, -0.25))
    p.neon.box([18.6, 0.5, 0.6], N, Placement(boss_point(0, NOSE + 19, 18.8)))
    for side in [-1, 1]:
        p.neon.box(
            [0.5, 0.5, 12.4], N, Placement(boss_point(side * 4.5, NOSE + 13, 18.5), 0, -0.25)
        )
    seat = boss_point(DORSAL_AT[0], DORSAL_AT[1], 0)
    p.hull.cylinder(6.6, 1.2, 12, M.panel, Placement([seat[0], ROOF - 0.6, seat[2]]))
    p.neon.ring(6.7, 0.4, 12, N, Placement([seat[0], ROOF + 0.2, seat[2]]))
    well = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.bare.cylinder(6, 0.6, 8, M.dark, Placement([well[0], ROOF - 0.3, well[2]]))
    for y in [44, 47.5]:
        p.bare.box([12, 0.5, 1.6], M.dark, Placement(boss_point(0, y, ROOF - 0.1)))
    # A dorsal spine from behind the cockpit to the turret's seat: a raised box, lit vents.
    p.hull.bevel_slab(
        _outline(_box(-4.5, 4.5, -60, -44)),
        [ROOF - 0.5, ROOF + 1.4, ROOF + 2.6],
        [0, 0.8],
        M.panel,
        None,
        M.base,
    )
    for k in range(3):
        p.neon.box([5, 0.3, 0.6], N, Placement(boss_point(0, -57 + k * 5, ROOF + 2.6)))
    mast = boss_point(0, -46, ROOF + 2.4)
    p.hull.cylinder(0.6, 6, 5, M.base, Placement(mast))
    p.neon.box([3.6, 0.5, 0.5], N, Placement([mast[0], mast[1] + 5.2, mast[2]]))
    # Armour bands round its flanks, dark.
    for y in [-6, 26, 40]:
        for side in [-1, 1]:
            p.bare.box(
                [0.6, 14, 2.4], M.dark, Placement(boss_point(side * (HALF + 0.1), y, BELLY + 3))
            )


def _tail(p: Any) -> None:
    """Draw the H tail (FB-TILTROTOR-BEHEMOTH-02): a stabiliser over the tail, a fin at each end.

    Lit along the stabiliser's trailing edge and up each fin's rudder.
    """
    plate = [[-STAB_X, STAB[0] + 2], [STAB_X, STAB[0] + 2], [STAB_X, STAB[1]], [-STAB_X, STAB[1]]]
    p.hull.bevel_slab(
        _outline(plate), [STAB_H[0], STAB_H[0] + 0.6, STAB_H[1]], [0, 0.5], M.base, None, M.panel
    )
    p.neon.box([STAB_X * 2 - 4, 0.4, 0.6], N, Placement(boss_point(0, STAB[1] - 0.6, STAB_H[1])))
    for side in [-1, 1]:
        x = -side * STAB_X
        fin = [
            [STAB_H[0], -STAB[0]],
            [FIN_TOP, -STAB[0] - 6],
            [FIN_TOP, -STAB[1] - 1],
            [STAB_H[0], -STAB[1] - 1],
        ]
        p.hull.slab(fin, [-0.9, 0.9], M.base, Placement([x, 0, 0], 0, 0, QUARTER), M.panel)
        p.neon.box(
            [0.6, FIN_TOP - STAB_H[1] - 1.5, 0.6],
            N,
            Placement([x, STAB_H[1] + 0.5, -STAB[1] - 0.4]),
        )


def _centre_wing(p: Any) -> None:
    """Draw the wing's centre section on the roof (FB-TILTROTOR-BEHEMOTH-02).

    Lit along its leading edge; a fold knuckle at each end (the outer halves' hinge), lit.
    """
    p.hull.bevel_slab(
        _outline(_box(-CENTRE_X, CENTRE_X, CHORD[0], CHORD[1])),
        [CENTRE_H[0] - 0.5, CENTRE_H[0] + 1, CENTRE_H[1]],
        [0, 0.6],
        M.base,
        None,
        M.panel,
    )
    p.neon.box(
        [CENTRE_X * 2 - 6, 0.4, 0.6], N, Placement(boss_point(0, CHORD[0] + 0.8, CENTRE_H[1]))
    )
    for side in [-1, 1]:
        knuckle = boss_point(side * CENTRE_X, CHORD[0] + 2.5, CENTRE_H[0])
        p.hull.cylinder(2.6, OUTER_H[1] - CENTRE_H[0] + 0.6, 8, M.panel, Placement(knuckle))
        p.neon.ring(2.7, 0.4, 8, N, Placement([knuckle[0], OUTER_H[1] - 0.6, knuckle[2]]))
        for k in range(3):
            y = CHORD[0] + 7 + k * 5
            p.bare.box(
                [0.5, 0.3, 3.6],
                M.dark,
                Placement(boss_point(side * (CENTRE_X - 9), y, CENTRE_H[1])),
            )


def _sponsons(p: Any) -> None:
    """Draw the gun sponsons low on its flanks (FB-TILTROTOR-BEHEMOTH-10): the cannons dock there.

    Each a bevelled box out from the fuselage, lit along its edge, two saddles on top for the
    nacelle and a pedestal under the cannon's turret (the stump stands on it once it is gone).
    """
    x0 = SPONSON[0]
    x1 = SPONSON[1]
    for side in [-1, 1]:
        p.hull.bevel_slab(
            _outline(_box(x0, x1, SPONSON[2], SPONSON[3]), side),
            [SPONSON_H[0], SPONSON_H[1] - 1.5, SPONSON_H[1]],
            [1.2, 0.6],
            M.base,
            None,
            M.panel,
        )
        p.neon.box(
            [0.6, 0.4, SPONSON[3] - SPONSON[2] - 3],
            N,
            Placement(boss_point(side * (x1 - 0.6), (SPONSON[2] + SPONSON[3]) / 2, SPONSON_H[1])),
        )
        x = side * (x0 + x1) / 2
        for y in [-40, -26]:
            p.hull.box(
                [8, NACELLE_H - 6 - SPONSON_H[1] + 0.4, 2.4],
                M.panel,
                Placement(boss_point(x, y, SPONSON_H[1])),
            )
        dock = boss_point(side * 26, -50, SPONSON_H[1])
        p.hull.cylinder(5, CANNON_POD[1] - SPONSON_H[1] - 0.2, 10, M.panel, Placement(dock), 4.4)
        p.neon.ring(5.05, 0.4, 10, N, Placement([dock[0], SPONSON_H[1] + 0.8, dock[2]]))


def _outer_wing(side: float) -> Any:
    """Return the drawing of the outer wing half on `side` (+1: right) as drawn: spread.

    A thick plate out to the tip, lit along its trailing edge, flap seams across it, a fold knuckle
    plate at its root, and its tip's forked cradle (two cheek plates either side of the nacelle,
    a bridge behind it), lit on top.
    """

    def draw(p: Any) -> None:
        plate = _box(CENTRE_X, WING_TIP_X, CHORD[0], CHORD[1])
        p.hull.bevel_slab(
            _outline(plate, side),
            [OUTER_H[0], OUTER_H[0] + 1.2, OUTER_H[1]],
            [0, 0.7],
            M.base,
            None,
            M.panel,
        )
        length = WING_TIP_X - CENTRE_X
        p.neon.box(
            [length - 4, 0.4, 0.7],
            N,
            Placement(boss_point(side * (CENTRE_X + WING_TIP_X) / 2, CHORD[1] - 0.8, OUTER_H[1])),
        )
        for x in [42, 56]:
            p.bare.box(
                [0.5, 0.3, 8], M.dark, Placement(boss_point(side * x, CHORD[1] - 5, OUTER_H[1]))
            )
        p.bare.box(
            [length - 4, 0.3, 0.5],
            M.dark,
            Placement(boss_point(side * (CENTRE_X + WING_TIP_X) / 2, CHORD[1] - 9.5, OUTER_H[1])),
        )
        for cheek in [[CRADLE[0], CRADLE[0] + 2], [CRADLE[1] - 2, CRADLE[1]]]:
            p.hull.bevel_slab(
                _outline(_box(cheek[0], cheek[1], CRADLE[2], CRADLE[3]), side),
                [CRADLE_H[0], CRADLE_H[1] - 1, CRADLE_H[1]],
                [0, 0.4],
                M.panel,
                None,
                M.base,
            )
            p.neon.box(
                [1.2, 0.4, CRADLE[3] - CRADLE[2] - 2],
                N,
                Placement(
                    boss_point(
                        side * (cheek[0] + cheek[1]) / 2, (CRADLE[2] + CRADLE[3]) / 2, CRADLE_H[1]
                    )
                ),
            )
        bridge = _box(CRADLE[0], CRADLE[1], NACELLE_AT[1] + 5, CRADLE[3])
        p.hull.bevel_slab(
            _outline(bridge, side),
            [CRADLE_H[0], CRADLE_H[0] + 3, CRADLE_H[0] + 5],
            [0, 0.4],
            M.base,
            None,
            M.panel,
        )
        knuckle = boss_point(side * (CENTRE_X + 1.5), CHORD[0] + 2.5, OUTER_H[0])
        p.hull.cylinder(2.4, OUTER_H[1] - OUTER_H[0] + 0.9, 8, M.panel, Placement(knuckle))

    return draw


def _barbette(radius: float, low: float, top: float) -> Any:
    """Return the drawing of a gun's barbette: a drum from `low` to `top`, lit round its rim."""

    def draw(p: Any, at: Vec3) -> None:
        p.hull.cylinder(
            radius, top - low, 10, M.panel, Placement([at[0], low, at[2]]), radius - 0.5
        )
        p.neon.ring(radius - 0.2, 0.4, 10, N, Placement([at[0], top - 1.2, at[2]]))
        p.bare.ring(radius + 0.1, 0.6, 10, M.dark, Placement([at[0], low + 0.4, at[2]]))

    return draw


def _cannon(p: Any, at: Vec3) -> None:
    """Add a turbine cannon's body (FB-TILTROTOR-BEHEMOTH-10): the nacelle, tilted, folded.

    The nacelle lies along the boss behind its turret (the cannon's mount), its blades folded back
    along it: the same as the rig draws it as it tilts (`tiltrotor_behemoth_nacelle`).
    """
    shift = [at[0], NACELLE_H, at[2] - NACELLE_LENGTH - 3]
    for pair in docked_layers():
        append_triangles(getattr(p, pair[0]).geometry, pair[1], shift)


def _draw_fairing(p: Any) -> None:
    """Draw the spine fairing over the mortar (FB-TILTROTOR-BEHEMOTH-11): a lit armoured hump."""
    p.hull.bevel_slab(
        _outline(FAIRING),
        [ROOF - 0.3, FAIRING_TOP - 2, FAIRING_TOP],
        [0, 1.4],
        M.panel,
        None,
        M.base,
    )
    p.neon.box([0.6, 0.4, 15], N, Placement(boss_point(0, 19, FAIRING_TOP)))
    for side in [-1, 1]:
        p.bare.box([0.8, 0.5, 14], M.dark, Placement(boss_point(side * 5, 18.5, FAIRING_TOP - 1.2)))


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over the spine rotor (BOSS-58): an octagonal cap, a lit seam round it."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.bevel_slab(
        polygon(8, 6.7), [ROOF - 0.4, ROOF + 0.2, ROOF + 1.5], [0, 0.9], M.panel, Placement(at)
    )
    p.neon.ring(6.2, 0.25, 8, N, Placement([at[0], ROOF + 0.7, at[2]], math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.ring(6.5, 1.2, 12, M.base, Placement([at[0], ROOF - 0.6, at[2]]))
    p.neon.ring(6.5, 0.3, 12, N, Placement([at[0], ROOF + 0.4, at[2]]))


def build_tiltrotor_behemoth(scene: Any) -> Any:
    """FB-TILTROTOR-BEHEMOTH-01, FB-TILTROTOR-BEHEMOTH-04: the Tiltrotor Behemoth.

    A boxy fuselage, a high wing with a rotor nacelle in a cradle at each tip, gun sponsons, an H
    tail over its ramp; orchid light lines; about 6 L across its rotors.
    """

    def core(p: Any) -> None:
        _fuselage(p)
        _tail(p)
        _centre_wing(p)
        _sponsons(p)

    return build_boss_model(
        TILTROTOR_BEHEMOTH,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "wing-left": _barbette(5.6, OUTER_H[1] - 0.4, WING_GUN_H),
                "wing-right": _barbette(5.6, OUTER_H[1] - 0.4, WING_GUN_H),
                "tail-left": _barbette(5, ROOF - 1, GUN_H),
                "tail-right": _barbette(5, ROOF - 1, GUN_H),
                "nose-gun": _barbette(5.8, 16, NOSE_GUN_H),
                "cannon-left": _cannon,
                "cannon-right": _cannon,
            },
            # FB-TILTROTOR-BEHEMOTH-05: its nacelles, spinners, slats and ramp.
            "rig": {"build": build_behemoth_rig, "triangles": behemoth_triangles},
            "armour": {
                "wing-right": {"whole": _outer_wing(1)},
                "wing-left": {"whole": _outer_wing(-1)},
                "spine-fairing": {"whole": _draw_fairing},
                "rotor-hatch": {"whole": _draw_hatch, "frame": _draw_hatch_frame},
            },
        },
    )
