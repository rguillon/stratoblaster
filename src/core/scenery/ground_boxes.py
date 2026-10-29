"""The boxes of ground props take, and the buckets of the index of placed buildings. Ported from
`core/scenery/ground-boxes.ts`."""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Sequence  # noqa: E402
from typing import Protocol  # noqa: E402


class GroundBoxPlacement(Protocol):
    """The centre of a box of ground."""

    @property
    def x(self) -> float: ...

    @property
    def z(self) -> float: ...


class BuildingRecord(Protocol):
    """A building placed: its prop, and the half-extents of the box of ground it takes (see
    `away_placement.BuildingRecord`)."""

    @property
    def placement(self) -> "PropPlacement": ...

    @property
    def half_x(self) -> float: ...

    @property
    def half_z(self) -> float: ...


class GroundBox(Protocol):
    """A box of ground a prop takes around its centre (`Pick<BuildingRecord, halfX | halfZ>`)."""

    @property
    def half_x(self) -> float: ...

    @property
    def half_z(self) -> float: ...

    @property
    def placement(self) -> "PropPlacement": ...


__pragma__("noskip")

# Bucket size of the index of placed buildings.
BUILDING_BUCKET = 32
# Margin the buckets left out keep, so rounding never leaves out one that counts.
SLACK = 1e-9
BUCKET_STRIDE = 1000003

INFINITY = float("Infinity")


class PropPlacement:
    """One prop standing on the ground."""

    def __init__(  # noqa: PLR0917 (positional data fields: Transcrypt drops keyword arguments)
        self,
        kind: str,
        x: float,
        y: float,
        z: float,
        rotation: float,
        scale: float,
        size: Sequence[float] | None = None,
    ) -> None:
        self.kind = kind
        """Key of the prop's model (`PropKindRule.id`)."""
        self.x = x
        self.y = y
        """Height of the ground the prop stands on."""
        self.z = z
        self.rotation = rotation
        """Turn around the vertical axis, in radians."""
        self.scale = scale
        self.size = size
        """Per-axis scale (X, Y, Z) instead of `scale`, for podiums stretched to their block."""


class GroundArea:
    """A rectangle of ground, in world units."""

    def __init__(self, x_min: float, x_max: float, z_min: float, z_max: float) -> None:
        self.x_min = x_min
        self.x_max = x_max
        self.z_min = z_min
        self.z_max = z_max


def inside(area: GroundArea, x: float, z: float) -> bool:
    """Whether (`x`, `z`) is inside `area` (its far edges excluded)."""
    return x >= area.x_min and x < area.x_max and z >= area.z_min and z < area.z_max


def overlap(a: GroundBox, b: GroundBox, gap: float) -> bool:
    """Whether the ground boxes of `a` and `b` come closer than `gap`."""
    apart_x = abs(a.placement.x - b.placement.x) >= a.half_x + b.half_x + gap
    apart_z = abs(a.placement.z - b.placement.z) >= a.half_z + b.half_z + gap
    return not apart_x and not apart_z


def _bucket_key(i: int, j: int) -> str:
    return str(i * BUCKET_STRIDE + j)


class _Bucket:
    """A bucket of a `BuildingIndex`: its buildings, and the largest half-extents among them."""

    def __init__(self, buildings: list[BuildingRecord], half_x: float, half_z: float) -> None:
        self.buildings = buildings
        self.half_x = half_x
        self.half_z = half_z


def _to_bucket(v: float, i: int) -> float:
    """Distance from `v` to the bucket `i` along one axis (0 inside it)."""
    return max(0, i * BUILDING_BUCKET - v, v - (i + 1) * BUILDING_BUCKET)


class BuildingIndex:
    """The placed buildings, in buckets `BUILDING_BUCKET` wide by where their centres are
    (reviewer, 2026-10-28: number keys, and a bucket too far for its largest building to come close
    is left out)."""

    def __init__(self) -> None:
        self._buckets: dict[str, _Bucket] = {}

    def add(self, building: BuildingRecord) -> None:
        x = building.placement.x
        z = building.placement.z
        key = _bucket_key(math.floor(x / BUILDING_BUCKET), math.floor(z / BUILDING_BUCKET))
        bucket = self._buckets.get(key)
        if bucket is None:
            self._buckets[key] = _Bucket([building], building.half_x, building.half_z)
            return
        bucket.buildings.append(building)
        bucket.half_x = max(bucket.half_x, building.half_x)
        bucket.half_z = max(bucket.half_z, building.half_z)

    def clear(self, area: GroundBox, gap: float) -> bool:
        """Whether no building of the buckets two around `area`'s comes closer to it than `gap`."""
        x = area.placement.x
        z = area.placement.z
        bx = math.floor(x / BUILDING_BUCKET)
        bz = math.floor(z / BUILDING_BUCKET)
        for i in range(bx - 2, bx + 3):
            dx = _to_bucket(x, i)
            for j in range(bz - 2, bz + 3):
                bucket = self._buckets.get(_bucket_key(i, j))
                if bucket is None:
                    continue
                if dx > area.half_x + bucket.half_x + gap + SLACK:
                    continue
                if _to_bucket(z, j) > area.half_z + bucket.half_z + gap + SLACK:
                    continue
                for b in bucket.buildings:
                    if overlap(b, area, gap):
                        return False
        return True


class PlacerSnapshot:
    """What a `PropPlacer` placed, in order: enough to make it again without placing them
    (P13-R03). The first `fixed` buildings are its set pieces and lines; `placed_to` is the first
    chunk not placed yet (see `PropPlacer.ensure_placed`)."""

    def __init__(self, buildings: Sequence[BuildingRecord], fixed: int, placed_to: int) -> None:
        self.buildings = buildings
        self.fixed = fixed
        self.placed_to = placed_to
