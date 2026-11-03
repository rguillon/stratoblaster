# Copyright (c) 2026 Renaud Guillon
"""Spans of a loft: the stations of a body between two Z, to draw it in parts (D-254).

A boss's armour is drawn apart from its core (BOSS-42): a body lofted along Z is cut into the
sections the core keeps and the sections its armour regions are, each lofted from the same
stations so that the surfaces meet. Stations are `[z, half width, bottom, top]`, tail to nose.
"""

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Station = list[float]
# __pragma__ ("noskip")


def station_at(stations: list[Any], z: float) -> list[float]:
    """Return the station of `stations` at `z`, between the two around it (the last past them)."""
    for k in range(len(stations) - 1):
        a = stations[k]
        b = stations[k + 1]
        if z <= b[0]:
            t = 0 if b[0] == a[0] else (z - a[0]) / (b[0] - a[0])
            return [
                z,
                a[1] + (b[1] - a[1]) * t,
                a[2] + (b[2] - a[2]) * t,
                a[3] + (b[3] - a[3]) * t,
            ]
    last = stations[len(stations) - 1]
    return [z, last[1], last[2], last[3]]


def span_of(stations: list[Any], z0: float, z1: float) -> Any:
    """Return `[span, first]`: the stations from `z0` to `z1`, and the band `z0` lies in.

    The span has a station at both ends and the body's own between them; `first` is the index,
    among the whole body's bands, of the band `z0` lies in (so a paint by band can follow on).
    """
    span = [station_at(stations, z0)]
    first = 0
    for k in range(len(stations)):
        if stations[k][0] <= z0:
            first = k
        if z0 < stations[k][0] and stations[k][0] < z1:
            span.append(stations[k])
    span.append(station_at(stations, z1))
    return [span, first]


def shifted_paint(paint: Any, first: int) -> Any:
    """Return `paint` reading its bands from `first` on (a span's first band of the body)."""
    return lambda side, band: paint(side, band + first)
