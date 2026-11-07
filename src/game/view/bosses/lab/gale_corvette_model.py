# Copyright (c) 2026 Renaud Guillon
"""MB-GALE-CORVETTE-01 to MB-GALE-CORVETTE-05: the Gale Corvette, the Lab's L-11 mini boss.

Logical pixels, nose +Z, Y up (towards the camera). A small armed airship: a riveted cigar gas
envelope ringed with light bands, a long gondola under it whose nose juts out ahead with the bow
gun, an engine nacelle on a stub wing each side (their propellers are its rig,
`gale_corvette_rig`), and a cruciform tail: two horizontal stern fins under armoured fairings, a
tall upper fin. A machine, not a creature: the Lab's third round builds flying fortresses (user
request, 2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.gale_corvette import (
    BOW_GUN_AT,
    DORSAL_AT,
    DORSAL_H,
    ENGINE_GUN_H,
    ENV_H,
    ENVELOPE,
    FAIRING,
    FAIRING_TOP,
    FIN_ROOT,
    FIN_SPAN,
    FIN_TIP,
    FIN_TOP,
    GALE_CORVETTE,
    GONDOLA,
    GONDOLA_HALF,
    GONDOLA_LOW,
    GONDOLA_TOP,
    NACELLE_AT,
    NACELLE_H,
    NACELLE_HALF,
    NACELLE_RADIUS,
    ROTOR_AT,
    ROTOR_H,
    envelope_radius,
    envelope_top,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.gale_corvette_rig import build_prop_rig, prop_triangles
from game.view.bosses.world_1_organic_kit import M, polygon
from render.geometry.solids import LoftOptions, Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["gale-corvette"]
QUARTER = math.pi / 2
# The light bands round the envelope (Y), and the rivet rows along its back: their X off the
# centre line and the Ys they run between.
BANDS = [-31, -6, 22]
RIVET_X = 6.5
RIVETS = [-34, 30]
# The stub wings out to the nacelles: `[y0, y1]` and their thickness.
STUB = [-5, 7]
STUB_THICK = 1.2


# The envelope's section: a 14-sided circle (counter-clockwise seen from the nose), `[u, v]`
# across its width and up its height.
GORE_SIDES = 14
GORE_SECTION = [
    [math.cos(2 * math.pi * k / GORE_SIDES), (1 + math.sin(2 * math.pi * k / GORE_SIDES)) / 2]
    for k in range(GORE_SIDES)
]


def _gore(side: int, _band: int) -> Any:
    """Return the shade of the envelope's facet `side` (every other gore darker), or None."""
    return M.base if side % 2 == 1 else None


def _model(x: float, y: float) -> list[Any]:
    """Return the playfield outline point `(x, y)` as a model outline point `[x, z]`."""
    return [-x, -y]


def _envelope(p: Any) -> None:
    """Draw the gas envelope (MB-GALE-CORVETTE-01): a riveted metal cigar along Z, lit bands.

    A loft along +Z from its tail, its gores in two shades; rivet rows down its back, a lit band
    round it at each of `BANDS`, a dark nose cap with a mooring ring.
    """
    stations = [[-s[0], s[1], ENV_H - s[1], ENV_H + s[1]] for s in reversed(ENVELOPE)]
    p.hull.loft(GORE_SECTION, stations, M.panel, None, LoftOptions(False, _gore))
    for y in BANDS:
        r = envelope_radius(y)
        p.neon.ring(r + 0.25, 0.9, GORE_SIDES, N, Placement(boss_point(0, y, ENV_H), 0, QUARTER))
        p.bare.ring(
            r + 0.15, 2.4, GORE_SIDES, M.base, Placement(boss_point(0, y + 0.75, ENV_H), 0, QUARTER)
        )
    for side in [-1, 1]:
        y = RIVETS[0]
        while y <= RIVETS[1]:
            r = envelope_radius(y)
            if r > RIVET_X + 1:
                h = ENV_H + math.sqrt(r * r - RIVET_X * RIVET_X)
                p.bare.box(
                    [0.9, 0.5, 1.2], M.dark, Placement(boss_point(side * RIVET_X, y, h - 0.2))
                )
            y += 4
    nose = boss_point(0, -41.5, ENV_H)
    p.hull.cylinder(4.6, 2.5, 10, M.base, Placement(nose, 0, QUARTER), 1.5)
    p.neon.ring(1.7, 0.5, 8, N, Placement([nose[0], nose[1], nose[2] + 2.5], 0, QUARTER))
    # A catwalk down its back, between the dorsal turret's seat and the hatch.
    for y in [-24, -8, 6]:
        h = envelope_top(y)
        p.bare.box([3.4, 0.6, 7], M.base, Placement(boss_point(0, y + 3.5, h - 0.4)))
    seat = boss_point(DORSAL_AT[0], DORSAL_AT[1], 0)
    p.hull.cylinder(5.6, 1.6, 10, M.base, Placement([seat[0], DORSAL_H - 1.4, seat[2]]))
    p.neon.ring(5.7, 0.4, 10, N, Placement([seat[0], DORSAL_H - 0.6, seat[2]]))
    well = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.bare.cylinder(5.4, 0.6, 8, M.dark, Placement([well[0], ROTOR_H - 0.7, well[2]]))


def _gondola_outline() -> list[list[float]]:
    """Return the gondola's outline from above (model XZ): a long boat, its nose ahead."""
    w = GONDOLA_HALF
    front = GONDOLA[0]
    back = GONDOLA[1]
    right: list[list[float]] = [
        [0, front],
        [w * 0.55, front + 2],
        [w, front + 7],
        [w, back - 6],
        [w * 0.6, back],
    ]
    left = [[-q[0], q[1]] for q in reversed(right)]
    points = [_model(q[0], q[1]) for q in right]
    points.extend([_model(q[0], q[1]) for q in left if q[0] != 0])
    return points


def _gondola(p: Any) -> None:
    """Draw the gondola (MB-GALE-CORVETTE-02): a long armoured boat hung under the envelope.

    Lit bridge windows down its sides, deck plating, its hangers up into the envelope, and the bow
    gun's barbette on its nose (the bow gun's part sits on it).
    """
    p.hull.bevel_slab(
        _gondola_outline(),
        [GONDOLA_LOW, GONDOLA_TOP - 2.5, GONDOLA_TOP],
        [2.4, 0.7],
        M.base,
        None,
        M.panel,
    )
    for side in [-1, 1]:
        x = side * (GONDOLA_HALF + 0.05)
        for y0 in [-49, -39, -29, -19, -9]:
            p.neon.box([0.4, 1.3, 6], N, Placement(boss_point(x, y0 + 3, GONDOLA_TOP - 4.2)))
    for y in [-40, -26, -10, 6]:
        bottom = ENV_H - envelope_radius(y)
        if bottom > GONDOLA_TOP - 0.5:
            p.hull.box(
                [GONDOLA_HALF * 1.2, bottom - GONDOLA_TOP + 1.5, 2.2],
                M.panel,
                Placement(boss_point(0, y, GONDOLA_TOP - 0.5)),
            )
    for y in [-44, -36]:
        p.bare.box([GONDOLA_HALF * 1.4, 0.4, 3], M.dark, Placement(boss_point(0, y, GONDOLA_TOP)))
    gun = boss_point(BOW_GUN_AT[0], BOW_GUN_AT[1], 0)
    p.hull.cylinder(5.2, 1.0, 10, M.panel, Placement([gun[0], GONDOLA_TOP - 0.5, gun[2]]))


def _nacelle(p: Any, side: float) -> None:
    """Draw an engine nacelle on its stub wing (MB-GALE-CORVETTE-02), on `side` (+1: right).

    A cigar laid along Z, a lit intake ring at its nose, exhaust vents; the stub wing from the
    envelope's flank, with struts under it to the gondola.
    """
    x = side * NACELLE_AT[0]
    tail = NACELLE_AT[1] + NACELLE_HALF
    length = NACELLE_HALF * 2
    r = NACELLE_RADIUS
    profile = [
        [1.5, 0],
        [r * 0.8, 1.5],
        [r, 5],
        [r, length - 5],
        [r * 0.75, length - 1.5],
        [0, length],
    ]
    p.hull.lathe(profile, 10, M.panel, Placement(boss_point(x, tail, NACELLE_H), 0, QUARTER))
    p.neon.ring(
        r * 0.78, 0.6, 10, N, Placement(boss_point(x, tail - length + 1.6, NACELLE_H), 0, QUARTER)
    )
    p.neon.ring(r + 0.1, 0.5, 10, N, Placement(boss_point(x, tail - 4, NACELLE_H), 0, QUARTER))
    for k in range(3):
        p.bare.box(
            [1.2, 0.5, 2],
            M.dark,
            Placement(boss_point(x - side * 1.6, tail - 7 - 3 * k, NACELLE_H + r - 0.3)),
        )
    inner = 9
    outer = NACELLE_AT[0] - r + 0.8
    stub = [
        _model(side * inner, STUB[0]),
        _model(side * outer, STUB[0] + 1),
        _model(side * outer, STUB[1]),
        _model(side * inner, STUB[1] + 2),
    ]
    p.hull.bevel_slab(
        stub,
        [NACELLE_H + 0.8, NACELLE_H + 1.4, NACELLE_H + 0.8 + STUB_THICK + 0.6],
        [0, 0.4],
        M.base,
        None,
        M.panel,
    )
    p.neon.box(
        [outer - inner - 4, 0.3, 0.5],
        N,
        Placement(boss_point(side * (inner + outer) / 2, STUB[0] + 0.8, NACELLE_H + 2.6), 0),
    )
    for y in [STUB[0] + 2, STUB[1] - 1]:
        start = boss_point(side * GONDOLA_HALF, y, GONDOLA_TOP - 3)
        end = boss_point(side * (outer - 1), y, NACELLE_H - 1)
        _rod(p.hull, start, end, 0.7, M.base)


def _rod(builder: Any, start: Vec3, end: Vec3, radius: float, color: Any) -> None:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz) or 1
    builder.cylinder(
        radius, length, 4, color, Placement(start, math.atan2(dx, dz), math.acos(dy / length))
    )


def _fins(p: Any) -> None:
    """Draw the cruciform tail (MB-GALE-CORVETTE-02): the two stern fins and the upper fin.

    The stern fins are flat plates from inside the envelope out, lit along their trailing edge
    (their fairings are armour, `_fairings`); the upper fin stands on the envelope's back, a lit
    stripe up its rudder.
    """
    for side in [-1, 1]:
        fin = [
            _model(side * 3, FIN_ROOT[0]),
            _model(side * FIN_SPAN, FIN_TIP[0]),
            _model(side * FIN_SPAN, FIN_TIP[1]),
            _model(side * 3, FIN_ROOT[1]),
        ]
        p.hull.bevel_slab(
            fin, [FIN_TOP - 1.2, FIN_TOP - 0.6, FIN_TOP], [0, 0.4], M.base, None, M.panel
        )
        p.neon.box(
            [1.4, 0.4, FIN_TIP[1] - FIN_TIP[0] - 1],
            N,
            Placement(
                boss_point(side * (FIN_SPAN - 0.6), (FIN_TIP[0] + FIN_TIP[1]) / 2, FIN_TOP - 0.2)
            ),
        )
    # The upper fin: a plate standing along Z on the centre line (drawn in local X = height,
    # rolled up a quarter turn).
    upper = [[16, -48], [41, -47], [42, -43], [32, -29], [26, -27], [16, -27]]
    p.hull.slab(upper, [-0.7, 0.7], M.base, Placement([0, 0, 0], 0, 0, QUARTER), M.panel)
    p.neon.box([1.6, 12, 0.5], N, Placement([0, 24, -47.9]))
    p.neon.box([1.7, 0.4, 4.4], N, Placement([0, 41.2, -45]))


def _fairing_outlines() -> list[list[list[float]]]:
    """Return the two fairings' outlines (model XZ)."""
    right = [_model(q[0], q[1]) for q in FAIRING]
    left = [_model(-q[0], q[1]) for q in reversed(FAIRING)]
    return [right, left]


def _fairings(p: Any) -> None:
    """Draw the armoured fairings over the stern fins (MB-GALE-CORVETTE-10), shed as it turns.

    Each a heavy streamlined plate over its fin, a lit seam along it, rivets round its edge.
    """
    for outline in _fairing_outlines():
        p.hull.bevel_slab(
            outline,
            [FIN_TOP - 0.2, FAIRING_TOP - 1.6, FAIRING_TOP],
            [0, 1.6],
            M.panel,
            None,
            M.base,
        )
    for side in [-1, 1]:
        p.neon.box([0.5, 0.4, 14], N, Placement(boss_point(side * 16, 39.5, FAIRING_TOP)))
        for y in [33, 37, 41, 45]:
            p.bare.box(
                [0.9, 0.4, 0.9], M.dark, Placement(boss_point(side * 22.5, y, FAIRING_TOP - 0.9))
            )
            p.bare.box(
                [0.9, 0.4, 0.9], M.dark, Placement(boss_point(side * 9.5, y, FAIRING_TOP - 0.9))
            )


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over the stern rotor (BOSS-58): an octagonal cap, a lit seam round it."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.bevel_slab(
        polygon(8, 5.8), [ROTOR_H - 0.6, ROTOR_H, ROTOR_H + 1.4], [0, 0.8], M.panel, Placement(at)
    )
    p.neon.ring(5.4, 0.25, 8, N, Placement([at[0], ROTOR_H + 0.5, at[2]], math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.ring(5.6, 1.2, 12, M.base, Placement([at[0], ROTOR_H - 0.8, at[2]]))
    p.neon.ring(5.6, 0.3, 12, N, Placement([at[0], ROTOR_H + 0.2, at[2]]))


def _engine_gun(p: Any, at: Vec3) -> None:
    """Add an engine gun's cowl (MB-GALE-CORVETTE-03): an armoured ring on its nacelle's back.

    Lit round its rim, two cheek plates down the nacelle's sides.
    """
    x = at[0]
    z = at[2]
    p.hull.bevel_slab(
        polygon(8, 5.2),
        [ENGINE_GUN_H - 2.4, ENGINE_GUN_H - 0.8, ENGINE_GUN_H],
        [0, 0.5],
        M.panel,
        Placement([x, 0, z], math.pi / 8),
        M.base,
    )
    p.neon.ring(5.25, 0.4, 8, N, Placement([x, ENGINE_GUN_H - 1.4, z], math.pi / 8))
    for dx in [-1, 1]:
        p.hull.box(
            [1.2, 3.6, 6.5],
            M.base,
            Placement([x + dx * (NACELLE_RADIUS + 0.2), NACELLE_H - 0.5, z]),
        )


def _bow_gun(p: Any, at: Vec3) -> None:
    """Add the bow gun's barbette (MB-GALE-CORVETTE-03): an armoured drum on the gondola's nose.

    A lit chevron on the nose deck ahead of it, and a rangefinder bar behind.
    """
    gun = boss_point(BOW_GUN_AT[0], BOW_GUN_AT[1], 0)
    p.hull.cylinder(5.4, 1.6, 10, M.panel, Placement([gun[0], GONDOLA_TOP - 1.1, gun[2]]), 5)
    p.neon.ring(5.45, 0.4, 10, N, Placement([gun[0], GONDOLA_TOP - 0.6, gun[2]]))
    p.neon.box([4, 0.3, 0.6], N, Placement([0, GONDOLA_TOP, at[2] + 8]))
    p.hull.box([8, 1.2, 1.4], M.base, Placement([0, GONDOLA_TOP, at[2] - 5]))
    p.neon.box([1, 0.5, 0.6], N, Placement([3.6, GONDOLA_TOP + 1.2, at[2] - 5]))
    p.neon.box([1, 0.5, 0.6], N, Placement([-3.6, GONDOLA_TOP + 1.2, at[2] - 5]))


def build_gale_corvette(scene: Any) -> Any:
    """MB-GALE-CORVETTE-01, MB-GALE-CORVETTE-04: the Gale Corvette.

    A riveted cigar envelope over a long gondola, an engine nacelle on a stub wing each side, a
    cruciform tail; sky-blue light bands (shown green); about 3 L long.
    """

    def core(p: Any) -> None:
        _envelope(p)
        _gondola(p)
        _nacelle(p, 1)
        _nacelle(p, -1)
        _fins(p)

    return build_boss_model(
        GALE_CORVETTE,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "engine-left": _engine_gun,
                "engine-right": _engine_gun,
                "bow-gun": _bow_gun,
            },
            # MB-GALE-CORVETTE-05: its propellers swivel up and reverse as it turns round.
            "rig": {"build": build_prop_rig, "triangles": prop_triangles},
            "armour": {
                "fairings": {"whole": _fairings},
                "rotor-hatch": {"whole": _draw_hatch, "frame": _draw_hatch_frame},
            },
        },
    )
