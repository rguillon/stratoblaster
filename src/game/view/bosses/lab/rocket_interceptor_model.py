# Copyright (c) 2026 Renaud Guillon
"""MB-ROCKET-INTERCEPTOR-01 to MB-ROCKET-INTERCEPTOR-05: the Rocket Interceptor, the Lab's L-20.

Logical pixels, nose +Z, Y up (towards the camera). A gigantic rocket-plane seen from above: a
slim core plane (a long faceted fuselage, a glazed canopy, stubby delta wings, two canted tail fins
and a main rocket nozzle) riding between two big strap-on boosters held to its wingtips by pylons.
The boosters' casings, the wings' middle sections and the wingtip doors are its rig
(`rocket_interceptor_rig`); the wings' outer sections (moving pieces) and the spine hatch are its
armour. A machine, not a creature: the Lab's fourth round builds gigantic airplanes (user request,
2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.rocket_interceptor import (
    BOOSTER_AXIS,
    BOOSTER_CASING,
    BOOSTER_R,
    BOOSTER_TIP,
    CHIN_AT,
    CHIN_TOP,
    EXT_Y,
    EXTENSION,
    FLAK_TOP,
    NOSE,
    ROCKET_INTERCEPTOR,
    ROTOR_AT,
    SPINE_TOP,
    TAIL,
    WING,
    WING_Y,
)
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_shapes import edge_strips
from game.view.bosses.lab.rocket_interceptor_rig import (
    BAND,
    build_interceptor_rig,
    flat,
    interceptor_triangles,
    pt,
)
from game.view.bosses.mini_boss_greebles import lamps, seam, vent
from game.view.bosses.world_1_organic_kit import F, M
from game.view.enemies.enemy_shapes import CANOPY_SECTION, FIGHTER_SECTION
from render.geometry.solids import LoftOptions, Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["rocket-interceptor"]
QUARTER = math.pi / 2
GLASS = [0.06, 0.08, 0.1]
# The fuselage's loft stations along Z (model: nose +Z), `[z, half width, bottom, top]`.
FUSELAGE: list[Any] = [
    [-TAIL, 4, 3, 8.5],
    [-30, 6.2, 1, SPINE_TOP - 0.6],
    [-10, 7, 0, SPINE_TOP],
    [20, 7, 0, SPINE_TOP - 0.5],
    [36, 5, 0.5, 9],
    [46, 3, 2, 7],
    [-NOSE, 0, 4, 4],
]
# The canopy along the fuselage's back, `[z, half width, bottom, top]`.
CANOPY: list[Any] = [
    [21, 2.2, SPINE_TOP - 1.2, SPINE_TOP - 0.5],
    [26, 3.6, SPINE_TOP - 1.6, SPINE_TOP + 1.4],
    [33, 3.2, 9.4, SPINE_TOP + 0.4],
    [38, 0, 8.6, 8.6],
]


def _fuselage(p: Any) -> None:
    """Draw the core plane's fuselage (MB-ROCKET-INTERCEPTOR-02).

    A long, faceted body of dark plating from its needle nose to its tail, its glazed canopy, a
    light down each shoulder, seams across its back, the chin gun's and the rotor's seats, and its
    main rocket nozzle at the tail, burning.
    """
    p.hull.loft(FIGHTER_SECTION, FUSELAGE, M.base)
    p.hull.loft(CANOPY_SECTION, CANOPY, GLASS, None, LoftOptions(True))
    for s in [-1, 1]:
        edge_strips(p.neon, [[s * 3.9, -24], [s * 4.3, 6], [s * 4.1, 24]], 0.5, [6.9, 7.5], N)
        p.hull.box([1.4, 1.6, 9], M.panel, Placement([s * 3.6, SPINE_TOP - 1.2, -14], s * 0.08))
    for z in [-20, -2, 14]:
        p.bare.box([8, 0.3, 0.6], M.dark, Placement([0, SPINE_TOP - 0.2, z]))
    vent(p.hull, [0, SPINE_TOP - 0.2, -22], [4, 4], 3)
    chin = pt(CHIN_AT[0], CHIN_AT[1], CHIN_TOP - 0.4)
    p.hull.cylinder(4.6, 0.6, 8, M.dark, Placement(chin, math.pi / 8))
    p.neon.box([1, 0.4, 1], N, Placement([0, 6.6, -NOSE - 6]))
    # Its main rocket: a bell nozzle out of the tail, burning.
    p.hull.lathe(
        [[3.4, 0], [4, 2], [5.2, 6]], 10, M.panel, Placement([0, 5.5, -TAIL + 0.5], 0, -QUARTER)
    )
    p.reactor([0, 5.5, -TAIL - 5], 4)


def _wings(p: Any) -> None:
    """Draw the stub delta wings (MB-ROCKET-INTERCEPTOR-02): short, thick, swept plates.

    A light along each leading edge, seams, the pylon sockets at the tip and the slot at the tip
    the telescoping sections come out of.
    """
    for s in [-1, 1]:
        outline = [flat(s * 4, WING[0][1] - 1)]
        outline.extend([flat(s * q[0], q[1]) for q in WING])
        outline.append(flat(s * 4, WING[3][1]))
        p.flesh.bevel_slab(outline, WING_Y, [0.5, 1.2], F.graphite, None, F.slate)
        edge_strips(
            p.neon,
            [flat(s * 7.5, -8.8), flat(s * 21.5, 8.2)],
            0.6,
            [WING_Y[2] - 0.6, WING_Y[2] + 0.1],
            N,
        )
        seam(p.hull, flat(s * 12, -2), flat(s * 12, 26.5), [WING_Y[2], 0.4, 0.3])
        seam(p.hull, flat(s * 17, 4), flat(s * 17, 25.5), [WING_Y[2], 0.4, 0.3])
        # The slot at the tip the sections slide out of, lit along its lips.
        p.bare.box([0.8, 3, 15.4], M.dark, Placement(pt(s * 21.7, 17, 3)))
        for y in [3, 19]:
            p.hull.box([3, 1.4, 7], M.panel, Placement(pt(s * 19.5, y, WING_Y[2] - 0.6)))
        lamps(p.neon, [pt(s * 20.5, 25, WING_Y[2])], 1.2, N)


def _tail(p: Any) -> None:
    """Draw its tail (MB-ROCKET-INTERCEPTOR-02): two canted fins and small tailplanes."""
    for s in [-1, 1]:
        fin = [flat(s * 7, 24), flat(s * 7, 36), flat(s * 8.6, 37), flat(s * 8.6, 30)]
        p.hull.slab(fin, [6, 18], M.panel, Placement([0, 0, 0]), M.base)
        p.neon.box([0.5, 0.5, 6], N, Placement(pt(s * 7.8, 33, 18)))
        plane = [flat(s * 5, 28), flat(s * 15, 34), flat(s * 15, 37), flat(s * 5, 36)]
        p.hull.bevel_slab(plane, [4.5, 5.6, 6.4], [0.2, 0.5], M.base, None, M.panel)


def build_rocket_interceptor(scene: Any) -> Any:
    """MB-ROCKET-INTERCEPTOR-01, MB-ROCKET-INTERCEPTOR-04: the Rocket Interceptor.

    A rocket-plane between two strap-on boosters, about 3.6 L across, orange lights (shown
    yellow): its boosters' missile blocks, its tail's flak mortar, its chin gun and spine rotor
    (their mounts, drawn by `build_boss_model`, BOSS-58). Its boosters fall away and its wings
    telescope out at its transformation (MB-ROCKET-INTERCEPTOR-05).
    """

    def core(p: Any) -> None:
        _fuselage(p)
        _wings(p)
        _tail(p)

    return build_boss_model(
        ROCKET_INTERCEPTOR,
        scene,
        N,
        {
            "core": core,
            "parts": {"booster-left": _nose_cone, "booster-right": _nose_cone, "flak": _flak},
            "rig": {"build": build_interceptor_rig, "triangles": interceptor_triangles},
            "armour": {
                "wing-ext-right": {"whole": _extension(1)},
                "wing-ext-left": {"whole": _extension(-1)},
                "rotor-hatch": {"whole": _hatch, "frame": _hatch_frame},
            },
        },
    )


def _nose_cone(p: Any, at: Vec3) -> None:
    """Add a booster's nose cone (MB-ROCKET-INTERCEPTOR-03): its part, ahead of its casing.

    A long ogive of plating with a pale band and a lit ring at its foot, four strakes round it.
    """
    x = at[0]
    y0 = -BOOSTER_CASING[0]
    length = -BOOSTER_TIP - y0
    p.hull.lathe(
        [
            [BOOSTER_R + 0.2, 0],
            [BOOSTER_R + 0.2, 4],
            [BOOSTER_R - 0.8, 8],
            [6.4, 12.5],
            [3.2, 16],
            [0, length],
        ],
        10,
        M.panel,
        Placement([x, BOOSTER_AXIS, y0], 0, QUARTER),
    )
    p.bare.ring(BOOSTER_R + 0.3, 2, 10, BAND, Placement([x, BOOSTER_AXIS, y0 + 4.5], 0, QUARTER))
    p.neon.ring(BOOSTER_R + 0.35, 0.6, 10, N, Placement([x, BOOSTER_AXIS, y0 + 0.4], 0, QUARTER))
    for a in [0.5, 2.6]:
        p.hull.box(
            [0.8, 2.6, 8],
            M.base,
            Placement(
                [x + math.cos(a) * 8.6, BOOSTER_AXIS + math.sin(a) * 8.6, y0 + 5],
                0,
                0,
                a - QUARTER,
            ),
        )


def _flak(p: Any, at: Vec3) -> None:
    """Add the tail turret (MB-ROCKET-INTERCEPTOR-03): an armoured drum the flak mortar stands on.

    Lit round its foot, splinter plates round it.
    """
    p.hull.lathe(
        [[5.6, 8], [6.8, 9.2], [6.8, FLAK_TOP - 0.8], [6, FLAK_TOP], [0, FLAK_TOP]],
        8,
        M.panel,
        Placement([at[0], 0, at[2]], math.pi / 8),
    )
    p.neon.ring(6.9, 0.5, 8, N, Placement([at[0], 9.6, at[2]], math.pi / 8))
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        q = [at[0] + math.sin(a) * 7.4, 8.6, at[2] + math.cos(a) * 7.4]
        p.hull.box([3, 2.4, 1], M.base, Placement(q, a))


def _extension(side: float) -> Any:
    """Return the drawing of the wing's outer section on `side`, as drawn once out.

    A thin plated slab with a pointed tip, a light along its leading edge and round its tip, the
    seat the lance's pod stands on under the doors.
    """

    def draw(p: Any) -> None:
        outline = [flat(side * q[0], q[1]) for q in EXTENSION]
        p.flesh.bevel_slab(
            outline, [EXT_Y[0], EXT_Y[1] - 0.8, EXT_Y[1]], [0.2, 0.5], F.graphite, None, F.slate
        )
        edge_strips(
            p.neon,
            [flat(side * 35, 11.1), flat(side * 47, 11.1), flat(side * 50.4, 14.2)],
            0.5,
            [EXT_Y[1] - 0.6, EXT_Y[1] + 0.05],
            N,
        )
        p.bare.cylinder(5.6, 0.2, 8, M.dark, Placement(pt(side * 44, 17, EXT_Y[1] - 0.1)))
        lamps(p.neon, [pt(side * 50.6, 17, EXT_Y[1] - 0.6)], 1.3, N)

    return draw


def _hatch(p: Any) -> None:
    """Draw the hatch over the spine rotor (BOSS-58): an octagonal cap, a lit seam round it."""
    at = pt(ROTOR_AT[0], ROTOR_AT[1], SPINE_TOP - 0.3)
    p.hull.cylinder(6, 1.4, 8, M.panel, Placement(at, math.pi / 8), 5.2)
    p.hull.box([6.4, 0.5, 1.2], M.dark, Placement([at[0], SPINE_TOP + 1, at[2]]))
    p.neon.ring(5.7, 0.25, 8, N, Placement([at[0], SPINE_TOP + 0.7, at[2]], math.pi / 8))


def _hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a lit collar round the opening the rotor rises from."""
    at = pt(ROTOR_AT[0], ROTOR_AT[1], SPINE_TOP - 0.2)
    p.neon.ring(5.5, 0.4, 12, N, Placement(at))
