"""Shapes shared by the veteran models (P05-R14 to P05-R18), ported from
`enemies/veteran-shapes.ts`. Logical pixels, nose +Z, Y up."""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[float]
type Rgb = list[float]
__pragma__("noskip")

from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from render.geometry.solids import LoftOptions  # noqa: E402

WHITE = [1, 1, 1]  # type: list[float]
QUARTER = math.pi / 2


def nose_gun(parts: Any, at: Vec3, length: float, radius: float = 0.55) -> None:
    """A gun barrel from `at` towards the nose, `length` long and `radius` thick, a charge light at
    its mouth, its muzzle marked just past it (phase 7 review: shots leave from the barrels the
    player sees)."""
    x = at[0]
    y = at[1]
    z = at[2]
    parts.hull.cylinder(
        radius, length, 6, ENEMY_LOOK.hull.dark, Placement([x, y, z], 0, QUARTER), radius
    )
    parts.charge.cylinder(radius * 1.1, 0.8, 6, WHITE, Placement([x, y, z + length], 0, QUARTER))
    parts.muzzle([x, y, z + length + 0.8], "gun")


def station_at(stations: Any, z: float) -> list[float]:
    """The station of a loft (tail to nose) at `z`, between its two nearest ones."""
    after = -1
    for i, s in enumerate(stations):
        if after < 0 and s[0] >= z:
            after = i
    b = stations[max(0, after)] if len(stations) > 0 else None
    a = stations[max(0, after - 1)] if len(stations) > 0 else b
    if a == None or b == None:  # noqa: E711
        raise Exception("A loft needs stations")
    t = 0 if b[0] == a[0] else (z - a[0]) / (b[0] - a[0])

    def mix(i: int) -> float:
        value: float = a[i] + (b[i] - a[i]) * t
        return value

    return [z, mix(1), mix(2), mix(3)]


# The upper half of a round section (open), from one side over the back to the other.
BAND_SECTION = [[1, 0.45], [0.5, 1], [-0.5, 1], [-1, 0.45]]  # type: list[list[float]]


def back_band(builder: Any, stations: Any, span: Any, color: Rgb, lift: float = 0.12) -> None:
    """A neon band painted over the back of a loft (`stations`, a POD_SECTION-like body) from `z0`
    to `z1`, standing `lift` off it: a stripe across a wasp's abdomen."""

    def raise_station(st: list[float]) -> list[float]:
        return [st[0], st[1] + lift, st[2], st[3] + lift]

    z0 = span[0]
    z1 = span[1]
    builder.loft(
        BAND_SECTION,
        [raise_station(station_at(stations, z0)), raise_station(station_at(stations, z1))],
        color,
        None,
        LoftOptions(True),
    )


def edge_strip(a: Any, b: Any, width: float) -> list[list[float]]:
    """A strip `width` wide just outside the edge from `a` to `b` of an outline around the origin:
    a neon edge light, e.g. along a flying wing's leading edge."""
    dx = b[0] - a[0]
    dz = b[1] - a[1]
    d = math.sqrt(dx * dx + dz * dz)
    nx = dz / d
    nz = -dx / d
    # Away from the centre.
    if nx * (a[0] + b[0]) + nz * (a[1] + b[1]) < 0:
        nx = -nx
        nz = -nz
    return [
        [a[0], a[1]],
        [b[0], b[1]],
        [b[0] + nx * width, b[1] + nz * width],
        [a[0] + nx * width, a[1] + nz * width],
    ]
