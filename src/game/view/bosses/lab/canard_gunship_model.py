# Copyright (c) 2026 Renaud Guillon
"""MB-CANARD-GUNSHIP-01 to MB-CANARD-GUNSHIP-05: the Canard Gunship, the Lab's L-19 mini boss.

Logical pixels, nose +Z, Y up (towards the camera). A gigantic canard-wing gunship: a long boxy
fuselage with a glazed nose, small canards behind it, the main wings at the back with winglets on
their tips and an engine on each (their pusher propellers are its rig, `canard_gunship_rig`), two
cargo doors down its right flank (moving pieces: they fold down into firing platforms as it
transforms). A machine, not a creature: the Lab's fourth round builds gigantic airplanes (user
request, 2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.canard_gunship import (
    BELLY,
    CANARD_GUN_H,
    CANARD_GUNSHIP,
    CANARD_H,
    CANARD_ROOT,
    CANARD_TIP,
    CANARD_TIP_X,
    DOOR_REACH,
    DOOR_THICK,
    DOORS,
    DORSAL_AT,
    ENGINE_H,
    ENGINE_RADIUS,
    ENGINE_X,
    ENGINE_Y,
    FLOOR,
    HALF,
    NOSE,
    NOSE_GUN_AT,
    NOSE_GUN_H,
    ROOF,
    ROTOR_AT,
    TAIL,
    WING_H,
    WING_ROOT,
    WING_TIP,
    WING_TIP_X,
    WINGLET_TOP,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.canard_gunship_rig import build_gunship_rig, gunship_rig_triangles
from game.view.bosses.world_1_organic_kit import M, polygon
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["canard-gunship"]
QUARTER = math.pi / 2
GLASS = [0.05, 0.065, 0.08]
# The fuselage's section: a box with chamfered edges, counter-clockwise seen from the nose, `[u,
# v]` across its width and up its height.
BOX = [
    [1, 0.12],
    [1, 0.82],
    [0.72, 1],
    [-0.72, 1],
    [-1, 0.82],
    [-1, 0.12],
    [-0.7, 0],
    [0.7, 0],
]
# Its stations from the tail cone to the nose: `[config y, half width, low, high]`.
STATIONS = [  # type: list[list[float]]
    [TAIL, 2.5, 12, 18.5],
    [TAIL - 10, 6.5, 6, 20],
    [TAIL - 20, HALF, BELLY, ROOF],
    [NOSE + 24, HALF, BELLY, ROOF],
    [NOSE + 14, 7, 3, 18],
    [NOSE + 6, 4.5, 5, 15.5],
    [NOSE, 1.5, 8.5, 12],
]


def _model(x: float, y: float) -> list[Any]:
    """Return the playfield outline point `(x, y)` as a model outline point `[x, z]`."""
    return [-x, -y]


def _outline(points: list[Any], side: float = 1) -> list[list[float]]:
    """Return a playfield outline (its X times `side`) as a model outline."""
    return [_model(side * q[0], q[1]) for q in points]


def _fuselage(p: Any) -> None:
    """Draw the fuselage (MB-CANARD-GUNSHIP-02): a long chamfered box with a glazed nose.

    Lit lines along its roof edges, a row of lit ports down its left flank, the dark cargo bays
    behind the right flank's doors with their lit seams, the dorsal turret's seat and the spine
    rotor's collar; a smoked canopy over the nose, its frame lit, and a tail cone with a lit band.
    """
    stations = [[-s[0], s[1], s[2], s[3]] for s in STATIONS]
    p.hull.loft(BOX, stations, M.base)
    for side in [-1, 1]:
        p.neon.box([0.5, 0.4, 70], N, Placement(boss_point(side * 6.6, -12, ROOF - 0.1)))
        p.bare.box([3, 0.4, 92], M.panel, Placement(boss_point(side * 3.4, -14, ROOF - 0.15)))
    for k in range(9):
        y = -44 + k * 9
        p.neon.box([0.4, 1.4, 2.6], N, Placement(boss_point(-HALF - 0.05, y, 13)))
    for door in DOORS:
        mid = (door[0] + door[1]) / 2
        length = door[1] - door[0]
        p.bare.box([0.4, 13, length - 1], M.dark, Placement(boss_point(HALF + 0.02, mid, FLOOR)))
        p.neon.box([0.5, 0.4, length], N, Placement(boss_point(HALF + 0.1, mid, FLOOR + 13.6)))
    # The canopy: a smoked glass wedge over the nose, framed.
    p.hull.box([10, 1.4, 12], GLASS, Placement(boss_point(0, NOSE + 15, 17.4), 0, -0.22))
    p.neon.box([10.6, 0.5, 0.5], N, Placement(boss_point(0, NOSE + 21, 18.6)))
    p.neon.box([0.5, 0.5, 12], N, Placement(boss_point(0, NOSE + 15, 18.6), 0, -0.22))
    seat = boss_point(DORSAL_AT[0], DORSAL_AT[1], 0)
    p.hull.cylinder(5.8, 1.2, 10, M.panel, Placement([seat[0], ROOF - 0.6, seat[2]]))
    p.neon.ring(5.9, 0.4, 10, N, Placement([seat[0], ROOF + 0.2, seat[2]]))
    well = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.bare.cylinder(5.2, 0.6, 8, M.dark, Placement([well[0], ROOF - 0.3, well[2]]))
    tail = boss_point(0, TAIL - 6, 15)
    p.neon.ring(4.2, 0.6, 8, N, Placement(tail, 0, QUARTER))


def _canards(p: Any) -> None:
    """Draw the canards (MB-CANARD-GUNSHIP-02): two small plates either side of the nose.

    Lit along their leading edges; the canard pods (its parts) stand on their tips.
    """
    for side in [-1, 1]:
        plate = [
            [HALF - 1, CANARD_ROOT[0]],
            [CANARD_TIP_X, CANARD_TIP[0]],
            [CANARD_TIP_X, CANARD_TIP[1]],
            [HALF - 1, CANARD_ROOT[1]],
        ]
        p.hull.bevel_slab(
            _outline(plate, side),
            [CANARD_H[0], CANARD_H[0] + 0.6, CANARD_H[1]],
            [0, 0.4],
            M.base,
            None,
            M.panel,
        )
        x = (HALF + CANARD_TIP_X) / 2
        y = (CANARD_ROOT[0] + CANARD_TIP[0]) / 2
        a = math.atan2(CANARD_TIP_X - HALF, CANARD_ROOT[0] - CANARD_TIP[0])
        p.neon.box(
            [0.5, 0.4, CANARD_TIP_X - HALF],
            N,
            Placement(boss_point(side * x, y + 0.6, CANARD_H[1] - 0.1), -side * a),
        )


def _wings(p: Any) -> None:
    """Draw the main wings at the back (MB-CANARD-GUNSHIP-02), swept, a winglet on each tip.

    Lit along their trailing edges; flap lines across them; each winglet a tall plate with a lit
    stripe up its edge.
    """
    for side in [-1, 1]:
        plate = [
            [HALF - 1, WING_ROOT[0]],
            [WING_TIP_X, WING_TIP[0]],
            [WING_TIP_X, WING_TIP[1]],
            [HALF - 1, WING_ROOT[1]],
        ]
        p.hull.bevel_slab(
            _outline(plate, side),
            [WING_H[0], WING_H[0] + 0.8, WING_H[1]],
            [0, 0.6],
            M.base,
            None,
            M.panel,
        )
        dx = WING_TIP_X - HALF
        dy = WING_TIP[1] - WING_ROOT[1]
        a = math.atan2(dx, dy)
        length = math.sqrt(dx * dx + dy * dy)
        p.neon.box(
            [0.6, 0.4, length],
            N,
            Placement(
                boss_point(
                    side * (HALF + WING_TIP_X) / 2,
                    (WING_ROOT[1] + WING_TIP[1]) / 2 - 0.6,
                    WING_H[1] - 0.1,
                ),
                -side * a,
            ),
        )
        for x in [20, 46]:
            y = WING_ROOT[1] + (WING_TIP[1] - WING_ROOT[1]) * (x - HALF) / dx - 4
            p.bare.box([0.5, 0.3, 7], M.dark, Placement(boss_point(side * x, y, WING_H[1]), 0))
        winglet = [
            [WING_H[1] - 0.5, -WING_TIP[0]],
            [WINGLET_TOP - 2, -WING_TIP[0] - 8],
            [WINGLET_TOP, -WING_TIP[1] + 1],
            [WINGLET_TOP, -WING_TIP[1] - 2],
            [WING_H[1] - 0.5, -WING_TIP[1] - 1],
        ]
        x = -side * WING_TIP_X
        p.hull.slab(winglet, [-0.8, 0.8], M.base, Placement([x, 0, 0], 0, 0, QUARTER), M.panel)
        p.neon.box(
            [0.5, WINGLET_TOP - WING_H[1] - 2, 0.6],
            N,
            Placement([x, WING_H[1] + 1, -WING_TIP[1] - 1.6]),
        )


def _engine(p: Any, side: float) -> None:
    """Draw an engine on its wing (MB-CANARD-GUNSHIP-02), on `side` (+1: right).

    A cigar along the fuselage, a lit intake ring at its nose and a lit exhaust collar at its tail,
    where its pusher propeller turns (the rig).
    """
    x = side * ENGINE_X
    length = ENGINE_Y[1] - ENGINE_Y[0]
    r = ENGINE_RADIUS
    profile = [
        [2, 0],
        [r * 0.85, 1.6],
        [r, 5],
        [r, length - 6],
        [r * 0.7, length - 1.5],
        [1.5, length],
    ]
    tail = boss_point(x, ENGINE_Y[1], ENGINE_H)
    p.hull.lathe(profile, 10, M.panel, Placement(tail, 0, QUARTER))
    p.neon.ring(
        r * 0.78, 0.6, 10, N, Placement(boss_point(x, ENGINE_Y[0] + 1.2, ENGINE_H), 0, QUARTER)
    )
    p.neon.ring(
        r * 0.86, 0.6, 10, N, Placement(boss_point(x, ENGINE_Y[1] - 2.2, ENGINE_H), 0, QUARTER)
    )
    for k in range(3):
        p.bare.box(
            [1.4, 0.5, 2.2],
            M.dark,
            Placement(boss_point(x, ENGINE_Y[0] + 8 + 4 * k, ENGINE_H + r - 0.3)),
        )


def _canard_pod(p: Any, at: Vec3) -> None:
    """Add a canard pod (MB-CANARD-GUNSHIP-03): an armoured drum on its canard's tip.

    A lit band round it, a pointed fairing ahead of it; its twin turret stands on top.
    """
    base = CANARD_H[1] - 0.2
    p.hull.lathe(
        [
            [4.6, base],
            [5.2, base + 1],
            [5.2, CANARD_GUN_H - 1],
            [4.4, CANARD_GUN_H],
            [0, CANARD_GUN_H],
        ],
        8,
        M.panel,
        Placement([at[0], 0, at[2]], math.pi / 8),
    )
    p.neon.ring(5.25, 0.5, 8, N, Placement([at[0], base + 2.2, at[2]], math.pi / 8))
    p.hull.cylinder(2.6, 6, 6, M.base, Placement([at[0], base + 1.6, at[2] + 4.5], 0, QUARTER), 0.6)


def _nose_gun(p: Any, at: Vec3) -> None:
    """Add the nose gun's barbette (MB-CANARD-GUNSHIP-03): an armoured drum over the nose.

    A lit rim, a lit chevron on the nose ahead of it.
    """
    gun = boss_point(NOSE_GUN_AT[0], NOSE_GUN_AT[1], 0)
    p.hull.cylinder(5.4, 3, 10, M.panel, Placement([gun[0], NOSE_GUN_H - 3, gun[2]]), 4.8)
    p.neon.ring(5.2, 0.4, 10, N, Placement([gun[0], NOSE_GUN_H - 1.2, gun[2]]))
    p.neon.box([3.6, 0.3, 0.6], N, Placement([0, 13.6, at[2] + 6.5], 0, -0.4))


def _door(k: int) -> Any:
    """Return the drawing of door `k` (MB-CANARD-GUNSHIP-10) as drawn: open, a platform.

    Its deck plating on top (its inside, against the bay while closed), a lit strip along its
    outer edge, tread bars across it and a dark hinge rail at its foot.
    """
    door = DOORS[k]

    def draw(p: Any) -> None:
        mid = (door[0] + door[1]) / 2
        length = door[1] - door[0]
        outline = [
            [HALF, door[0]],
            [HALF + DOOR_REACH, door[0] + 0.6],
            [HALF + DOOR_REACH, door[1] - 0.6],
            [HALF, door[1]],
        ]
        p.hull.bevel_slab(
            _outline(outline),
            [FLOOR - DOOR_THICK, FLOOR - 0.3, FLOOR],
            [0, 0.3],
            M.base,
            None,
            M.panel,
        )
        p.neon.box(
            [0.7, 0.3, length - 2],
            N,
            Placement(boss_point(HALF + DOOR_REACH - 0.7, mid, FLOOR - 0.1)),
        )
        for j in range(4):
            y = door[0] + 2.5 + j * (length - 5) / 3
            p.bare.box(
                [DOOR_REACH - 3, 0.25, 0.6],
                M.dark,
                Placement(boss_point(HALF + DOOR_REACH / 2 + 0.5, y, FLOOR - 0.1)),
            )
        p.bare.cylinder(
            0.7,
            length,
            6,
            M.dark,
            Placement(boss_point(HALF + 0.4, door[1], FLOOR - 0.6), 0, QUARTER),
        )

    return draw


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over the spine rotor (BOSS-58): an octagonal cap, a lit seam round it."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.bevel_slab(
        polygon(8, 5.9), [ROOF - 0.4, ROOF + 0.2, ROOF + 1.4], [0, 0.8], M.panel, Placement(at)
    )
    p.neon.ring(5.4, 0.25, 8, N, Placement([at[0], ROOF + 0.6, at[2]], math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.ring(5.7, 1.2, 12, M.base, Placement([at[0], ROOF - 0.6, at[2]]))
    p.neon.ring(5.7, 0.3, 12, N, Placement([at[0], ROOF + 0.4, at[2]]))


def build_canard_gunship(scene: Any) -> Any:
    """MB-CANARD-GUNSHIP-01, MB-CANARD-GUNSHIP-04: the Canard Gunship.

    A long boxy fuselage, canards at its nose, swept wings with winglets and pusher engines at its
    back, cargo doors down its right flank; lime light lines; about 3.8 L across.
    """

    def core(p: Any) -> None:
        _fuselage(p)
        _canards(p)
        _wings(p)
        _engine(p, 1)
        _engine(p, -1)

    return build_boss_model(
        CANARD_GUNSHIP,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "canard-left": _canard_pod,
                "canard-right": _canard_pod,
                "nose-gun": _nose_gun,
            },
            # MB-CANARD-GUNSHIP-05: its propellers, the doors' struts, the racks and railings.
            "rig": {"build": build_gunship_rig, "triangles": gunship_rig_triangles},
            "armour": {
                "door-fore": {"whole": _door(0)},
                "door-aft": {"whole": _door(1)},
                "rotor-hatch": {"whole": _draw_hatch, "frame": _draw_hatch_frame},
            },
        },
    )
