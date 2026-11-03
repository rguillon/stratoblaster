# Copyright (c) 2026 Renaud Guillon
"""The Narwhal's pressure hull (FB-NARWHAL-02, FB-NARWHAL-06, 2-1): its body and the caps over it.

The hull is one round body from tail to nose (`HULL`, loft stations). Over its two armour regions
(the back and the spine) it is drawn in two parts (D-254): the core keeps the lower half of the
body there, flat on top at `DECK`, and each region's armour is the cap over it, the body's upper
half from `CAP_BOTTOM` up, so that the whale looks whole at rest and keeps a flat deck once its
plating has burst off. Logical pixels, nose +Z, Y up (towards the camera).
"""

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.world_2.loft_spans import shifted_paint, span_of, station_at
from game.view.bosses.world_2.narwhal_parts import SUB_SECTION
from game.view.bosses.world_2.w2_organic import ICE_FLESH
from game.view.enemies.enemy_shapes import side_stripe
from render.geometry.solids import LoftOptions

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import EnemyParts

# __pragma__ ("noskip")


N = BOSS_LOOK.neon.narwhal
if N == None:
    N = [0.05, 0.95, 0.75]

# The pressure hull (loft stations, tail to nose: z, half width, bottom, top): round, its widest
# just behind the hump.
HULL = [  # type: list[list[float]]
    [-66, 4, 2, 9],
    [-56, 9, -2, 12],
    [-40, 14, -5, 15],
    [-16, 17, -7, 17],
    [10, 18, -7, 17.5],
    [30, 16.5, -6, 16.5],
    [42, 13, -4, 14],
    [50, 8, -1, 10],
    [56, 0, 4.5, 4.5],
]
# The flat back of `SUB_SECTION`.
BACK = 4
# Where the two armour regions span the hull along Z (FB-NARWHAL-06): the back behind the hump,
# the spine from the hump's rear to the forward deck. Their caps overlap the tail and the nose by
# `OVERLAP` so no seam shows at rest.
BACK_SPAN = [-41, -8]
SPINE_SPAN = [-8, 40]
OVERLAP = 0.2
# The core's flat deck under the armour, and the cap's bottom, sunk a little into it: the hull's
# widest line (height 0.5 of `SUB_SECTION`) runs at 5 to 5.3 along the body.
DECK = 5.3
CAP_BOTTOM = 5.0
# The lower half of `SUB_SECTION` under a flat top (the core where a cap lies), and the cap over
# it: the upper half, from the widest line up, its flat back at `CAP_BACK` and its shoulders.
LOWER_SECTION = [  # type: list[list[float]]
    [0.4, 0],
    [0.92, 0.4],
    [1.0, 1.0],
    [-1.0, 1.0],
    [-0.92, 0.4],
    [-0.4, 0],
]
CAP_SECTION = [  # type: list[list[float]]
    [1.0, 0],
    [0.85, 0.6],
    [0.35, 1.0],
    [-0.35, 1.0],
    [-0.85, 0.6],
    [-1.0, 0],
]
CAP_BACK = 2
CAP_SHOULDERS = [1, 3]
# Where the neon lines along the back run (the stations' Z), and the stripe on a shoulder.
NEON_FROM = -56
NEON_TO = 42
STRIPE_SPAN = [0.1, 0.35]
STRIPE_LIFT = 1.03


def hull_paint(side: int, band: int) -> Any:
    """Snow lies in patches along its back, between the neon lines (FB-NARWHAL-05).

    `band` is the band's index among the whole hull's.
    """
    if side == BACK and band % 2 == 1:
        return ICE_FLESH.rime
    if band == 0:
        return ICE_FLESH.bone
    return None


def _cap_paint(side: int, band: int) -> Any:
    """Snow on a cap's flat back, the same patches as the hull's."""
    if side == CAP_BACK and band % 2 == 1:
        return ICE_FLESH.rime
    return None


def hull_span(z0: float, z1: float) -> Any:
    """Return `[stations, first]`: the hull's stations from `z0` to `z1`, and its first band.

    See `loft_spans.span_of`.
    """
    return span_of(HULL, z0, z1)


def half_width(z: float) -> float:
    """Return the hull's half width at `z` (between its stations)."""
    return station_at(HULL, z)[1]


def _stripe_stations(stations: list[list[float]], bottom: Any) -> list[list[float]]:
    """Return `stations` with their bottom at `bottom` (a cap's), or as they are."""
    if bottom == None:
        return stations
    return [[st[0], st[1], bottom, st[3]] for st in stations]


def _neon_lines(p: EnemyParts, section: Any, sides: list[int], stations: Any) -> None:
    """Draw the two teal lines along the back, on the shoulders `sides` of `section`."""
    for side in sides:
        stripe = side_stripe(section, side, STRIPE_SPAN, STRIPE_LIFT)
        p.neon.loft(stripe, stations, N, None, LoftOptions(True))


def _whole(p: EnemyParts, z0: float, z1: float, neon_z: Any) -> None:
    """Draw the body whole from `z0` to `z1` (its tail or its nose).

    The neon lines run over `neon_z` (a span along Z), when given.
    """
    span = hull_span(z0, z1)
    paint = shifted_paint(hull_paint, span[1])
    p.flesh.loft(SUB_SECTION, span[0], ICE_FLESH.teal, None, LoftOptions(False, paint))
    if neon_z != None:
        _neon_lines(p, SUB_SECTION, [BACK - 1, BACK + 1], hull_span(neon_z[0], neon_z[1])[0])


def hull_body(p: EnemyParts) -> None:
    """Draw the core's body (FB-NARWHAL-02): teal flesh, whole at the tail and the nose.

    Between them, under the armour (FB-NARWHAL-06), only its lower half, flat on top at `DECK`:
    the deck its plating leaves bare once shed, where its lances and racks rise.
    """
    _whole(p, HULL[0][0], BACK_SPAN[0], [NEON_FROM, BACK_SPAN[0]])
    lower = hull_span(BACK_SPAN[0], SPINE_SPAN[1])[0]
    p.flesh.loft(
        LOWER_SECTION,
        [[st[0], st[1], st[2], DECK] for st in lower],
        ICE_FLESH.teal,
    )
    _whole(p, SPINE_SPAN[1], HULL[-1][0], [SPINE_SPAN[1], NEON_TO])


def hull_cap(p: EnemyParts, z0: float, z1: float) -> None:
    """Draw the cap over the body from `z0` to `z1`: the armour of a region (FB-NARWHAL-06).

    The hull's upper half from `CAP_BOTTOM` up, snow in patches on its flat back and the two neon
    lines along its shoulders, as the whole body has.
    """
    span = hull_span(z0, z1)
    stations = _stripe_stations(span[0], CAP_BOTTOM)
    paint = shifted_paint(_cap_paint, span[1])
    p.flesh.loft(CAP_SECTION, stations, ICE_FLESH.teal, None, LoftOptions(False, paint))
    _neon_lines(p, CAP_SECTION, CAP_SHOULDERS, stations)
