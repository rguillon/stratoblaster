"""How a prop sits on the ground (P04-R04): pure helpers of the prop placement"""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Sequence  # noqa: E402
from typing import Protocol  # noqa: E402

from core.scenery.height_field import HeightField  # noqa: E402


class Heights(Protocol):
    """Anything that tells the ground's height (a `HeightField`, a `SampledGround`)."""

    def height(self, x: float, z: float) -> float: ...


__pragma__("noskip")


class SampledGround:
    """The heights of `field` sampled on the grid of multiples of `step` that covers the square of
    `size` from (`x0`, `z0`), read back between the samples as the terrain's mesh draws them (D-212:
    the trees of a cell ask for many heights; the field's cost a few octaves of noise each). The
    mesh has a vertex at every multiple of its cell, and splits each cell into two triangles along
    the diagonal from its (+X, -Z) corner to its (-X, +Z) corner (`build_grid_indices`): with
    `step` its cell, a tree stands on the ground drawn. Outside the grid, its edge."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self, field: Heights, x0: float, z0: float, size: float, step: float
    ) -> None:
        i0 = math.floor(x0 / step)
        j0 = math.floor(z0 / step)
        self._columns = max(1, math.ceil((x0 + size) / step) - i0)
        self._rows = max(1, math.ceil((z0 + size) / step) - j0)
        self._x0 = i0 * step
        self._z0 = j0 * step
        self._step = step
        self._heights = [
            field.height((i0 + i) * step, (j0 + j) * step)
            for j in range(self._rows + 1)
            for i in range(self._columns + 1)
        ]

    def height(self, x: float, z: float) -> float:
        columns = self._columns
        rows = self._rows
        u = _clamped((x - self._x0) / self._step, columns)
        v = _clamped((z - self._z0) / self._step, rows)
        i = math.floor(u)
        j = math.floor(v)
        i = columns - 1 if i > columns - 1 else i
        j = rows - 1 if j > rows - 1 else j
        fu = u - i
        fv = v - j
        h = self._heights
        row = columns + 1
        h10 = h[j * row + i + 1]
        h01 = h[(j + 1) * row + i]
        if fu + fv <= 1:
            h00 = h[j * row + i]
            return h00 + (h10 - h00) * fu + (h01 - h00) * fv
        h11 = h[(j + 1) * row + i + 1]
        return h11 + (h01 - h11) * (1 - fu) + (h10 - h11) * (1 - fv)


# Comparisons and index loops, not `min`, `max` and `for v in`: in JavaScript those go through
# Transcrypt's slower helpers, and the trees ask for many (D-212).
def _min_of(values: Sequence[float]) -> float:
    low = values[0]
    for k in range(1, len(values)):
        if values[k] < low:  # noqa: PLR1730
            low = values[k]
    return low


def _max_of(values: Sequence[float]) -> float:
    high = values[0]
    for k in range(1, len(values)):
        if values[k] > high:  # noqa: PLR1730
            high = values[k]
    return high


def _clamped(v: float, high: float) -> float:
    """`v` within [0, `high`]."""
    if v < 0:
        return 0
    return high if v > high else v


def lowest_under(field: HeightField, x: float, z: float, half: float) -> float:
    """The lowest ground under a square of half side `half` around (x, z)."""
    heights = [field.height(x, z)]
    for dx in [-half, half]:
        for dz in [-half, half]:
            heights.append(field.height(x + dx, z + dz))
    return _min_of(heights)


def standing_height(
    field: Heights,
    spot: Sequence[float],
    limits: Sequence[float],
) -> float | None:
    """Lowest ground height under a footprint of radius `radius` around (`x`, `z`), or None when
    the ground there is steeper than `max_slope` or lower than `min_height`.

    `spot` is (x, z, radius); `limits` is (max_slope, min_height).
    """
    x = spot[0]
    z = spot[1]
    radius = spot[2]
    max_slope = limits[0]
    min_height = limits[1]
    heights = [
        field.height(x, z),
        field.height(x + radius, z),
        field.height(x - radius, z),
        field.height(x, z + radius),
        field.height(x, z - radius),
    ]
    low = _min_of(heights)
    high = _max_of(heights)
    if low < min_height:
        return None
    return low if high - low <= max_slope * radius else None
