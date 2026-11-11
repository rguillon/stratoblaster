# Copyright (c) 2026 Renaud Guillon
"""The Balanced ship's central body (GFX-SHIP-01, D-327, D-332, D-336).

A long, slim fuselage lofted through cross-sections, faceted (owner, D-336: "rework the central
part, it's too round, add more details, make a better connection with the wings"): each section is
a few flat facets: a dorsal spine ridge, a flat deck either side of it, bevelled shoulders down to
the chines, a flat underside and a flat belly. The chines run out flat at the height of the wings'
top face and widen behind the canards into strakes that reach the nacelles: the body itself is the
stub wing joining them, its leading edge one swept curve from the canards to the intakes. It closes
to a point at both ends: nothing comes out of its back (owner, D-332: "the central body had no back
reactor"); the reactors are the nacelles and the pairs on the wing tips.

Stations along the ship give each part's size; between them the sizes follow smooth curves.
Model units: nose towards +Z, Y up.
"""

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
SPINE = 5

# `[z, body half width, deck height, belly depth, chine half width, spine]`, nose to tail. D-332:
# long and slim; D-336: the chines widen from the canards into strakes out to the nacelles (their
# inner corner at 0.58 across) and close in behind them; a spine ridge runs from the canopy's back
# to the tail. D-354 (owner: "make the nose longer, less pointy"): the nose runs 0.55 further, to
# 3.3, and is blunt: it swells fast behind its tip, a rounded radome rather than a needle.
STATIONS = [
    [3.3, 0, 0, 0, 0, 0],
    [3.22, 0.05, 0.043, 0.038, 0.055, 0],
    [2.85, 0.12, 0.1, 0.083, 0.13, 0],
    [1.6, 0.182, 0.148, 0.122, 0.21, 0],
    [1.0, 0.2, 0.16, 0.13, 0.25, 0],
    [0.5, 0.24, 0.19, 0.15, 0.38, 0.02],
    [0.0, 0.26, 0.2, 0.16, 0.57, 0.04],
    [-0.4, 0.26, 0.2, 0.16, 0.64, 0.045],
    [-1.2, 0.24, 0.18, 0.14, 0.64, 0.045],
    [-1.9, 0.16, 0.12, 0.09, 0.63, 0.03],
    [-2.2, 0.08, 0.06, 0.05, 0.18, 0.01],
    [-2.45, 0, 0, 0, 0, 0],
]
# Each gap between stations is cut into this many sections.
STATION_STEPS = 3
# Points across the top, from one chine edge to the other: the chine edge, the chine's root, the
# shoulder, the deck's edge, the spine and the same on the other side.
TOP_POINTS = 9
# The chine stands as high as the wing's top face, so the wings run out of it flush.
CHINE_EDGE = 0.035
# Where the facets meet, as shares of the body's half width: the chine's root, the shoulder, the
# deck's edge; the shoulder's height as a share of the deck's.
CHINE_ROOT = 1.1
SHOULDER = 0.8
DECK_EDGE = 0.4
SHOULDER_HEIGHT = 0.75
# The underside's points, as shares of the body's half width and the belly's depth.
FLANK = [0.9, 0.5]
BELLY_CORNER = 0.45


def chine_edge(station: list[float]) -> float:
    """Height of the chine's edge at a station: the wings' top, lower where the chine is narrow."""
    return CHINE_EDGE * min(1, station[CHINE_HALF_WIDTH] / 0.3)


def top_ring(station: list[float]) -> list[list[float]]:
    """Return the top's `TOP_POINTS` at a station, from the right chine edge over to the left."""
    half = station[BODY_HALF_WIDTH]
    chine = station[CHINE_HALF_WIDTH]
    deck = station[BODY_HEIGHT]
    edge = chine_edge(station)
    right = [
        [chine, edge],
        [min(half * CHINE_ROOT, chine), edge],
        [half * SHOULDER, max(edge, deck * SHOULDER_HEIGHT)],
        [half * DECK_EDGE, max(edge, deck)],
    ]
    ring = [list(p) for p in right]
    ring.append([0, max(edge, deck + station[SPINE])])
    ring.extend([[-right[k][0], right[k][1]] for k in range(len(right) - 1, -1, -1)])
    return ring


def top_height(station: list[float], x: float) -> float:
    """Height of the hull's top at `x` (either side), at a station; 0 past the chines."""
    side = abs(x)
    if station[CHINE_HALF_WIDTH] <= side:
        return 0
    ring = top_ring(station)
    # The right half, from the spine out to the chine edge.
    for k in range(4, 0, -1):
        inner = ring[k]
        outer = ring[k - 1]
        if side <= outer[0]:
            span = outer[0] - inner[0]
            t = (side - inner[0]) / span if span > 0 else 1
            return inner[1] + (outer[1] - inner[1]) * t
    return ring[0][1]


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
    one, then the underside from the left chine's edge round the belly to the right one's.
    """
    ring = top_ring(station)
    half = station[BODY_HALF_WIDTH]
    depth = station[BELLY_DEPTH]
    edge = chine_edge(station)
    chine = station[CHINE_HALF_WIDTH]
    under = [
        [-chine, -edge],
        [-half * FLANK[0], -depth * FLANK[1]],
        [-half * BELLY_CORNER, -depth],
        [half * BELLY_CORNER, -depth],
        [half * FLANK[0], -depth * FLANK[1]],
        [chine, -edge],
    ]
    for p in under:
        ring.append(p)
    return [station[Z], ring]


def underside_height(station: list[float], x: float) -> float:
    """Height of the hull's underside at `x` (either side), at a station.

    Along its flat belly, its flanks and its chines' undersides; the chine's edge past them.
    """
    _z, ring = hull_section(station)
    under = ring[TOP_POINTS:]
    side = abs(x)
    # The right half, from the belly's corner out to the chine's edge.
    points = [under[3], under[4], under[5]]
    if side <= points[0][0]:
        return float(points[0][1])
    for k in range(len(points) - 1):
        inner = points[k]
        outer = points[k + 1]
        if side <= outer[0]:
            span = outer[0] - inner[0]
            t = (side - inner[0]) / span if span > 0 else 1
            return float(inner[1] + (outer[1] - inner[1]) * t)
    return float(points[len(points) - 1][1])


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
