# Copyright (c) 2026 Renaud Guillon
"""MB-BUNKER-SAUCER-01, MB-BUNKER-SAUCER-02: the Bunker Saucer, the Lab's L-24 mini boss.

Logical pixels, nose +Z, Y up (towards the camera). A gigantic flying concrete pillbox seen from
above: a thick saucer of cast concrete, its belly a shallow lens, a lit steel belt round its rim, a
parapet round its rim deck notched with slit embrasures, two stepped rings rising to a crown, the
observation cupola on the crown (two halves, moving pieces, BOSS-45), the pillbox drum on the
front step, the lift-jet sockets on the rim's back quarters. Its parts (the pillbox's armoured
collar, the lift-jet nacelles) and armour (the cupola's halves, the rotor's hatch) are drawn here
too; the slits' shutters, the periscope and the cupola's rams move on its rig
(`bunker_saucer_rig`). Concrete and steel with red light lines (shown yellow), not a creature (the
Lab's fifth round, user request 2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.bunker_saucer import (
    BUNKER_SAUCER,
    CROWN,
    CUPOLA_RADIUS,
    CUPOLA_SLIDE,
    CUPOLA_TOP,
    DECK,
    HATCH_RADIUS,
    JET_AT,
    JET_RADIUS,
    NOTCH_HALF,
    PARAPET,
    PILLBOX_AT,
    PILLBOX_RADIUS,
    PILLBOX_TOP,
    RIM,
    ROTOR_AT,
    SLIT_DEGS,
    STEP,
    slit_at,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.bunker_saucer_rig import build_saucer_rig, rig_triangles
from game.view.bosses.world_1_organic_kit import M
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["bunker-saucer"]
# Cast concrete, a darker course of it, and the steel of its fittings.
CONCRETE = [0.115, 0.115, 0.112]
COURSE = [0.08, 0.08, 0.08]
STAIN = [0.05, 0.05, 0.05]
SIDES = 20
# The saucer's profile, `[radius, height]` from the middle of its belly to its rim deck.
BELLY = [  # type: list[list[float]]
    [0, -15],
    [20, -13.4],
    [36, -9],
    [48, -4.2],
    [55, -0.6],
    [RIM, 2],
    [RIM, 5.4],
    [PARAPET[1] + 0.3, DECK],
]
# The jets' sockets break the parapet this many degrees either side of their centres.
JET_GAP = 13


def pt(x: float, y: float) -> list[float]:
    """Return a config point `(x, y)` as a slab outline point (model X, Z)."""
    return [-x, -y]


def _angle(at: list[Any]) -> float:
    """Return the angle of a config point round the centre (degrees, counter-clockwise from +X)."""
    return math.atan2(at[1], at[0]) * 180 / math.pi


def _arc(r0: float, r1: float, a0: float, a1: float) -> list[list[float]]:
    """Return the slab outline of the ring sector `r0..r1` between `a0` and `a1` degrees."""
    steps = max(1, math.ceil((a1 - a0) / 9))
    outer: list[list[float]] = []
    inner: list[list[float]] = []
    for k in range(steps + 1):
        a = (a0 + (a1 - a0) * k / steps) * math.pi / 180
        outer.append(pt(r1 * math.cos(a), r1 * math.sin(a)))
        inner.append(pt(r0 * math.cos(a), r0 * math.sin(a)))
    result = list(outer)
    result.extend([inner[len(inner) - 1 - k] for k in range(len(inner))])
    return result


def _gaps() -> list[list[float]]:
    """Return the parapet's gaps `[from, to]` (degrees), sorted: its notches, the jets' sockets."""
    half = NOTCH_HALF / ((PARAPET[0] + PARAPET[1]) / 2) * 180 / math.pi
    gaps: list[list[float]] = []
    for k in range(len(SLIT_DEGS)):
        for side in [1, -1]:
            a = _angle(slit_at(k, side))
            gaps.append([a - half, a + half])
    for side in [1, -1]:
        a = _angle([side * JET_AT[0], JET_AT[1]])
        gaps.append([a - JET_GAP, a + JET_GAP])
    gaps.sort(key=lambda g: g[0])
    return gaps


def _draw_saucer(p: Any) -> None:
    """Draw the saucer (MB-BUNKER-SAUCER-01): its concrete lens, its rim's lit steel belt.

    Steel bands round its rim face, a lit seam between them, lamps along its edge.
    """
    p.flesh.lathe(BELLY, SIDES, CONCRETE)
    p.hull.ring(RIM + 0.05, 1.6, SIDES, M.base, Placement([0, 2.2, 0]))
    p.neon.ring(RIM + 0.1, 0.5, SIDES, N, Placement([0, 3.2, 0]))
    for k in range(6):
        a = (k + 0.5) * math.pi / 3
        q = [math.cos(a) * (RIM + 0.15), 4.5, math.sin(a) * (RIM + 0.15)]
        p.charge.box([0.9, 0.6, 0.9], N, Placement(q, -a))


def _draw_parapet(p: Any) -> None:
    """Draw the parapet round the rim deck (MB-BUNKER-SAUCER-03): concrete, notched for the slits.

    Steel facings on each notch's cheeks, a dark sill under each gun, a lit strip along its top.
    """
    gaps = _gaps()
    for i in range(len(gaps)):
        a0 = gaps[i][1]
        a1 = gaps[(i + 1) % len(gaps)][0]
        if a1 < a0:
            a1 += 360
        p.flesh.bevel_slab(
            _arc(PARAPET[0], PARAPET[1], a0, a1),
            [DECK, PARAPET[2] - 0.8, PARAPET[2]],
            [0, 0.5],
            CONCRETE,
            None,
            COURSE,
        )
        mid = (a0 + a1) / 2 * math.pi / 180
        r = PARAPET[1] - 0.6
        at = boss_point(r * math.cos(mid), r * math.sin(mid), PARAPET[2] - 0.2)
        span = (a1 - a0) * math.pi / 180 * r
        p.neon.box(
            [0.4, 0.4, span * 0.7], N, Placement(at, math.atan2(-math.sin(mid), math.cos(mid)))
        )
    for k in range(len(SLIT_DEGS)):
        for side in [1, -1]:
            _draw_notch(p, slit_at(k, side))


def _draw_notch(p: Any, at: list[Any]) -> None:
    """Draw a slit's notch: steel cheeks either side, a dark sill, a lit lintel over its mouth."""
    a = math.atan2(at[1], at[0])
    c = math.cos(a)
    s = math.sin(a)
    # Along the rim (tangent) and out of it (normal), config axes.
    tx = -s
    ty = c
    mid = (PARAPET[0] + PARAPET[1]) / 2
    yaw = math.atan2(-c, -s)
    for side in [-1, 1]:
        x = c * mid + tx * side * (NOTCH_HALF + 0.2)
        y = s * mid + ty * side * (NOTCH_HALF + 0.2)
        p.hull.box(
            [0.7, PARAPET[2] - DECK + 0.4, PARAPET[1] - PARAPET[0] + 0.4],
            M.panel,
            Placement(boss_point(x, y, DECK), yaw),
        )
    sill = boss_point(c * mid, s * mid, DECK)
    p.bare.box([2 * NOTCH_HALF, 0.15, PARAPET[1] - PARAPET[0]], STAIN, Placement(sill, yaw))
    lip = boss_point(c * (PARAPET[1] + 0.1), s * (PARAPET[1] + 0.1), DECK - 0.6)
    p.neon.box([2 * NOTCH_HALF - 0.6, 0.35, 0.35], N, Placement(lip, yaw))


def _draw_steps(p: Any) -> None:
    """Draw the two stepped rings over the rim deck (MB-BUNKER-SAUCER-02) and their details.

    Cast concrete with a darker course at each foot, buttresses round the lower step, expansion
    joints across the deck, a lit band round each step's face.
    """
    p.flesh.lathe(
        [[STEP[0] + 0.6, DECK], [STEP[0], STEP[1] - 1], [STEP[0] - 1, STEP[1]], [0, STEP[1]]],
        SIDES,
        CONCRETE,
    )
    p.flesh.lathe(
        [
            [CROWN[0] + 0.6, STEP[1]],
            [CROWN[0], CROWN[1] - 1],
            [CROWN[0] - 1, CROWN[1]],
            [0, CROWN[1]],
        ],
        SIDES,
        CONCRETE,
    )
    p.flesh.ring(STEP[0] + 0.65, 1.2, SIDES, COURSE, Placement([0, DECK, 0]))
    p.flesh.ring(CROWN[0] + 0.65, 1.0, SIDES, COURSE, Placement([0, STEP[1], 0]))
    p.neon.ring(STEP[0] + 0.25, 0.35, SIDES, N, Placement([0, STEP[1] - 2.6, 0]))
    p.neon.ring(CROWN[0] + 0.25, 0.35, SIDES, N, Placement([0, CROWN[1] - 2.2, 0]))
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        c = math.cos(a)
        s = math.sin(a)
        yaw = math.atan2(-c, -s)
        # A buttress against the lower step.
        foot = boss_point(c * (STEP[0] + 1.2), s * (STEP[0] + 1.2), DECK)
        p.flesh.box([2.4, STEP[1] - DECK - 1.5, 2.6], COURSE, Placement(foot, yaw))


def _draw_crown(p: Any) -> None:
    """Draw the crown's fittings (MB-BUNKER-SAUCER-02, MB-BUNKER-SAUCER-10).

    The rails the cupola's halves slide out on, the well under the cupola (dark, a ring of light,
    the periscope's housing), lamps round its edge, a radio mast, the rotor hatch's collar.
    """
    for side in [-1, 1]:
        for y in [-6.5, 6.5]:
            x = side * (CUPOLA_RADIUS + CUPOLA_SLIDE) / 2
            q = boss_point(x, y, CROWN[1])
            p.hull.box([CUPOLA_RADIUS + CUPOLA_SLIDE + 2, 0.6, 1.2], M.base, Placement(q))
    p.bare.cylinder(CUPOLA_RADIUS - 0.4, 0.25, 16, STAIN, Placement([0, CROWN[1], 0]))
    p.neon.ring(CUPOLA_RADIUS - 2.4, 0.3, 16, N, Placement([0, CROWN[1] + 0.2, 0]))
    p.hull.cylinder(3.6, 1.6, 8, M.panel, Placement([0, CROWN[1], 0]))
    p.hull.cylinder(2.2, 1.5, 8, M.base, Placement([0, CROWN[1] + 1.6, 0]))
    for k in range(8):
        a = (k + 0.5) * math.pi / 4
        q = [math.cos(a) * (CROWN[0] - 1.6), CROWN[1], math.sin(a) * (CROWN[0] - 1.6)]
        if abs(math.cos(a)) > 0.9:
            continue
        p.charge.box([1.1, 0.7, 1.1], N, Placement(q, -a))
    mast = boss_point(-21, 13, CROWN[1])
    p.hull.cylinder(1.3, 1.2, 6, M.panel, Placement(mast))
    p.hull.cylinder(0.35, 9, 4, M.base, Placement([mast[0], CROWN[1] + 1.2, mast[2]]))
    for h in [4, 7]:
        p.hull.box([3.2, 0.25, 0.25], M.base, Placement([mast[0], CROWN[1] + 1.2 + h, mast[2]]))
    p.neon.box([0.8, 0.8, 0.8], N, Placement([mast[0], CROWN[1] + 10.2, mast[2]]))
    hatch = boss_point(ROTOR_AT[0], ROTOR_AT[1], CROWN[1])
    p.hull.cylinder(HATCH_RADIUS + 1, 0.4, 8, M.base, Placement(hatch, math.pi / 8))


def _draw_pillbox_drum(p: Any) -> None:
    """Draw the pillbox's drum on the front step (MB-BUNKER-SAUCER-04): the turret's seat."""
    at = boss_point(PILLBOX_AT[0], PILLBOX_AT[1], 0)
    r = PILLBOX_RADIUS
    p.flesh.lathe(
        [[r + 1.2, STEP[1]], [r, STEP[1] + 1.2], [r, PILLBOX_TOP]],
        12,
        CONCRETE,
        Placement([at[0], 0, at[2]]),
    )
    p.hull.cylinder(r - 0.6, 0.3, 12, M.base, Placement([at[0], PILLBOX_TOP, at[2]]))


def _draw_jet_sockets(p: Any) -> None:
    """Draw the lift jets' sockets on the rim (MB-BUNKER-SAUCER-05): what is left once a jet goes.

    A steel ring sunk in the deck, a dark throat, a grille across it.
    """
    for side in [-1, 1]:
        at = boss_point(side * JET_AT[0], JET_AT[1], DECK)
        p.hull.cylinder(JET_RADIUS - 1, 0.4, 12, M.base, Placement(at))
        p.bare.cylinder(JET_RADIUS - 2.5, 0.2, 12, STAIN, Placement([at[0], DECK + 0.4, at[2]]))
        for k in range(3):
            p.hull.box(
                [0.5, 0.5, 2 * JET_RADIUS - 5],
                M.panel,
                Placement([at[0], DECK + 0.4, at[2]], k * math.pi / 3),
            )


def pillbox(p: Any, at: Vec3) -> None:
    """Draw the pillbox (MB-BUNKER-SAUCER-04): an armoured steel collar round its twin turret.

    Vision slits round it, lit; a hooded periscope and a whip aerial on its back.
    """
    x = at[0]
    z = at[2]
    r = PILLBOX_RADIUS + 0.6
    p.hull.lathe(
        [[r, PILLBOX_TOP - 0.6], [r, PILLBOX_TOP + 1.4], [r - 1.4, PILLBOX_TOP + 2.2]],
        12,
        M.panel,
        Placement([x, 0, z]),
        False,
    )
    p.hull.lathe(
        [[r - 1.4, PILLBOX_TOP + 2.2], [4.6, PILLBOX_TOP + 2.2]],
        12,
        M.base,
        Placement([x, 0, z]),
        False,
    )
    for k in range(6):
        a = (k + 0.5) * math.pi / 3
        q = [x + math.cos(a) * (r + 0.02), PILLBOX_TOP + 0.4, z + math.sin(a) * (r + 0.02)]
        p.neon.box([0.4, 0.5, 2.2], N, Placement(q, -a))
    back = [x, PILLBOX_TOP + 2.2, z - r + 1.4]
    p.hull.box([1.6, 2.6, 1.6], M.base, Placement(back))
    p.hull.box([2.2, 0.8, 2.4], M.panel, Placement([back[0], back[1] + 2.6, back[2] + 0.4]))
    p.hull.cylinder(0.2, 7, 4, M.base, Placement([x + 3.5, PILLBOX_TOP + 2.2, back[2]]))
    p.neon.box([0.5, 0.5, 0.5], N, Placement([x + 3.5, PILLBOX_TOP + 9.2, back[2]]))


def lift_jet(p: Any, at: Vec3) -> None:
    """Draw a lift-jet nacelle (MB-BUNKER-SAUCER-05): no gun, its intake facing up.

    A steel drum over its socket, its intake's fan blades under a grille ring, a lit lip, armoured
    fairings either side and its exhaust glowing out under the rim.
    """
    x = at[0]
    z = at[2]
    r = JET_RADIUS
    p.hull.lathe(
        [[r - 0.6, DECK], [r, DECK + 1.2], [r, DECK + 4.6], [r - 1, DECK + 5.6]],
        14,
        M.panel,
        Placement([x, 0, z]),
        False,
    )
    p.hull.lathe(
        [[r - 1, DECK + 5.6], [r - 2.2, DECK + 5.6], [r - 2.4, DECK + 4.2]],
        14,
        M.base,
        Placement([x, 0, z]),
        False,
    )
    p.bare.cylinder(r - 2.3, 0.2, 14, M.dark, Placement([x, DECK + 4, z]))
    p.hull.cylinder(1.8, 1.4, 8, M.base, Placement([x, DECK + 4, z]))
    for k in range(4):
        p.hull.box(
            [1.2, 0.3, 2 * r - 4.6],
            M.panel,
            Placement([x, DECK + 4.1, z], k * math.pi / 4),
        )
    p.neon.ring(r - 1.6, 0.3, 14, N, Placement([x, DECK + 5.45, z]))
    p.neon.ring(r + 0.05, 0.4, 14, N, Placement([x, DECK + 2.2, z]))
    out = math.atan2(-x, -z)
    for side in [-1, 1]:
        a = out + side * math.pi / 2
        q = [x + math.sin(a) * (r - 0.4), DECK, z + math.cos(a) * (r - 0.4)]
        p.hull.box([3, 4, 5], M.base, Placement(q, a), M.panel)
    # Its exhaust: a glowing nozzle under the rim's edge.
    nozzle = [x * 1.06, -0.6, z * 1.06]
    p.neon.cylinder(r * 0.55, 1.2, 10, N, Placement(nozzle))


def _half(side: float) -> Any:
    """Return the drawing of the cupola's half on `side` (+1 the config's right), as drawn.

    A half drum of thick steel-faced concrete, vision slits round its curve, a flat armoured top
    with a lit edge, the hinge lugs along its cut face.
    """

    def draw(p: Any) -> None:
        r = CUPOLA_RADIUS
        n = 8
        outline: list[list[float]] = []
        top: list[list[float]] = []
        for k in range(n + 1):
            a = -math.pi / 2 + math.pi * k / n
            outline.append(pt(side * r * math.cos(a), r * math.sin(a)))
            top.append(pt(side * (r - 1.2) * math.cos(a), (r - 1.2) * math.sin(a)))
        p.flesh.slab(outline, [CROWN[1], CUPOLA_TOP - 1.2], CONCRETE, None, COURSE)
        p.hull.slab(top, [CUPOLA_TOP - 1.2, CUPOLA_TOP], M.panel, None, M.base)
        for k in range(1, n):
            a = -math.pi / 2 + math.pi * k / n
            q = boss_point(side * (r + 0.02) * math.cos(a), (r + 0.02) * math.sin(a), CROWN[1] + 2)
            if k % 2 == 1:
                p.neon.box(
                    [0.4, 0.6, 2.4], N, Placement(q, math.atan2(-side * math.cos(a), -math.sin(a)))
                )
        for y in [-7, 0, 7]:
            q = boss_point(side * 0.6, y, CUPOLA_TOP - 2.5)
            p.hull.box([1.2, 2.4, 2.4], M.base, Placement(q))
        p.neon.box([0.35, 0.3, 2 * r - 2], N, Placement(boss_point(side * 0.9, 0, CUPOLA_TOP)))

    return draw


def _hatch(p: Any) -> None:
    """Draw the hatch over the crown's rotor (BOSS-58): a riveted steel lid, a lit seam round it."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], CROWN[1])
    p.hull.lathe(
        [
            [HATCH_RADIUS, CROWN[1]],
            [HATCH_RADIUS, CROWN[1] + 1],
            [HATCH_RADIUS - 1.6, CROWN[1] + 2],
        ],
        8,
        M.panel,
        Placement([at[0], 0, at[2]], math.pi / 8),
    )
    p.neon.ring(
        HATCH_RADIUS + 0.05, 0.3, 8, N, Placement([at[0], CROWN[1] + 0.4, at[2]], math.pi / 8)
    )
    p.hull.box([HATCH_RADIUS * 1.4, 0.6, 1.2], M.base, Placement([at[0], CROWN[1] + 2, at[2]]))


def _hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a steel collar round the well the rotor rises from."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], CROWN[1])
    p.hull.ring(HATCH_RADIUS, 0.9, 12, M.base, Placement([at[0], CROWN[1], at[2]]))
    p.neon.ring(HATCH_RADIUS, 0.3, 12, N, Placement([at[0], CROWN[1] + 0.9, at[2]]))
    p.bare.cylinder(HATCH_RADIUS - 0.3, 0.2, 12, M.dark, Placement([at[0], CROWN[1], at[2]]))


def build_bunker_saucer(scene: Any) -> Any:
    """MB-BUNKER-SAUCER-01, MB-BUNKER-SAUCER-02: the Bunker Saucer.

    A concrete saucer 3.6 L across, red light lines (shown yellow) round its rim and steps.
    """

    def core(p: Any) -> None:
        _draw_saucer(p)
        _draw_parapet(p)
        _draw_steps(p)
        _draw_crown(p)
        _draw_pillbox_drum(p)
        _draw_jet_sockets(p)

    return build_boss_model(
        BUNKER_SAUCER,
        scene,
        N,
        {
            "core": core,
            "parts": {"jet-left": lift_jet, "jet-right": lift_jet, "pillbox": pillbox},
            "armour": {
                "cupola-right": {"whole": _half(1)},
                "cupola-left": {"whole": _half(-1)},
                "rotor-hatch": {"whole": _hatch, "frame": _hatch_frame},
            },
            "rig": {"build": build_saucer_rig, "triangles": rig_triangles},
        },
    )
