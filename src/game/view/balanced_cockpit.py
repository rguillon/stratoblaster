# Copyright (c) 2026 Renaud Guillon
"""The Balanced ship's cockpit (GFX-SHIP-01, D-354): its canopy, frame and what shows inside.

Owner: "make a better realistic looking cockpit". A fighter's canopy sitting on the body's deck,
not a ball on it: lofted along the ship, each section an arch on the sill where it meets the hull;
a low, raked windscreen rising to the front bow, the bubble's peak just behind it, then a long, slow
fall into the spine. Tinted glass shows the cockpit inside: a dark floor, the instrument hood under
the windscreen, the ejection seat and the pilot's helmet. A dark bow frames the windscreen and
glowing rails run along both sills (the cockpit glows as the wings' edges do, D-335).

Pure geometry: sections `[z, ring]` and points; `balanced_ship.py` builds the meshes. Model units,
nose towards +Z, Y up.
"""

import math

from game.view.balanced_hull import smooth_stations, station_at, top_height

# isort: split
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")

# The canopy, `[z, half width, height over the sill]`, front to back.
CANOPY_ROWS = [
    [1.72, 0.06, 0.0],
    [1.64, 0.08, 0.045],
    [1.54, 0.092, 0.088],
    [1.42, 0.1, 0.115],
    [1.24, 0.104, 0.128],
    [1.04, 0.102, 0.124],
    [0.86, 0.096, 0.108],
    [0.7, 0.086, 0.08],
    [0.56, 0.07, 0.045],
    [0.46, 0.055, 0.0],
]
# Each gap between rows is cut into this many sections, along a smooth curve.
CANOPY_STEPS = 2
# Points round the canopy's arch, from the right sill over to the left one (its smooth part).
ARCH_POINTS = 11
# How far under the sill the canopy's skin closes, so no gap shows where it meets the hull.
SINK = 0.02
# The windscreen's bow: where it stands, its width along the ship, its thickness, its segments.
BOW = {"z": 1.42, "width": 0.022, "thickness": 0.012}
BOW_SEGMENTS = 8
# The sill rails: their width and how far they stand over the sill.
RAIL = {"width": 0.014, "height": 0.012}
# These hold numbers only, unannotated: Transcrypt leaves annotated module names unexported.
# Inside: the floor (a share of the canopy's half width, its depth); the instrument hood (Z front
# and back, half width, height); the seat (Z front and back, half width, height; the headrest's
# half width and height); the helmet (Z, radius, its middle's height over the floor).
FLOOR = {"share": 0.85, "depth": 0.03}
HOOD_ZS = [1.58, 1.44]
HOOD = {"half": 0.07, "height": 0.05}
SEAT_ZS = [0.88, 0.82]
SEAT = {
    "half": 0.045,
    "height": 0.085,
    "headHalf": 0.03,
    "headHeight": 0.09,
}
HELMET = {"z": 0.93, "radius": 0.032, "y": 0.06}


def canopy_rows() -> list[list[float]]:
    """Return the canopy's rows, cut along smooth curves (`[z, half width, height]`)."""
    return smooth_stations(CANOPY_ROWS, CANOPY_STEPS)


def canopy_at(z: float) -> list[float]:
    """Return the canopy's half width and height at `z`, between its rows."""
    rows = canopy_rows()
    for i in range(len(rows) - 1):
        a = rows[i]
        b = rows[i + 1]
        if b[0] <= z <= a[0]:
            t = (a[0] - z) / (a[0] - b[0])
            return [a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]
    return [0.0, 0.0]


def sill_height(z: float, half: float) -> float:
    """Height of the canopy's sill at `z`: the hull's top where its edge meets it."""
    return top_height(station_at(z), half)


def floor_height(z: float) -> float:
    """Height of the cockpit's floor at `z`: a hair over the deck's middle."""
    return top_height(station_at(z), 0) + 0.004


def arch(half: float, height: float, sill: float, count: int) -> list[list[float]]:
    """Return an arch's `count` points over a sill, from its right foot over to its left one."""
    points: list[list[float]] = []
    for i in range(count):
        angle = math.pi * i / (count - 1)
        points.append([half * math.cos(angle), sill + height * math.sin(angle)])
    return points


def canopy_sections() -> list[list[Any]]:
    """Return the canopy's sections, front to back: the arch, then two points under the sill.

    The first `ARCH_POINTS` of each ring are the glass (the smooth part).
    """
    sections: list[list[Any]] = []
    for row in canopy_rows():
        z = row[0]
        half = row[1]
        sill = sill_height(z, half)
        ring = arch(half, row[2], sill, ARCH_POINTS)
        ring.append([-half, sill - SINK])
        ring.append([half, sill - SINK])
        sections.append([z, ring])
    return sections


def rail_sections(side: float, grow: float = 1.0) -> list[list[Any]]:
    """Return the sections of the sill rail on `side` (1 right, -1 left), front to back.

    `grow` widens it, as the ship's glowing edges are on the playfield (D-355).
    """
    width = RAIL["width"] * grow
    sections: list[list[Any]] = []
    for row in canopy_rows():
        z = row[0]
        x = side * row[1]
        sill = sill_height(z, row[1])
        low = sill - 0.006
        high = sill + RAIL["height"]
        inner = x - side * width / 2
        outer = x + side * width / 2
        sections.append([z, [[outer, high], [inner, high], [inner, low], [outer, low]]])
    return sections


def bow_segments() -> list[list[float]]:
    """Return the windscreen bow's segments over the canopy: `[x, y, angle, length]` each.

    Each lies along the arch, a hair outside the glass, its middle at `x, y`, turned `angle` round
    Z from +X.
    """
    half, height = canopy_at(BOW["z"])
    sill = sill_height(BOW["z"], half)
    grow = BOW["thickness"] / 2
    points = arch(half + grow, height + grow, sill, BOW_SEGMENTS + 1)
    segments: list[list[float]] = []
    for i in range(len(points) - 1):
        a = points[i]
        b = points[i + 1]
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        segments.append([
            (a[0] + b[0]) / 2,
            (a[1] + b[1]) / 2,
            math.atan2(dy, dx),
            math.sqrt(dx * dx + dy * dy),
        ])
    return segments


def floor_sections() -> list[list[Any]]:
    """Return the cockpit floor's sections: a dark slab under the glass, front to back."""
    sections: list[list[Any]] = []
    for row in CANOPY_ROWS:
        z = row[0]
        half = row[1] * FLOOR["share"]
        top = floor_height(z)
        bottom = top - FLOOR["depth"]
        sections.append([z, [[half, top], [-half, top], [-half, bottom], [half, bottom]]])
    return sections
