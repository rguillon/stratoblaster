# Copyright (c) 2026 Renaud Guillon
"""MB-CONDOR-LIFTER-01 to MB-CONDOR-LIFTER-05: the Condor Lifter, the Lab's L-16 mini boss.

Logical pixels, nose +Z, Y up (towards the camera). A gigantic heavy-lift cargo plane: a fat
fuselage with a glazed cockpit and gear sponsons, a high straight wing with four turboprops on it
(their propellers are its rig, `condor_lifter_rig`), a T-tail over the flat rear closed by the
cargo ramp (rig), and an external cargo deck on its back with two strapped containers (an armour
region: they morph into gun decks). A machine, not a creature: the Lab's fourth round builds
gigantic airplanes (user request, 2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.condor_lifter import (
    CONDOR_LIFTER,
    CONTAINER_TOP,
    CONTAINER_X,
    CONTAINER_Y,
    DECK_HALF,
    DECK_TOP,
    DECK_Y,
    DORSAL_AT,
    DORSAL_H,
    ENGINE_GUN_H,
    FIN_ROOT,
    FIN_TIP,
    FIN_TOP,
    FUSELAGE,
    NACELLE_H,
    NACELLE_R,
    NACELLE_X,
    NACELLE_Y,
    NOSE_GUN_AT,
    NOSE_GUN_H,
    RAMP_H,
    RAMP_Y,
    ROTOR_AT,
    ROTOR_H,
    TAIL_ROOT,
    TAIL_SPAN,
    TAIL_TIP,
    WING_LOW,
    WING_ROOT,
    WING_SPAN,
    WING_TIP,
    WING_TOP,
    fuselage_at,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.condor_lifter_rig import (
    build_condor_rig,
    draw_container_walls,
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


N = BOSS_LOOK.neon["condor-lifter"]
QUARTER = math.pi / 2
SIDES = 14


def _section() -> list[list[float]]:
    """Return the fuselage's section: a fat rounded box, `[u, v]` across and up."""
    result: list[list[float]] = []
    for k in range(SIDES):
        a = 2 * math.pi * k / SIDES
        c = math.cos(a)
        s = math.sin(a)
        u = (1 if c >= 0 else -1) * math.pow(abs(c), 0.6)
        v = (1 + (1 if s >= 0 else -1) * math.pow(abs(s), 0.6)) / 2
        result.append([u, v])
    return result


SECTION = _section()


def _model(x: float, y: float) -> list[float]:
    """Return the playfield outline point `(x, y)` as a model outline point `[x, z]`."""
    return [-x, -y]


def _panel(side: int, _band: int) -> Any:
    """Return the shade of the fuselage's facet `side` between stations `band` (or None)."""
    return M.base if side in [0, SIDES - 1, SIDES // 2 - 1, SIDES // 2] else None


def _fuselage(p: Any) -> None:
    """Draw the fuselage (MB-CONDOR-LIFTER-01): a fat loft, a glazed cockpit, gear sponsons.

    Its flat rear is the cargo bay's mouth (lit inside, behind the ramp), its sides lined with
    small lit windows, a lit stripe along each flank.
    """
    stations = [[-s[0], s[1], s[2], s[3]] for s in reversed(FUSELAGE)]
    p.hull.loft(SECTION, stations, M.panel, None, LoftOptions(False, _panel))
    # The cockpit: a glazed brow over the nose, its windows lit.
    for k in range(4):
        x = (k - 1.5) * 2.6
        y = -53.5 + abs(k - 1.5) * 0.6
        top = fuselage_at(y)[2]
        p.neon.box([2.1, 0.5, 1.6], N, Placement(boss_point(x, y, top - 0.6), 0, -0.35))
    p.bare.box([11, 0.6, 1], M.dark, Placement(boss_point(0, -51.2, fuselage_at(-51.2)[2] - 0.2)))
    for side in [-1, 1]:
        for y in [-40, -32, -24, 12, 20, 28]:
            hw = fuselage_at(y)[0]
            p.neon.box([0.3, 0.9, 1.4], N, Placement(boss_point(side * (hw + 0.05), y, 14)))
        p.neon.box([0.3, 0.4, 30], N, Placement(boss_point(side * 11.05, -2, 9)))
        # The gear sponsons along the lower flanks.
        sponson = [
            _model(side * 10, -14),
            _model(side * 14, -10),
            _model(side * 14, 18),
            _model(side * 10, 22),
        ]
        p.hull.bevel_slab(sponson, [1.5, 6, 8.5], [0.6, 1.4], M.base, None, M.panel)
        p.neon.box([0.4, 0.4, 20], N, Placement(boss_point(side * 13.3, 4, 8.5)))
    # The cargo bay's mouth: lit inside, behind the ramp.
    p.neon.box([13, 9, 0.2], N, Placement(boss_point(0, RAMP_Y + 0.1, RAMP_H + 1.5)))
    p.bare.box([15, 0.6, 1.2], M.dark, Placement(boss_point(0, RAMP_Y - 0.3, RAMP_H - 0.3)))
    # The rotor's well behind the cockpit, the dorsal turret's seat on the wing.
    well = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.bare.cylinder(5.4, 0.8, 8, M.dark, Placement([well[0], ROTOR_H - 0.9, well[2]]))
    seat = boss_point(DORSAL_AT[0], DORSAL_AT[1], 0)
    p.hull.cylinder(5.8, 1.2, 10, M.base, Placement([seat[0], WING_TOP - 0.2, seat[2]]))
    p.neon.ring(5.9, 0.4, 10, N, Placement([seat[0], DORSAL_H - 0.9, seat[2]]))


def _wing(p: Any) -> None:
    """Draw the high straight wing (MB-CONDOR-LIFTER-02): lit leading edges, flaps, tip lights."""
    outline = [
        _model(0, WING_ROOT[0]),
        _model(WING_SPAN, WING_TIP[0]),
        _model(WING_SPAN, WING_TIP[1]),
        _model(0, WING_ROOT[1]),
        _model(-WING_SPAN, WING_TIP[1]),
        _model(-WING_SPAN, WING_TIP[0]),
    ]
    p.hull.bevel_slab(
        outline, [WING_LOW, WING_LOW + 1.6, WING_TOP], [0, 0.7], M.base, None, M.panel
    )
    for side in [-1, 1]:
        # The leading edge, lit between the nacelles and out to the tip.
        for x0, x1 in [[13, 18], [26, 38], [46, 60]]:
            mid = (x0 + x1) / 2
            y = WING_ROOT[0] + (WING_TIP[0] - WING_ROOT[0]) * mid / WING_SPAN + 0.6
            p.neon.box([x1 - x0, 0.4, 0.6], N, Placement(boss_point(side * mid, y, WING_TOP - 0.3)))
        # The flaps and ailerons along the trailing edge: dark strips, their seams.
        for x0, x1 in [[13, 36], [38, 58]]:
            mid = (x0 + x1) / 2
            y = WING_ROOT[1] + (WING_TIP[1] - WING_ROOT[1]) * mid / WING_SPAN - 2.4
            p.bare.box([x1 - x0, 0.3, 3.6], M.dark, Placement(boss_point(side * mid, y, WING_TOP)))
        p.neon.box([1.2, 0.5, 3], N, Placement(boss_point(side * (WING_SPAN - 0.8), -6, WING_TOP)))
        # Its spar's rivet line.
        for k in range(8):
            x = 14 + k * 6
            p.bare.box([0.8, 0.3, 0.8], M.dark, Placement(boss_point(side * x, -5, WING_TOP)))


def _nacelle(p: Any, x: float) -> None:
    """Draw a turboprop over the wing at `x`: a long cowling, its spinner, exhaust stacks."""
    length = NACELLE_Y[1] - NACELLE_Y[0]
    r = NACELLE_R
    profile = [
        [1.2, 0],
        [r * 0.7, 2],
        [r, 9],
        [r, length - 6],
        [r * 0.9, length - 1.5],
        [r * 0.75, length],
    ]
    p.hull.lathe(
        profile, 10, M.panel, Placement(boss_point(x, NACELLE_Y[1], NACELLE_H), 0, QUARTER)
    )
    p.hull.cylinder(
        2.6, 2.6, 8, M.base, Placement(boss_point(x, NACELLE_Y[0], NACELLE_H), 0, QUARTER), 0.4
    )
    p.neon.ring(
        r * 0.78, 0.6, 10, N, Placement(boss_point(x, NACELLE_Y[0] + 0.8, NACELLE_H), 0, QUARTER)
    )
    for side in [-1, 1]:
        p.bare.box(
            [1, 1.2, 3.5],
            M.dark,
            Placement(boss_point(x + side * (r - 0.3), NACELLE_Y[0] + 12, NACELLE_H + 1)),
        )
    p.neon.box([0.6, 0.4, 8], N, Placement(boss_point(x, NACELLE_Y[1] - 9, NACELLE_H + r - 0.2)))


def _cargo_deck(p: Any) -> None:
    """Draw the external cargo deck on its back (MB-CONDOR-LIFTER-02): a pallet over the fuselage.

    Lit along its edges, struts down to the fuselage's flanks, tie-down rails across it.
    """
    outline = [
        _model(DECK_HALF, DECK_Y[0]),
        _model(DECK_HALF, DECK_Y[1]),
        _model(-DECK_HALF, DECK_Y[1]),
        _model(-DECK_HALF, DECK_Y[0]),
    ]
    p.hull.bevel_slab(
        outline, [DECK_TOP - 1.2, DECK_TOP - 0.4, DECK_TOP], [0, 0.3], M.base, None, M.panel
    )
    mid = (DECK_Y[0] + DECK_Y[1]) / 2
    long = DECK_Y[1] - DECK_Y[0]
    for side in [-1, 1]:
        p.neon.box(
            [0.5, 0.4, long - 1], N, Placement(boss_point(side * (DECK_HALF - 0.4), mid, DECK_TOP))
        )
        for y in [DECK_Y[0] + 3, DECK_Y[1] - 3]:
            start = boss_point(side * 10.5, y, 10)
            end = boss_point(side * (DECK_HALF - 1.5), y, DECK_TOP - 1)
            _rod(p.hull, start, end, 0.7, M.base)
    for rail in [DECK_Y[0] + 0.8, DECK_Y[1] - 0.8]:
        p.bare.box([DECK_HALF * 2 - 2, 0.3, 0.6], M.dark, Placement(boss_point(0, rail, DECK_TOP)))


def _rod(builder: Any, start: Vec3, end: Vec3, radius: float, color: Any) -> None:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz) or 1
    builder.cylinder(
        radius, length, 4, color, Placement(start, math.atan2(dx, dz), math.acos(dy / length))
    )


def _tail(p: Any) -> None:
    """Draw the T-tail (MB-CONDOR-LIFTER-02): a swept fin on the centre line, the tailplane on top.

    A lit stripe up the fin's rudder, lit tips on the tailplane.
    """
    base = fuselage_at(FIN_ROOT[0])[2] - 1
    fin = [
        [base, -FIN_ROOT[0]],
        [base, -FIN_ROOT[1]],
        [FIN_TOP, -FIN_TIP[1]],
        [FIN_TOP, -FIN_TIP[0]],
    ]
    p.hull.slab(fin, [-0.8, 0.8], M.base, Placement([0, 0, 0], 0, 0, QUARTER), M.panel)
    p.neon.box([1.8, FIN_TOP - base - 4, 0.5], N, Placement([0, base + 2, -FIN_ROOT[1] + 1.5]))
    plane = [
        _model(0, TAIL_ROOT[0]),
        _model(TAIL_SPAN, TAIL_TIP[0]),
        _model(TAIL_SPAN, TAIL_TIP[1]),
        _model(-TAIL_SPAN, TAIL_TIP[1]),
        _model(-TAIL_SPAN, TAIL_TIP[0]),
    ]
    p.hull.bevel_slab(
        plane, [FIN_TOP - 0.8, FIN_TOP, FIN_TOP + 0.8], [0, 0.4], M.base, None, M.panel
    )
    for side in [-1, 1]:
        p.neon.box(
            [1.2, 0.4, 4.2], N, Placement(boss_point(side * (TAIL_SPAN - 0.6), 49.5, FIN_TOP + 0.6))
        )
        p.bare.box(
            [TAIL_SPAN - 4, 0.3, 1.6],
            M.dark,
            Placement(boss_point(side * TAIL_SPAN / 2, 50.6, FIN_TOP + 0.8)),
        )


def _container_whole(p: Any) -> None:
    """Draw the two containers strapped on the deck (MB-CONDOR-LIFTER-10): walls, roofs, straps."""
    draw_container_walls(p)
    for side in [-1, 1]:
        _roof(p, side, CONTAINER_Y[0], CONTAINER_Y[1])
        mid_x = side * (CONTAINER_X[0] + CONTAINER_X[1]) / 2
        wide = CONTAINER_X[1] - CONTAINER_X[0]
        for y in [12, 24]:
            p.neon.box([wide + 1.4, 0.35, 1], N, Placement(boss_point(mid_x, y, CONTAINER_TOP)))
            p.bare.box(
                [0.4, CONTAINER_TOP - DECK_TOP, 1],
                M.dark,
                Placement(boss_point(side * (CONTAINER_X[1] + 0.55), y, DECK_TOP)),
            )


def _roof(p: Any, side: float, y0: float, y1: float) -> None:
    """Draw a container's roof between `y0` and `y1`: a plate with ribs across it."""
    mid_x = side * (CONTAINER_X[0] + CONTAINER_X[1]) / 2
    wide = CONTAINER_X[1] - CONTAINER_X[0]
    p.hull.box(
        [wide + 0.4, 0.8, y1 - y0 + 0.4],
        M.base,
        Placement(boss_point(mid_x, (y0 + y1) / 2, CONTAINER_TOP - 0.8)),
        M.panel,
    )
    y = y0 + 2
    while y < y1 - 1:
        p.bare.box([wide - 1, 0.25, 0.6], M.dark, Placement(boss_point(mid_x, y, CONTAINER_TOP)))
        y += 3


def _roof_piece(side: float, half: int) -> Any:
    """One half of a container's roof, flying off (its armour piece)."""
    mid = (CONTAINER_Y[0] + CONTAINER_Y[1]) / 2

    def draw(p: Any) -> None:
        if half == 0:
            _roof(p, side, CONTAINER_Y[0], mid)
        else:
            _roof(p, side, mid, CONTAINER_Y[1])

    return draw


def _container_frame(p: Any) -> None:
    """Draw what the containers leave (BOSS-44): their dark floors on the deck, lit rims."""
    for side in [-1, 1]:
        mid_x = side * (CONTAINER_X[0] + CONTAINER_X[1]) / 2
        mid_y = (CONTAINER_Y[0] + CONTAINER_Y[1]) / 2
        wide = CONTAINER_X[1] - CONTAINER_X[0]
        long = CONTAINER_Y[1] - CONTAINER_Y[0]
        p.bare.box(
            [wide - 0.6, 0.3, long - 0.6], M.dark, Placement(boss_point(mid_x, mid_y, DECK_TOP))
        )
        for y in [CONTAINER_Y[0] + 3, CONTAINER_Y[1] - 3]:
            p.neon.box([wide - 2, 0.2, 0.4], N, Placement(boss_point(mid_x, y, DECK_TOP + 0.3)))


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over the cargo rotor (BOSS-58): an octagonal cap, a lit seam round it."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.bevel_slab(
        polygon(8, 5.8), [ROTOR_H - 0.8, ROTOR_H, ROTOR_H + 1.2], [0, 0.8], M.panel, Placement(at)
    )
    p.neon.ring(5.4, 0.25, 8, N, Placement([at[0], ROTOR_H + 0.4, at[2]], math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.ring(5.6, 1.2, 12, M.base, Placement([at[0], ROTOR_H - 0.9, at[2]]))
    p.neon.ring(5.6, 0.3, 12, N, Placement([at[0], ROTOR_H + 0.1, at[2]]))


def _engine_gun(p: Any, at: Vec3) -> None:
    """Add an engine gun's cowl (MB-CONDOR-LIFTER-03): an armoured collar on its nacelle's back."""
    x = at[0]
    z = at[2]
    p.hull.bevel_slab(
        polygon(8, 4.6),
        [NACELLE_H + 1.5, ENGINE_GUN_H - 0.8, ENGINE_GUN_H],
        [0, 0.5],
        M.base,
        Placement([x, 0, z - 1], math.pi / 8),
        M.panel,
    )
    p.neon.ring(4.65, 0.4, 8, N, Placement([x, ENGINE_GUN_H - 1.2, z - 1], math.pi / 8))


def _nose_gun(p: Any, _at: Vec3) -> None:
    """Add the nose gun's barbette (MB-CONDOR-LIFTER-03): an armoured drum ahead of the cockpit."""
    gun = boss_point(NOSE_GUN_AT[0], NOSE_GUN_AT[1], 0)
    p.hull.cylinder(5.2, 2.4, 10, M.panel, Placement([gun[0], NOSE_GUN_H - 2.2, gun[2]]), 4.6)
    p.neon.ring(5.0, 0.4, 10, N, Placement([gun[0], NOSE_GUN_H - 0.9, gun[2]]))


def build_condor_lifter(scene: Any) -> Any:
    """MB-CONDOR-LIFTER-01, MB-CONDOR-LIFTER-04: the Condor Lifter.

    A fat cargo plane, a high straight wing with four turboprops, a T-tail, two containers on a
    cargo deck on its back; teal lights; about 3.7 L across.
    """

    def core(p: Any) -> None:
        _fuselage(p)
        _wing(p)
        for x in NACELLE_X:
            _nacelle(p, x)
            _nacelle(p, -x)
        _cargo_deck(p)
        _tail(p)

    return build_boss_model(
        CONDOR_LIFTER,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "engine-left": _engine_gun,
                "engine-right": _engine_gun,
                "nose-gun": _nose_gun,
            },
            # MB-CONDOR-LIFTER-05: its propellers, its ramp, the containers' walls and cargo.
            "rig": {"build": build_condor_rig, "triangles": rig_triangles},
            "armour": {
                "containers": {
                    "whole": _container_whole,
                    "pieces": [_roof_piece(s, h) for s in [-1, 1] for h in [0, 1]],
                    "frame": _container_frame,
                },
                "rotor-hatch": {"whole": _draw_hatch, "frame": _draw_hatch_frame},
            },
        },
    )
