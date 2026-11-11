# Copyright (c) 2026 Renaud Guillon
"""The Balanced ship's central body (GFX-SHIP-01, D-327, D-332).

A long, slim fuselage lofted through cross-sections: each section's top is the smooth union of the
fuselage's rounded back and a thin chine along its flanks, whose edge stands as high as the wings'
and stub wings' top faces, so they run out of it flush. Where back and chine meet, a smooth maximum
rounds the joint into a fillet. The belly is three flat facets. It closes to a point at both ends:
nothing comes out of its back (owner, D-332: "the central body had no back reactor"); the reactors
are the nacelles out on the stub wings and the pairs on the wing tips.

Stations along the ship give each part's size; between them the sizes follow smooth curves.
Model units: nose towards +Z, Y up.
"""

import math

# isort: split
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")

# Columns of a station.
Z = 0
BODY_HALF_WIDTH = 1
BODY_HEIGHT = 2
BELLY_DEPTH = 3
CHINE_HALF_WIDTH = 4

# `[z, body half width, body height, belly depth, chine half width]`, nose to tail. D-332 (owner:
# "make the central body longer and thiner"): longer (z 2.75 to -2.45, 4.8 before) and about half
# as wide (0.56 across at its widest, 1.4 with the nacelle shoulders before), a needle nose
# swelling into the cockpit, widest behind it, tapering to a point at the tail.
STATIONS = [
    [2.75, 0, 0, 0, 0],
    [2.45, 0.04, 0.035, 0.03, 0.045],
    [2.0, 0.09, 0.075, 0.06, 0.1],
    [1.5, 0.15, 0.12, 0.1, 0.17],
    [1.0, 0.21, 0.17, 0.13, 0.25],
    [0.5, 0.25, 0.21, 0.15, 0.3],
    [0.0, 0.28, 0.23, 0.16, 0.33],
    [-0.6, 0.28, 0.23, 0.16, 0.33],
    [-1.2, 0.25, 0.2, 0.14, 0.3],
    [-1.8, 0.18, 0.15, 0.1, 0.22],
    [-2.2, 0.1, 0.09, 0.06, 0.12],
    [-2.45, 0, 0, 0, 0],
]
# Each gap between stations is cut into this many sections.
STATION_STEPS = 3
# Points across the top, from one chine edge to the other (the smooth half): half evenly spaced,
# half crowding at the edges where the chine turns down fastest.
TOP_POINTS = 25
# The chine's thickness at the body.
CHINE_THICKNESS = 0.05
# The chine's edge stands as high as the wing's top face, so the wings run out of it flush.
CHINE_EDGE = 0.035
# How wide the fillets are: the smooth maximum's blend.
FILLET = 0.1
# The belly's corners, as a share of the body's half width.
BELLY_CORNER = 0.7


def smooth_max(a: float, b: float, k: float) -> float:
    """Return a maximum of `a` and `b` rounded over `k`: a fillet where the two cross."""
    h = max(k - abs(a - b), 0) / k
    return max(a, b) + h * h * k / 4


def _cap(x: float, half_width: float, height: float) -> float:
    """Height of an elliptic cap `half_width` wide each side of 0, at `x` (0 outside it)."""
    if half_width <= 0 or height <= 0:
        return 0
    u = x / half_width
    return height * math.sqrt(max(0, 1 - u * u))


def top_height(station: list[float], x: float) -> float:
    """Height of the hull's top at `x` (either side), at a station."""
    side = abs(x)
    chine_half = station[CHINE_HALF_WIDTH]
    if chine_half <= side:
        return 0
    body = _cap(side, station[BODY_HALF_WIDTH], station[BODY_HEIGHT])
    chine = CHINE_THICKNESS * max(0, 1 - side / chine_half)
    height = smooth_max(body, chine, FILLET)
    # Towards the chine's edge the top eases down to the wings' top face (less at the nose and the
    # tail, where the chine is narrow).
    edge = CHINE_EDGE * min(1, chine_half / 0.3)
    taper = min(1, (chine_half - side) / FILLET)
    return edge + (height - edge) * taper


def smooth_stations(stations: list[list[float]], steps: int) -> list[list[float]]:
    """Return the stations with each gap cut into `steps`, every column along a smooth curve.

    A Catmull-Rom spline through the stations, so each one is kept; sizes never go under 0.
    """
    count = len(stations)
    result: list[list[float]] = []

    def at(i: int) -> list[float]:
        return stations[max(0, min(count - 1, i))]

    for i in range(count - 1):
        p0 = at(i - 1)
        p1 = at(i)
        p2 = at(i + 1)
        p3 = at(i + 2)
        for k in range(steps):
            t = k / steps
            t2 = t * t
            t3 = t2 * t
            row = [
                0.5
                * (
                    2 * p1[c]
                    + (p2[c] - p0[c]) * t
                    + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2
                    + (3 * p1[c] - p0[c] - 3 * p2[c] + p3[c]) * t3
                )
                for c in range(len(p1))
            ]
            # The sizes (every column but Z) never go under 0. No list `+`: Transcrypt would
            # join them as strings.
            for c in range(1, len(row)):
                row[c] = max(0.0, row[c])
            result.append(row)
    result.append(list(stations[count - 1]))
    return result


def hull_section(station: list[float]) -> list[Any]:
    """Return the cross-section `[z, ring]` at a station.

    The ring starts with the `TOP_POINTS` of the top, from the right chine edge over to the left
    one, then the belly's two corners.
    """
    half = station[CHINE_HALF_WIDTH]
    ring: list[list[float]] = []
    for i in range(TOP_POINTS):
        u = 1 - 2 * i / (TOP_POINTS - 1)
        x = half * (u + math.sin(math.pi / 2 * u)) / 2
        ring.append([x, top_height(station, x)])
    corner = station[BODY_HALF_WIDTH] * BELLY_CORNER
    depth = -station[BELLY_DEPTH]
    ring.append([-corner, depth])
    ring.append([corner, depth])
    return [station[Z], ring]


def hull_sections() -> list[list[Any]]:
    """Return the hull's sections, nose to tail."""
    return [hull_section(s) for s in smooth_stations(STATIONS, STATION_STEPS)]


def station_at(z: float) -> list[float]:
    """Return the hull's sizes at `z`, between the smoothed stations (nose to tail)."""
    rows = smooth_stations(STATIONS, STATION_STEPS)
    if z >= rows[0][Z]:
        return list(rows[0])
    for i in range(len(rows) - 1):
        a = rows[i]
        b = rows[i + 1]
        if b[Z] <= z:
            t = (a[Z] - z) / (a[Z] - b[Z])
            return [a[c] + (b[c] - a[c]) * t for c in range(len(a))]
    return list(rows[len(rows) - 1])
