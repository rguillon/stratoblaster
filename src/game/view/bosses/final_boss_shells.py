# Copyright (c) 2026 Renaud Guillon
"""Carapaces drawn in lengths along Z (D-254), for the World 1 final bosses.

A boss whose armour is a length of its own shell (the Storm Petrel's tail plating, the Refinery
Titan's back and nose plating) draws the shell of its body as `render.geometry.organic.carapace`
would, but a length at a time: the core draws the lengths it keeps, the armour the length it sheds,
and they meet at the same stations. Logical pixels, nose +Z, Y up (towards the camera).
"""

from render.geometry.organic import SHELL_SECTION, SegmentedBody, segment_stations
from render.geometry.solids import LoftOptions

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# The pinch of a carapace's waists (as `carapace` draws them).
SHELL_PINCH = 0.12


def shell_body(
    tail: float, nose: float, segments: int, width: float, bottom: float, top: float
) -> SegmentedBody:
    """Return the body of a boss's shell, as `world_1_organic_kit.hide` lofts its carapace.

    `width` is the body's half width (the shell is a little narrower), `bottom` and `top` the
    body's: the shell runs from 1 px under the body's middle height up to `top`.
    """
    mid = (bottom + top) / 2
    return SegmentedBody(tail, nose, segments, width * 0.92, mid - 1, top, SHELL_PINCH)


def station_at(stations: list[Any], z: float) -> list[float]:
    """Return the loft station at `z`, interpolated between the two of `stations` around it.

    Past the last station, the last one.
    """
    for k in range(len(stations) - 1):
        a = stations[k]
        b = stations[k + 1]
        if z <= b[0]:
            t = 0 if b[0] == a[0] else (z - a[0]) / (b[0] - a[0])
            return [a[i] + (b[i] - a[i]) * t for i in range(4)]
    last: list[float] = stations[len(stations) - 1]
    return last


def shell_stations(body: SegmentedBody, z0: float, z1: float) -> list[Any]:
    """Return the loft stations of the shell of `body` from `z0` to `z1`.

    `[stations, first]`: the stations between the two heights, interpolated at both ends (an end
    at the body's own end closes to its point), and the index of the body's band `z0` lies in (so
    the seams keep their rhythm from one length to the next).
    """
    stations = segment_stations(body)
    result: list[Any] = [station_at(stations, z0)]
    result.extend([s for s in stations if z0 < s[0] < z1])
    result.append(station_at(stations, z1))
    first = len([s for s in stations if s[0] <= z0]) - 1
    return [result, max(0, first)]


def shell_length(b: Any, body: SegmentedBody, colors: list[Any], z0: float, z1: float) -> None:
    """Draw the shell of `body` from `z0` to `z1` in `b`: a carapace, its plates seamed.

    Alternately `colors[0]` and `colors[1]`, the seams in step with the body's other lengths.
    """
    clipped = shell_stations(body, z0, z1)
    offset = clipped[1]

    def paint(_side: int, band: int) -> Any:
        return colors[1] if (band + offset) % 2 == 1 else None

    b.loft(SHELL_SECTION, clipped[0], colors[0], None, LoftOptions(False, paint))
