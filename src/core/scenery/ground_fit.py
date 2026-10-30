"""How a prop sits on the ground (P04-R04): pure helpers of the prop placement"""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Sequence  # noqa: E402

from core.scenery.height_field import HeightField  # noqa: E402

__pragma__("noskip")


def _min_of(values: Sequence[float]) -> float:
    low = values[0]
    for v in values:
        low = min(low, v)
    return low


def _max_of(values: Sequence[float]) -> float:
    high = values[0]
    for v in values:
        high = max(high, v)
    return high


def lowest_under(field: HeightField, x: float, z: float, half: float) -> float:
    """The lowest ground under a square of half side `half` around (x, z)."""
    heights = [field.height(x, z)]
    for dx in [-half, half]:
        for dz in [-half, half]:
            heights.append(field.height(x + dx, z + dz))
    return _min_of(heights)


def standing_height(
    field: HeightField,
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
