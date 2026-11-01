"""The lines of a dark metal frame laid where armour was cut away (docs/superpowers/specs/2026-10-
31-boss-armour-shedding-design.md): ribs across the armour's footprint, clipped to it.

Pure: no Babylon. Points are `[x, z]` in the XZ plane; a footprint is the top view of the armour's
up-facing triangles.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# The cell of the footprint's lookup grid, px.
GRID = 8.0


def _in_triangle(t: list[float], x: float, z: float) -> bool:
    """Whether (x, z) is in the triangle `t` (flat: x0, z0, x1, z1, x2, z2), on either winding."""
    d1 = (x - t[2]) * (t[1] - t[3]) - (t[0] - t[2]) * (z - t[3])
    d2 = (x - t[4]) * (t[3] - t[5]) - (t[2] - t[4]) * (z - t[5])
    d3 = (x - t[0]) * (t[5] - t[1]) - (t[4] - t[0]) * (z - t[1])
    negative = d1 < 0 or d2 < 0 or d3 < 0
    positive = d1 > 0 or d2 > 0 or d3 > 0
    return not (negative and positive)


def _key(i: int, j: int) -> str:
    return str(i) + ":" + str(j)


class Footprint:
    """The top view of a set of triangles (each `[[x, z], [x, z], [x, z]]`), with its bounds."""

    def __init__(self, tris: list[list[list[float]]]) -> None:
        self.tris: list[list[float]] = []
        self.cells: dict[str, list[int]] = {}
        self.low = [math.inf, math.inf]
        self.high = [-math.inf, -math.inf]
        for tri in tris:
            flat = [tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]]
            index = len(self.tris)
            self.tris.append(flat)
            x0 = min(flat[0], flat[2], flat[4])
            x1 = max(flat[0], flat[2], flat[4])
            z0 = min(flat[1], flat[3], flat[5])
            z1 = max(flat[1], flat[3], flat[5])
            self.low = [min(self.low[0], x0), min(self.low[1], z0)]
            self.high = [max(self.high[0], x1), max(self.high[1], z1)]
            for i in range(math.floor(x0 / GRID), math.floor(x1 / GRID) + 1):
                for j in range(math.floor(z0 / GRID), math.floor(z1 / GRID) + 1):
                    key = _key(i, j)
                    if key not in self.cells:
                        self.cells[key] = []
                    self.cells[key].append(index)

    def empty(self) -> bool:
        """Whether it covers nothing."""
        return len(self.tris) == 0

    def holds(self, x: float, z: float) -> bool:
        """Whether (x, z) is under one of its triangles (a plain loop: ENG-157)."""
        key = _key(math.floor(x / GRID), math.floor(z / GRID))
        if key not in self.cells:
            return False
        for k in self.cells[key]:  # noqa: SIM110 (Transcrypt: any() over a generator is slow)
            if _in_triangle(self.tris[k], x, z):
                return True
        return False

    def centre(self) -> list[float]:
        """The middle of its bounds."""
        return [(self.low[0] + self.high[0]) / 2, (self.low[1] + self.high[1]) / 2]


def _span(low: float, high: float, gap: float) -> list[float]:
    """Stations `gap` apart, centred between `low` and `high`, strictly inside them."""
    count = math.floor((high - low) / gap)
    start = (low + high) / 2 - (count * gap) / 2
    return [start + k * gap for k in range(count + 1) if low < start + k * gap < high]


def frame_lines(style: str, footprint: Footprint, gap: float, spokes: int) -> list[list[Any]]:
    """The frame's lines over `footprint`, each `[a, b]`, unclipped: `wing` ribs along Z every
    `gap` across X, and two spars along X; `shell` a lattice `gap` apart both ways; `ring` `spokes`
    spokes out from the middle, and a hoop half way out."""
    low = footprint.low
    high = footprint.high
    result: list[list[Any]] = []
    if style == "ring":
        c = footprint.centre()
        reach = math.hypot(high[0] - low[0], high[1] - low[1]) / 2
        for k in range(spokes):
            a = (2 * math.pi * k) / spokes
            result.append([c, [c[0] + math.cos(a) * reach, c[1] + math.sin(a) * reach]])
        hoop = 2 * spokes
        for k in range(hoop):
            a = (2 * math.pi * k) / hoop
            b = (2 * math.pi * (k + 1)) / hoop
            r = reach / 2
            result.append(
                [
                    [c[0] + math.cos(a) * r, c[1] + math.sin(a) * r],
                    [c[0] + math.cos(b) * r, c[1] + math.sin(b) * r],
                ]
            )
        return result
    for x in _span(low[0], high[0], gap):
        result.append([[x, low[1]], [x, high[1]]])
    if style == "shell":
        zs = _span(low[1], high[1], gap)
    else:
        depth = high[1] - low[1]
        zs = [low[1] + depth / 3, low[1] + (2 * depth) / 3]
    for z in zs:
        result.append([[low[0], z], [high[0], z]])
    return result


def clip_line(line: list[Any], footprint: Footprint, step: float, least: float) -> list[list[Any]]:
    """The pieces of `line` over `footprint`, sampled every `step`, each at least `least` long."""
    a = line[0]
    b = line[1]
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    count = max(1, math.ceil(length / step))
    result: list[list[Any]] = []
    start = -1
    for k in range(count + 1):
        t = k / count
        x = a[0] + (b[0] - a[0]) * t
        z = a[1] + (b[1] - a[1]) * t
        held = footprint.holds(x, z)
        if held and start < 0:
            start = k
        if start >= 0 and (not held or k == count):
            end = k if held else k - 1
            if (end - start) * (length / count) >= least:
                t0 = start / count
                t1 = end / count
                result.append(
                    [
                        [a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0],
                        [a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1],
                    ]
                )
            start = -1
    return result
