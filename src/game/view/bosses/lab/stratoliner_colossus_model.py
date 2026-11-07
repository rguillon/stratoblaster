# Copyright (c) 2026 Renaud Guillon
"""FB-STRATOLINER-COLOSSUS-01 to -05: the Stratoliner Colossus, the Lab's L-16 final boss.

Logical pixels, nose +Z, Y up (towards the camera). A colossal six-engine swept-wing jet
bomber-airliner: a long round fuselage with rows of lit windows and a radome nose (an armour region:
its halves are its rig's), swept wings with three podded engines each on pylons ahead of them (the
outer engines' cowlings and cores are its rig, their fans an armour region), flaps along the inner
trailing edges (an armour region: its rig unfolds them into a second wing tier), a swept tailplane,
a tall fin and a tail gun. A machine, not a creature: the Lab's fourth round builds gigantic
airplanes (user request, 2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.stratoliner_colossus import (
    ENGINE_H,
    ENGINE_HALF,
    ENGINE_R,
    ENGINE_X,
    FIN_ROOT,
    FIN_TIP,
    FIN_TOP,
    FLAP,
    FUSELAGE,
    GATLING_AT,
    GATLING_POD,
    LANCE_AT,
    NACELLE_GUN_H,
    NOSE,
    NOSE_JOINT,
    PETAL_HINGE,
    ROOT_EDGES,
    ROOT_X,
    ROTOR_AT,
    SPINE_GUN_AT,
    SPINE_H,
    STRATOLINER_COLOSSUS,
    TAIL_GUN_AT,
    TAIL_GUN_H,
    TAIL_H,
    TAIL_ROOT,
    TAIL_SPAN,
    TAIL_TIP,
    TIP_EDGES,
    TIP_X,
    WING_GUN_H,
    WING_LOW,
    WING_TOP,
    engine_y,
    fuselage_at,
    leading_edge,
    trailing_edge,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.condor_lifter_joints import paint_posed
from game.view.bosses.lab.stratoliner_colossus_rig import (
    build_colossus_rig,
    rest_flaps,
    rest_noses,
    rig_triangles,
)
from game.view.bosses.world_1_organic_kit import M, polygon
from render.geometry.solids import LoftOptions, Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["stratoliner-colossus"]
QUARTER = math.pi / 2
SIDES = 14
SECTION = [
    [math.cos(2 * math.pi * k / SIDES), (1 + math.sin(2 * math.pi * k / SIDES)) / 2]
    for k in range(SIDES)
]
BLADES = 4


def _model(x: float, y: float) -> list[float]:
    """Return the playfield outline point `(x, y)` as a model outline point `[x, z]`."""
    return [-x, -y]


def _panel(side: int, _band: int) -> Any:
    """Return the shade of the fuselage's facet `side` (its belly and spine darker), or None."""
    return M.base if side in [3, 4, 10, 11] else None


def _fuselage(p: Any) -> None:
    """Draw the fuselage behind the nose cone (FB-STRATOLINER-COLOSSUS-01).

    A long round loft, a lit cheat line and rows of lit windows down its flanks, the cockpit's
    glazing just behind the radome, a dark spine walk, the spine gun's seat and the rotor's well.
    """
    stations = [[-s[0], s[1], s[2], s[3]] for s in reversed(FUSELAGE) if s[0] >= NOSE_JOINT]
    p.hull.loft(SECTION, stations, M.panel, None, LoftOptions(False, _panel))
    for side in [-1, 1]:
        y = -58
        while y < 40:
            hw = fuselage_at(y)[0]
            p.neon.box([0.3, 0.8, 1.2], N, Placement(boss_point(side * (hw - 0.05), y, 10.6)))
            y += 4
        p.neon.box([0.3, 0.4, 96], N, Placement(boss_point(side * 9.45, -10, 7)))
        for k in range(3):
            x = side * (1.6 + k * 2.2)
            p.neon.box(
                [1.8, 0.5, 1.6],
                N,
                Placement(boss_point(x, -62.5 + k * 0.4, fuselage_at(-62.5)[2] - 0.8 - k * 0.6)),
            )
    p.bare.box([2.4, 0.4, 70], M.dark, Placement(boss_point(0, -6, 15.9)))
    seat = boss_point(SPINE_GUN_AT[0], SPINE_GUN_AT[1], 0)
    p.hull.cylinder(6.6, 1.4, 12, M.base, Placement([seat[0], SPINE_H - 1.6, seat[2]]))
    p.neon.ring(6.7, 0.4, 12, N, Placement([seat[0], SPINE_H - 0.7, seat[2]]))
    well = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.bare.cylinder(6, 0.8, 8, M.dark, Placement([well[0], SPINE_H - 1, well[2]]))


def _wings(p: Any) -> None:
    """Draw the swept wings (FB-STRATOLINER-COLOSSUS-02): one chevron through the fuselage.

    Lit leading edges between the engines, dark ailerons outboard, tip lights, a rivet line.
    """
    outline = [
        _model(ROOT_X, ROOT_EDGES[0]),
        _model(TIP_X, TIP_EDGES[0]),
        _model(TIP_X, TIP_EDGES[1]),
        _model(ROOT_X, ROOT_EDGES[1]),
        _model(-ROOT_X, ROOT_EDGES[1]),
        _model(-TIP_X, TIP_EDGES[1]),
        _model(-TIP_X, TIP_EDGES[0]),
        _model(-ROOT_X, ROOT_EDGES[0]),
    ]
    p.hull.bevel_slab(
        outline, [WING_LOW, WING_LOW + 1.2, WING_TOP], [0, 0.8], M.base, None, M.panel
    )
    sweep = math.atan2(TIP_EDGES[0] - ROOT_EDGES[0], TIP_X - ROOT_X)
    for side in [-1, 1]:
        for x0, x1 in [[12, 22], [31, 41], [51, 61], [71, 84]]:
            _edge_light(p, side, x0, x1, sweep)
        # The ailerons outboard: dark strips along the trailing edge, a seam.
        mid = 64
        y = trailing_edge(mid) - 2.6
        length = 36 / math.cos(math.atan2(TIP_EDGES[1] - ROOT_EDGES[1], TIP_X - ROOT_X))
        turn = -side * math.atan2(TIP_EDGES[1] - ROOT_EDGES[1], TIP_X - ROOT_X)
        p.bare.box([length, 0.3, 3.8], M.dark, Placement(boss_point(side * mid, y, WING_TOP), turn))
        p.neon.box(
            [1.4, 0.5, TIP_EDGES[1] - TIP_EDGES[0] - 1],
            N,
            Placement(
                boss_point(side * (TIP_X - 0.7), (TIP_EDGES[0] + TIP_EDGES[1]) / 2, WING_TOP)
            ),
        )
        for k in range(9):
            x = 14 + k * 8
            y = (leading_edge(x) + trailing_edge(x)) / 2
            p.bare.box([0.8, 0.3, 0.8], M.dark, Placement(boss_point(side * x, y, WING_TOP)))


def _edge_light(p: Any, side: float, x0: float, x1: float, sweep: float) -> None:
    """Add a lit strip along the leading edge between `x0` and `x1` on `side`."""
    mid = (x0 + x1) / 2
    length = (x1 - x0) / math.cos(sweep)
    p.neon.box(
        [length, 0.4, 0.6],
        N,
        Placement(boss_point(side * mid, leading_edge(mid) + 0.8, WING_TOP - 0.3), -side * sweep),
    )


def _nacelle(p: Any, x: float, whole: bool) -> None:
    """Draw an engine on its pylon at `x`: a long nacelle, its exhaust cone, the pylon.

    `whole`: the full nacelle with its fan; else (an outer engine) only its back, behind the
    petals' hinge (the petals, its core and its fan are drawn apart).
    """
    y = engine_y(abs(x))
    rear = y + ENGINE_HALF
    r = ENGINE_R
    if whole:
        profile = [
            [1.6, 0],
            [r * 0.82, 2],
            [r, 6],
            [r, ENGINE_HALF * 2 - 2],
            [r * 0.96, ENGINE_HALF * 2],
        ]
    else:
        profile = [[1.6, 0], [r * 0.82, 2], [r, ENGINE_HALF - PETAL_HINGE]]
    p.hull.lathe(profile, 12, M.panel, Placement(boss_point(x, rear, ENGINE_H), 0, QUARTER))
    p.bare.cylinder(
        1.8, 2.5, 8, M.dark, Placement(boss_point(x, rear + 2.3, ENGINE_H), 0, QUARTER), 0.6
    )
    p.neon.ring(r + 0.05, 0.5, 12, N, Placement(boss_point(x, rear - 3, ENGINE_H), 0, QUARTER))
    p.hull.box(
        [1.6, WING_LOW - ENGINE_H + 0.6, ENGINE_HALF + 4],
        M.base,
        Placement(boss_point(x, rear - 4, ENGINE_H + 1)),
    )
    if whole:
        _fan(p, x, y - ENGINE_HALF, -1)
        p.neon.box([0.5, 0.3, 10], N, Placement(boss_point(x, y - 2, ENGINE_H + r - 0.1)))


def _fan(p: Any, x: float, front: float, half: int) -> None:
    """Draw an engine's front at `x` (`front` its Y): intake lip, fan blades, spinner.

    `half` -1: all of it; 0 or 1: one half (an armour piece flying off as the fan splits).
    """
    at = boss_point(x, front, ENGINE_H)
    r = ENGINE_R
    for k in range(12):
        a = (k + 0.5) * math.pi / 6
        if half >= 0 and (1 if math.sin(a) < 0 else 0) != half:
            continue
        width = 2 * r * math.sin(math.pi / 12) * 1.1
        lip = [at[0] - math.sin(a) * (r - 0.8), at[1] + math.cos(a) * (r - 0.8), at[2] - 0.5]
        p.hull.box([width, 1.2, 2.2], M.base, Placement(lip, 0, 0, a))
        if k % 3 == 0:
            p.neon.box([width, 0.3, 0.6], N, Placement([lip[0], lip[1], lip[2] + 0.9], 0, 0, a))
    for k in range(BLADES * 2):
        a = (k + 0.25) * math.pi / BLADES
        if half >= 0 and (1 if math.sin(a) < 0 else 0) != half:
            continue
        p.bare.box([1.1, r - 1.1, 0.35], M.dark, Placement([at[0], at[1], at[2] - 0.6], 0, 0, a))
    if half != 1:
        p.hull.cylinder(
            1.6, 2.2, 8, M.panel, Placement([at[0], at[1], at[2] - 0.6], 0, QUARTER), 0.3
        )


def _fan_piece(x: float, half: int) -> Any:
    """One half of an outer engine's fan, flying off as it splits (FB-STRATOLINER-COLOSSUS-10)."""

    def draw(p: Any) -> None:
        _fan(p, x, engine_y(abs(x)) - ENGINE_HALF, half)

    return draw


def _fans_whole(p: Any) -> None:
    """Draw the outer engines' fans, intakes and spinners (their armour region)."""
    for x in [ENGINE_X[2], -ENGINE_X[2]]:
        _fan(p, x, engine_y(abs(x)) - ENGINE_HALF, -1)


def _fans_frame(p: Any) -> None:
    """Draw what the fans leave (BOSS-44): a dark pedestal in each opened nacelle, a lit seam.

    The gatling's pod stands on it; once the gatling is destroyed, its stump does.
    """
    for x in [ENGINE_X[2], -ENGINE_X[2]]:
        at = boss_point(x, GATLING_AT[1], 0)
        p.bare.box(
            [ENGINE_R * 1.5, GATLING_POD[0] + 0.2, 8], M.dark, Placement([at[0], 0.5, at[2]])
        )
        p.neon.box([0.4, 0.3, 7], N, Placement([at[0], GATLING_POD[0] + 0.7, at[2]]))


def _tail(p: Any) -> None:
    """Draw the tail (FB-STRATOLINER-COLOSSUS-02): the swept tailplane and the tall fin.

    Lit tips and a lit rudder stripe.
    """
    plane = [
        _model(4, TAIL_ROOT[0]),
        _model(TAIL_SPAN, TAIL_TIP[0]),
        _model(TAIL_SPAN, TAIL_TIP[1]),
        _model(4, TAIL_ROOT[1]),
        _model(-4, TAIL_ROOT[1]),
        _model(-TAIL_SPAN, TAIL_TIP[1]),
        _model(-TAIL_SPAN, TAIL_TIP[0]),
        _model(-4, TAIL_ROOT[0]),
    ]
    p.hull.bevel_slab(
        plane, [TAIL_H - 1, TAIL_H - 0.3, TAIL_H + 0.6], [0, 0.5], M.base, None, M.panel
    )
    for side in [-1, 1]:
        p.neon.box(
            [1.2, 0.4, TAIL_TIP[1] - TAIL_TIP[0] - 1],
            N,
            Placement(
                boss_point(side * (TAIL_SPAN - 0.6), (TAIL_TIP[0] + TAIL_TIP[1]) / 2, TAIL_H + 0.5)
            ),
        )
    base = fuselage_at(FIN_ROOT[0])[2] - 1
    fin = [
        [base, -FIN_ROOT[0]],
        [base, -FIN_ROOT[1]],
        [FIN_TOP, -FIN_TIP[1]],
        [FIN_TOP, -FIN_TIP[0]],
    ]
    p.hull.slab(fin, [-0.9, 0.9], M.base, Placement([0, 0, 0], 0, 0, QUARTER), M.panel)
    p.neon.box([2, FIN_TOP - base - 3, 0.5], N, Placement([0, base + 1.5, -FIN_ROOT[1] + 1.5]))
    p.neon.box(
        [2, 0.5, FIN_TIP[1] - FIN_TIP[0] - 1],
        N,
        Placement(boss_point(0, (FIN_TIP[0] + FIN_TIP[1]) / 2, FIN_TOP - 0.3)),
    )


def _flaps_whole(p: Any) -> None:
    """Draw the flaps at rest (their armour region): the rig's flaps, as they lie on the wing."""
    for entry in rest_flaps():
        paint_posed(p, entry[0], entry[1])


def _flaps_frame(p: Any) -> None:
    """Draw what the flaps leave (BOSS-44): dark flap wells in the wing, a lit seam."""
    for side in [-1, 1]:
        well = [_model(side * q[0], q[1]) for q in FLAP]
        p.bare.slab(well, [WING_TOP - 0.1, WING_TOP + 0.15], M.dark)
        x = side * (FLAP[0][0] + FLAP[1][0]) / 2
        y = (FLAP[0][1] + FLAP[1][1]) / 2 + 0.8
        turn = -side * math.atan2(FLAP[1][1] - FLAP[0][1], FLAP[1][0] - FLAP[0][0])
        p.neon.box([28, 0.25, 0.4], N, Placement(boss_point(x, y, WING_TOP + 0.15), turn))


def _nose_whole(p: Any) -> None:
    """Draw the nose cone at rest (its armour region): the rig's two halves, closed."""
    for entry in rest_noses():
        paint_posed(p, entry[0], entry[1])
    tip = boss_point(0, -88.5, 8)
    p.neon.cylinder(0.6, 3, 6, N, Placement(tip, 0, QUARTER), 0.2)


def _nose_frame(p: Any) -> None:
    """Draw what the nose cone leaves (BOSS-44): the bulkhead, a keel under the lance."""
    keel = [_model(q[0] * 0.7, q[1]) for q in NOSE]
    p.bare.slab(keel, [2, 3], M.dark)
    at = boss_point(0, NOSE_JOINT - 0.5, 0)
    p.hull.box([17, 13, 1], M.base, Placement([at[0], 2.5, at[2]]))
    p.neon.box([12, 0.4, 0.4], N, Placement([at[0], 3.2, at[2] + 0.6]))
    p.neon.box([0.4, 0.3, 14], N, Placement(boss_point(0, LANCE_AT[1] - 2, 3)))


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over the spine rotor (BOSS-58): an octagonal cap, a lit seam round it."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.bevel_slab(
        polygon(8, 6.5), [SPINE_H - 0.8, SPINE_H, SPINE_H + 1.2], [0, 0.8], M.panel, Placement(at)
    )
    p.neon.ring(6.0, 0.25, 8, N, Placement([at[0], SPINE_H + 0.4, at[2]], math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.ring(6.3, 1.2, 12, M.base, Placement([at[0], SPINE_H - 0.9, at[2]]))
    p.neon.ring(6.3, 0.3, 12, N, Placement([at[0], SPINE_H + 0.1, at[2]]))


def _wing_gun(p: Any, at: Vec3) -> None:
    """Add a wing gun's barbette (FB-STRATOLINER-COLOSSUS-03): an armoured octagon on the wing."""
    p.hull.bevel_slab(
        polygon(8, 5.4),
        [WING_TOP - 0.3, WING_GUN_H - 0.5, WING_GUN_H],
        [0, 0.6],
        M.base,
        Placement([at[0], 0, at[2]], math.pi / 8),
        M.panel,
    )
    p.neon.ring(5.45, 0.35, 8, N, Placement([at[0], WING_GUN_H - 0.9, at[2]], math.pi / 8))


def _nacelle_gun(p: Any, at: Vec3) -> None:
    """Add an outer nacelle's gun collar (FB-STRATOLINER-COLOSSUS-03): a saddle on its cowling."""
    gun = boss_point(-at[0], -at[2] - 4, 0)
    p.hull.bevel_slab(
        polygon(8, 4.2),
        [ENGINE_H + ENGINE_R - 0.8, NACELLE_GUN_H - 0.4, NACELLE_GUN_H],
        [0, 0.4],
        M.base,
        Placement([gun[0], 0, gun[2]], math.pi / 8),
        M.panel,
    )
    p.neon.ring(4.25, 0.3, 8, N, Placement([gun[0], NACELLE_GUN_H - 0.7, gun[2]], math.pi / 8))


def _tail_gun(p: Any, _at: Vec3) -> None:
    """Add the tail gun's housing (FB-STRATOLINER-COLOSSUS-03): an armoured drum on its tail."""
    gun = boss_point(TAIL_GUN_AT[0], TAIL_GUN_AT[1], 0)
    p.hull.cylinder(5, TAIL_GUN_H - 6, 10, M.panel, Placement([gun[0], 6, gun[2]]), 4.4)
    p.neon.ring(4.5, 0.4, 10, N, Placement([gun[0], TAIL_GUN_H - 0.8, gun[2]]))


def build_stratoliner_colossus(scene: Any) -> Any:
    """FB-STRATOLINER-COLOSSUS-01, FB-STRATOLINER-COLOSSUS-04: the Stratoliner Colossus.

    A colossal six-engine swept-wing jet, about 5 L across; peach lights.
    """

    def core(p: Any) -> None:
        _fuselage(p)
        _wings(p)
        for x in ENGINE_X:
            outer = x == ENGINE_X[2]
            _nacelle(p, x, not outer)
            _nacelle(p, -x, not outer)
        _tail(p)

    return build_boss_model(
        STRATOLINER_COLOSSUS,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "wing-gun-left": _wing_gun,
                "wing-gun-right": _wing_gun,
                "nacelle-left": _nacelle_gun,
                "nacelle-right": _nacelle_gun,
                "tail-gun": _tail_gun,
            },
            # FB-STRATOLINER-COLOSSUS-05: its morphs (petals, cores, flaps, tier, nose halves).
            "rig": {"build": build_colossus_rig, "triangles": rig_triangles},
            "armour": {
                "fans": {
                    "whole": _fans_whole,
                    "pieces": [
                        _fan_piece(x, h) for x in [ENGINE_X[2], -ENGINE_X[2]] for h in [0, 1]
                    ],
                    "frame": _fans_frame,
                },
                "flaps": {"whole": _flaps_whole, "pieces": [], "frame": _flaps_frame},
                "nose": {"whole": _nose_whole, "pieces": [], "frame": _nose_frame},
                "rotor-hatch": {"whole": _draw_hatch, "frame": _draw_hatch_frame},
            },
        },
    )
