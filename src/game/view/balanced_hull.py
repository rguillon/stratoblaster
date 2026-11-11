# Copyright (c) 2026 Renaud Guillon
"""The Balanced ship's blended hull (GFX-SHIP-01, D-327).

One skin instead of a fuselage, a spine, strakes and side pods put together: each cross-section's
top is the smooth union of the fuselage's rounded back, the two nacelle shoulders running from the
intakes to the reactors, and a thin chine that flares out into the wing roots (the leading-edge
extensions). Where they meet, a smooth maximum rounds the joint into a fillet, so the shoulders
swell out of the back and the chine sweeps into the wings. The belly is three flat facets.

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
SHOULDER_HEIGHT = 5

# `[z, body half width, body height, belly depth, chine half width, shoulder height]`, nose to
# tail. The chine follows the old strakes' leading edge out to the wing roots; the shoulders rise
# behind the intake mouths and run on over the reactors, standing well over the intakes' and
# nacelles' tops so these never show through: only the intake mouths at the front and the nozzles
# behind the hull's cut-off tail show (D-327: no nacelle stands apart). Behind the cockpit the back
# widens to meet the shoulders into one broad back, with only a shallow saddle between them.
STATIONS = [
    [2.45, 0, 0, 0, 0, 0],
    [2.2, 0.05, 0.04, 0.035, 0.05, 0],
    [1.8, 0.11, 0.085, 0.07, 0.11, 0],
    [1.3, 0.18, 0.13, 0.11, 0.21, 0],
    [0.8, 0.26, 0.18, 0.14, 0.42, 0.06],
    [0.4, 0.32, 0.22, 0.16, 0.6, 0.2],
    [0.0, 0.38, 0.25, 0.17, 0.66, 0.26],
    [-0.5, 0.4, 0.25, 0.17, 0.68, 0.27],
    [-1.0, 0.38, 0.23, 0.15, 0.66, 0.26],
    [-1.4, 0.32, 0.2, 0.12, 0.64, 0.25],
    [-1.72, 0.24, 0.16, 0.08, 0.62, 0.23],
]
# Each gap between stations is cut into this many sections.
STATION_STEPS = 3
# Points across the top, from one chine edge to the other (the smooth half), cosine-spaced so they
# crowd at the edges where the curve turns fastest.
TOP_POINTS = 25
# Where the shoulders run, their half width, and the chine's thickness at the body.
SHOULDER_X = 0.42
SHOULDER_HALF_WIDTH = 0.26
CHINE_THICKNESS = 0.06
# The chine's edge stands as high as the wing's top face, so the wings run out of it flush.
CHINE_EDGE = 0.035
# How wide the fillets are: the smooth maximum's blend.
FILLET = 0.15
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
    body = _cap(side, station[BODY_HALF_WIDTH], station[BODY_HEIGHT])
    shoulder = _cap(side - SHOULDER_X, SHOULDER_HALF_WIDTH, station[SHOULDER_HEIGHT])
    chine_half = station[CHINE_HALF_WIDTH]
    chine = CHINE_THICKNESS * max(0, 1 - side / chine_half) if chine_half > 0 else 0
    height = smooth_max(smooth_max(body, shoulder, FILLET), chine, FILLET)
    if chine_half <= side:
        return 0
    # Towards the chine's edge the top eases down to the wing's top face (nothing at the nose,
    # where the chine is as narrow as the body).
    edge = CHINE_EDGE * min(1, chine_half / SHOULDER_X)
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
        x = half * math.cos(math.pi * i / (TOP_POINTS - 1))
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


def plate_sections(
    xs: list[float], zs: list[float], thickness: float, count: int
) -> list[list[Any]]:
    """Return the sections of a plate lying on the hull's top, from `xs[1]` over to `xs[0]`.

    Conformal: its top follows the hull `thickness` above it, its underside sinks a hair into the
    skin, so it reads as armour laid on the hull, not a flat slab floating over it. `zs` is its
    front and back; each ring has `count` top points (the smooth part), then the underside back.
    """
    sections: list[list[Any]] = []
    steps = max(2, int((zs[0] - zs[1]) / 0.1 + 0.5))
    for s in range(steps + 1):
        z = zs[0] + (zs[1] - zs[0]) * s / steps
        station = station_at(z)
        top: list[list[float]] = []
        under: list[list[float]] = []
        for i in range(count):
            x = xs[1] + (xs[0] - xs[1]) * i / (count - 1)
            surface = top_height(station, x)
            top.append([x, surface + thickness])
            under.insert(0, [x, surface - 0.01])
        ring = list(top)
        ring.extend(under)
        sections.append([z, ring])
    return sections
