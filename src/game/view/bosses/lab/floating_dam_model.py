# Copyright (c) 2026 Renaud Guillon
"""FB-FLOATING-DAM-01, FB-FLOATING-DAM-02: the Floating Dam, the Lab's L-21 final boss.

Logical pixels, nose +Z, Y up (towards the camera). A curved concrete arch dam flying sideways
across the screen, seen from above: its wall swept along its curve (a buttressed back, a road on its
crest, a sloping face), a spillway notch in its middle with a weir, a stepped chute and a stilling
basin, abutments at its ends with power pylons on them and the lines strung over the crest, sluice
bays and outfall ledges in its face, hoists over its gates, lift fans under its back
(`floating_dam_rig`). A machine, not a creature (the Lab's fifth round, user request 2026-11-06).
"""

import math

from game.config.bosses.lab.floating_dam import (
    ABUTMENT,
    BASIN,
    BASTION_TOP,
    CREST,
    CREST_Y,
    FLOATING_DAM,
    GATE,
    NOTCH,
    OUTLET_AT,
    OUTLET_HATCH,
    OUTLET_TOP,
    PYLON_AT,
    PYLON_TOP,
    SECTION,
    SILL,
    SLUICE_AT,
    SPAN,
    TOWER,
    TOWER_AT,
    WEIR_TOP,
    crest_y,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_greebles import rod
from game.view.bosses.lab.floating_dam_parts import (
    ASPHALT,
    CONCRETE,
    COURSE,
    ROOF,
    STEEL,
    N,
    dam_armour,
    gatehouse,
    hall,
    lit_bar,
    on_face,
    outline_of,
    sluice,
)
from game.view.bosses.lab.floating_dam_rig import FAN_AT, build_dam_rig, rig_triangles
from game.view.bosses.world_1_organic_kit import M
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


# How many stretches each half of the wall is swept in, between the notch and the abutment.
STRETCHES = 9
# Where buttresses stand on its back, lamps on its crest and joints run down its face (|x|).
BUTTRESSES = [24, 46, 70, 90]
LAMPS = [20, 40, 58, 76, 94]
JOINTS = [30, 53, 79]
# The masts by the notch the power lines rest on, and their top.
MAST_X = 18
MAST_TOP = 40


def _station(x: float) -> list[Vec3]:
    """Return the wall's section at `x` as model points, from its back foot round to its toe."""
    y = crest_y(x)
    return [boss_point(x, y - s[0], s[1]) for s in SECTION]


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _dot(a: Vec3, b: Vec3) -> float:
    return float(a[0] * b[0] + a[1] * b[1] + a[2] * b[2])


def _quad(builder: Any, corners: list[Vec3], inside: Vec3, color: Any) -> None:
    """Add a face of `corners`, wound so that it faces away from `inside` (model)."""
    n = _cross(_sub(corners[1], corners[0]), _sub(corners[2], corners[0]))
    if _dot(n, _sub(corners[0], inside)) < 0:
        corners = [corners[k] for k in range(len(corners) - 1, -1, -1)]
    builder.face(corners, color)


def _band_color(k: int) -> Any:
    """Return the colour of the wall's band `k` of its section (its crest's top is the road)."""
    if k == 1:
        return ASPHALT
    if k == 0 or k == len(SECTION) - 1:
        return COURSE
    return CONCRETE


def _sweep(p: Any, x0: float, x1: float) -> None:
    """Sweep the wall's section along its curve from `x0` to `x1`, capping its end at `x0`."""
    for i in range(STRETCHES):
        xa = x0 + (x1 - x0) * i / STRETCHES
        xb = x0 + (x1 - x0) * (i + 1) / STRETCHES
        a = _station(xa)
        b = _station(xb)
        mid = boss_point((xa + xb) / 2, crest_y((xa + xb) / 2) - 8, 8)
        n = len(SECTION)
        for k in range(n):
            j = (k + 1) % n
            _quad(p.hull, [a[k], a[j], b[j], b[k]], mid, _band_color(k))
    cap = _station(x0)
    inside = boss_point(x0 + (1 if x1 > x0 else -1) * 5, crest_y(x0) - 8, 8)
    _quad(p.hull, cap, inside, CONCRETE)


def _draw_wall(p: Any) -> None:
    """Draw the wall (FB-FLOATING-DAM-02): both halves either side of the spillway notch.

    Its road's lane line and parapets along the crest, lamps over it, lit joints down its face,
    buttresses on its back.
    """
    for s in [-1, 1]:
        _sweep(p, s * NOTCH, s * SPAN)
        for k in range(STRETCHES):
            xa = s * (NOTCH + (SPAN - NOTCH) * k / STRETCHES)
            xb = s * (NOTCH + (SPAN - NOTCH) * (k + 1) / STRETCHES)
            if k % 2 == 0:
                a = boss_point(xa + s * 1, crest_y(xa) + 0.5, CREST + 0.05)
                b = boss_point(xb - s * 1, crest_y(xb) + 0.5, CREST + 0.05)
                lit_bar(p, a, b, 0.5)
            for d in [-5.4, 4.4]:
                a = boss_point(xa, crest_y(xa) - d, CREST)
                b = boss_point(xb, crest_y(xb) - d, CREST)
                lit_bar(p, [a[0], a[1] + 0.6, a[2]], [b[0], b[1] + 0.6, b[2]], 1.1, COURSE)
        for x in LAMPS:
            q = boss_point(s * x, crest_y(s * x) - 4.6, CREST)
            p.hull.cylinder(0.35, 4, 4, M.base, Placement(q))
            p.neon.box([1.2, 0.6, 1.2], N, Placement([q[0], CREST + 4, q[2]]))
        for x in JOINTS:
            lit_bar(p, on_face(s * x, 5.6, 0.15), on_face(s * x, 20.5, 0.15), 0.55)
        for x in BUTTRESSES:
            q = boss_point(s * x, crest_y(s * x) + 8, -10)
            p.hull.box([4, 30, 5], COURSE, Placement(q, math.atan2(-s * 2 * 18 * x / 10000, 1)))


def _draw_notch(p: Any) -> None:
    """Draw the spillway (FB-FLOATING-DAM-12): its weir, its stepped chute, its stilling basin.

    The bridge's leaves cover the weir and the cover the chute and the basin until they open.
    """
    y = CREST_Y
    weir = [[-NOTCH, y - 6], [NOTCH, y - 6], [NOTCH, y + 6], [-NOTCH, y + 6]]
    p.hull.slab(outline_of(weir), [-10, WEIR_TOP], CONCRETE, None, COURSE)
    p.neon.box([2 * NOTCH - 2, 0.3, 0.5], N, Placement(boss_point(0, y - 5.6, WEIR_TOP)))
    for k in range(4):
        d0 = 6 + k * 3.8
        h = WEIR_TOP - (k + 1) * 3.2
        step = [[-NOTCH, y - d0], [NOTCH, y - d0], [NOTCH, y - d0 - 3.8], [-NOTCH, y - d0 - 3.8]]
        p.hull.slab(outline_of(step), [-8, h], CONCRETE, None, COURSE)
        p.bare.box([2 * NOTCH - 1, 0.2, 0.5], M.dark, Placement(boss_point(0, y - d0 - 0.4, h)))
    basin = [[-BASIN[0], BASIN[1]], [BASIN[0], BASIN[1]], [BASIN[0], y - 21], [-BASIN[0], y - 21]]
    p.hull.slab(outline_of(basin), [-6, BASIN[2]], COURSE)
    for s in [-1, 1]:
        wall = [[s * (BASIN[0] - 1.5), BASIN[1]], [s * BASIN[0], BASIN[1]]]
        wall.append([s * BASIN[0], y - 6])
        wall.append([s * (BASIN[0] - 1.5), y - 6])
        p.hull.slab(outline_of(wall), [BASIN[2], 6], CONCRETE)
    # The bridge's hinges and counterweight pits at the notch's sides.
    for s in [-1, 1]:
        q = boss_point(s * (NOTCH + 1.2), y + 0.5, CREST)
        p.hull.box([2.4, 1.6, 11], M.panel, Placement(q))
        p.neon.box([0.5, 0.4, 11], N, Placement([q[0], CREST + 1.6, q[2]]))


def _draw_abutments(p: Any) -> None:
    """Draw the abutments at the wall's ends (FB-FLOATING-DAM-02), their bastions and pylons."""
    a = ABUTMENT
    for s in [-1, 1]:
        tower = [[s * a[0], -20], [s * a[1], -20], [s * a[1], a[3]], [s * a[0], a[3]]]
        p.hull.bevel_slab(outline_of(tower), [-14, a[4] - 2, a[4]], [2, 1], CONCRETE, None, COURSE)
        bastion = [[s * a[0], a[2]], [s * a[1], a[2]], [s * a[1], -19], [s * a[0], -19]]
        p.hull.bevel_slab(
            outline_of(bastion), [-12, BASTION_TOP - 1.5, BASTION_TOP], [3, 0.8], CONCRETE
        )
        for h in [4, 10]:
            q = boss_point(s * (a[0] + a[1]) / 2, a[2] - 0.05, h)
            p.neon.box([a[1] - a[0] - 4, 0.6, 0.3], N, Placement(q))
        _pylon(p, s)


def _pylon(p: Any, s: float) -> None:
    """Add a lattice pylon on an abutment: four legs tapering up, cross arms, lit insulators."""
    x = s * PYLON_AT[0]
    y = PYLON_AT[1]
    base = ABUTMENT[4]
    top = PYLON_TOP
    feet = [[-3.5, -3.5], [3.5, -3.5], [3.5, 3.5], [-3.5, 3.5]]
    for f in feet:
        a = boss_point(x + f[0], y + f[1], base)
        b = boss_point(x + f[0] * 0.25, y + f[1] * 0.25, top)
        rod(p.hull, a, b, 0.4, M.panel)
    for k in range(2):
        h = base + 9 + k * 9
        for f in [[-1.0, 0.0], [1.0, 0.0]]:
            w = 3.5 - (h - base) / (top - base) * 2.6
            a = boss_point(x + f[0] * w, y - w, h)
            b = boss_point(x - f[0] * w, y + w, h + 9)
            rod(p.hull, a, b, 0.22, M.base)
    for h in [top - 7, top - 2]:
        a = boss_point(x, y - 7, h)
        b = boss_point(x, y + 7, h)
        rod(p.hull, a, b, 0.4, M.panel)
        for e in [-6.5, 6.5]:
            q = boss_point(x, y + e, h - 1.6)
            p.neon.cylinder(0.5, 1.6, 4, N, Placement(q))


def _sag(a: Vec3, b: Vec3, t: float, drop: float) -> Vec3:
    """Return the point `t` of the way from `a` to `b` on a line sagging `drop` in its middle."""
    return [
        a[0] + (b[0] - a[0]) * t,
        a[1] + (b[1] - a[1]) * t - drop * 4 * t * (1 - t),
        a[2] + (b[2] - a[2]) * t,
    ]


def _draw_lines(p: Any) -> None:
    """Draw the power lines strung from pylon to pylon over the crest, resting on two masts."""
    for s in [-1, 1]:
        q = boss_point(s * MAST_X, CREST_Y + 4.5, CREST)
        p.hull.cylinder(0.7, MAST_TOP - CREST, 4, M.panel, Placement(q), 0.4)
        rod(
            p.hull,
            boss_point(s * MAST_X, CREST_Y - 2.5, MAST_TOP),
            boss_point(s * MAST_X, CREST_Y + 11.5, MAST_TOP),
            0.35,
            M.panel,
        )
    for h in [PYLON_TOP - 7, PYLON_TOP - 2]:
        for e in [-6.5, 6.5]:
            spans: list[list[Any]] = [
                [
                    boss_point(-PYLON_AT[0], PYLON_AT[1] + e, h - 1.6),
                    boss_point(-MAST_X, CREST_Y + 4.5 + e, MAST_TOP),
                    9,
                ],
                [
                    boss_point(-MAST_X, CREST_Y + 4.5 + e, MAST_TOP),
                    boss_point(MAST_X, CREST_Y + 4.5 + e, MAST_TOP),
                    3,
                ],
                [
                    boss_point(MAST_X, CREST_Y + 4.5 + e, MAST_TOP),
                    boss_point(PYLON_AT[0], PYLON_AT[1] + e, h - 1.6),
                    9,
                ],
            ]
            for span in spans:
                count = 4 if span[2] > 5 else 1
                for k in range(count):
                    a = _sag(span[0], span[1], k / count, span[2])
                    b = _sag(span[0], span[1], (k + 1) / count, span[2])
                    rod(p.neon, a, b, 0.18, N)


def _draw_face(p: Any) -> None:
    """Draw what stands out of the face (FB-FLOATING-DAM-02, -03, -10).

    The outer sluices' outlet sills (their guns stand on them), the inner gates' dark bays, hoist
    gantries over them on the crest and the outfall ledges in front, the weir outlets' hoods.
    """
    for s in [-1, 1]:
        x = s * SLUICE_AT[0]
        sill = [
            [x - SILL[0], SILL[1]],
            [x + SILL[0], SILL[1]],
            [x + SILL[0], SILL[2]],
            [x - SILL[0], SILL[2]],
        ]
        p.hull.bevel_slab(outline_of(sill), [-4, SILL[3] - 1, SILL[3]], [0, 0.6], CONCRETE)
        p.bare.box(
            [2 * SILL[0] - 2, 0.2, 0.6], M.dark, Placement(boss_point(x, SILL[1] + 1, SILL[3]))
        )
        # The inner gate's bay: dark in the face under its panel; its ledge; its hoist.
        x0 = s * (GATE[0] + 1)
        x1 = s * (GATE[1] - 1)
        p.bare.face(
            [on_face(x0, 6, 0.2), on_face(x1, 6, 0.2), on_face(x1, 19, 0.2), on_face(x0, 19, 0.2)]
            if s < 0
            else [
                on_face(x1, 6, 0.2),
                on_face(x0, 6, 0.2),
                on_face(x0, 19, 0.2),
                on_face(x1, 19, 0.2),
            ],
            M.dark,
        )
        gx = s * (GATE[0] + GATE[1]) / 2
        ledge = [[s * GATE[0], GATE[2]], [s * GATE[1], GATE[2]], [s * GATE[1], crest_y(gx) - 19]]
        ledge.append([s * GATE[0], crest_y(gx) - 19])
        p.hull.bevel_slab(outline_of(ledge), [-4, 0, 1], [1.5, 0.4], COURSE)
        p.neon.box(
            [GATE[1] - GATE[0] - 2, 0.3, 0.4], N, Placement(boss_point(gx, GATE[2] + 0.6, 1))
        )
        for xg in [GATE[0], GATE[1]]:
            q = boss_point(s * xg, crest_y(s * xg) - 1, CREST)
            p.hull.box([1.6, 12, 1.6], STEEL, Placement(q))
        beam = boss_point(gx, crest_y(gx) - 1, CREST + 12)
        p.hull.box([GATE[1] - GATE[0] + 1.6, 1.6, 2.4], STEEL, Placement(beam), ROOF)
        p.neon.box(
            [GATE[1] - GATE[0] - 2, 0.3, 0.5], N, Placement([beam[0], CREST + 13.6, beam[2]])
        )
        # The weir outlet's hood under its hatch.
        o = [s * OUTLET_AT[0], OUTLET_AT[1]]
        hood = [
            [o[0] - OUTLET_HATCH[0], o[1] - OUTLET_HATCH[1]],
            [o[0] + OUTLET_HATCH[0], o[1] - OUTLET_HATCH[1]],
        ]
        hood.append([o[0] + OUTLET_HATCH[0], o[1] + OUTLET_HATCH[1]])
        hood.append([o[0] - OUTLET_HATCH[0], o[1] + OUTLET_HATCH[1]])
        p.hull.slab(outline_of(hood), [0, OUTLET_TOP - 0.2], CONCRETE)


def _draw_tower(p: Any) -> None:
    """Draw the control tower on the crest (FB-FLOATING-DAM-07): lit windows, the turret's seat."""
    x = TOWER_AT[0]
    y = TOWER_AT[1]
    body = [
        [x - TOWER[0], y - TOWER[1]],
        [x + TOWER[0], y - TOWER[1]],
        [x + TOWER[0], y + TOWER[1]],
    ]
    body.append([x - TOWER[0], y + TOWER[1]])
    p.hull.bevel_slab(
        outline_of(body), [CREST, TOWER[2] - 1.5, TOWER[2]], [0, 0.6], CONCRETE, None, ROOF
    )
    q = boss_point(x, y - TOWER[1] - 0.05, TOWER[2] - 3.5)
    p.neon.box([2 * TOWER[0] - 2, 1.2, 0.3], N, Placement(q))
    m = boss_point(x + TOWER[0] - 1.2, y + TOWER[1] - 1.2, TOWER[2])
    p.hull.cylinder(0.3, 6, 4, M.base, Placement(m))
    p.neon.box([0.8, 0.8, 0.8], N, Placement([m[0], TOWER[2] + 6, m[2]]))


def _draw_fan_mounts(p: Any) -> None:
    """Draw the lift fans' ducts under the wall's back and their struts (the rotors spin, rig)."""
    for f in FAN_AT:
        q = boss_point(f[0], f[1], -6)
        p.hull.lathe(
            [[8.5, 0], [9.2, 3], [8.6, 6], [7.4, 6], [7.4, 0]], 12, STEEL, Placement(q), False
        )
        p.neon.ring(8.7, 0.5, 12, N, Placement([q[0], 6, q[2]]))
        p.bare.cylinder(7.3, 0.2, 12, M.dark, Placement([q[0], 0.4, q[2]]))
        s = boss_point(f[0], f[1] - 7, -4)
        p.hull.box([3, 6, 8], COURSE, Placement(s))


def build_floating_dam(scene: Any) -> Any:
    """FB-FLOATING-DAM-01, FB-FLOATING-DAM-02: the Floating Dam.

    Weathered concrete and steel, water-blue light lines (shown green) on its crest and face.
    """

    def core(p: Any) -> None:
        _draw_fan_mounts(p)
        _draw_wall(p)
        _draw_notch(p)
        _draw_abutments(p)
        _draw_face(p)
        _draw_tower(p)
        _draw_lines(p)

    return build_boss_model(
        FLOATING_DAM,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "sluice-left": sluice,
                "sluice-right": sluice,
                "gatehouse-left": gatehouse,
                "gatehouse-right": gatehouse,
                "hall": hall,
            },
            "armour": dam_armour(),
            "rig": {"build": build_dam_rig, "triangles": rig_triangles},
        },
    )
