"""The segments of the roads, indexed by buckets for distance queries, and the building slots along
them (road network)."""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Callable  # noqa: E402

from core.scenery.road_types import Road  # noqa: E402

__pragma__("noskip")

from core.scenery.road_types import RoadSlot  # noqa: E402

INFINITY = float("Infinity")

# Bucket size of the segment index; distance queries see at least this far.
BUCKET = 64
# Key of the bucket (`i`, `j`) of a `SegmentIndex` (|j| stays far below a million).
BUCKET_KEY_STRIDE = 1000003


def _bucket_key(i: int, j: int) -> str:
    return str(i * BUCKET_KEY_STRIDE + j)


class Segment:
    """One straight piece of a road, with the road it belongs to."""

    def __init__(
        self, road: Road, ax: float, az: float, bx: float, bz: float, half_width: float
    ) -> None:
        self.road = road
        self.ax = ax
        self.az = az
        self.bx = bx
        self.bz = bz
        self.half_width = half_width


class Nearest:
    """The edge of the nearest road: its distance, and the road if there is one."""

    def __init__(self, distance: float, road: Road | None = None) -> None:
        self.distance = distance
        self.road = road


def segment_distance(x: float, z: float, s: Segment) -> float:
    """Distance from (`x`, `z`) to the centre line of `s`."""
    dx = s.bx - s.ax
    dz = s.bz - s.az
    length2 = dx * dx + dz * dz
    t = max(0, min(1, ((x - s.ax) * dx + (z - s.az) * dz) / length2)) if length2 > 0 else 0
    return math.hypot(x - (s.ax + t * dx), z - (s.az + t * dz))


class SegmentIndex:
    """The segments of roads, in buckets `BUCKET` wide by where their ends are."""

    def __init__(self) -> None:
        self._buckets: dict[str, list[Segment]] = {}
        self._reach = 0.0
        """Farthest a segment reaches from its nearer end: half its length, plus half its width."""

    def add(self, road: Road) -> None:
        points = road.points
        for i in range(len(points)):
            if i + 1 >= len(points):
                continue
            a = points[i]
            b = points[i + 1]
            half_width = max(a.width, b.width) / 2
            self._reach = max(self._reach, math.hypot(b.x - a.x, b.z - a.z) / 2 + half_width)
            segment = Segment(road, a.x, a.z, b.x, b.z, half_width)
            keys: list[str] = []
            for p in [a, b]:
                k = _bucket_key(math.floor(p.x / BUCKET), math.floor(p.z / BUCKET))
                if k not in keys:
                    keys.append(k)
            for k in keys:
                if k in self._buckets:
                    self._buckets[k].append(segment)
                else:
                    self._buckets[k] = [segment]

    def _segments_in(self, i: int, j: int) -> list[Segment]:
        return self._buckets.get(_bucket_key(i, j), [])

    def nearest(
        self,
        x: float,
        z: float,
        which: Callable[[Road], bool],
    ) -> Nearest:
        """The edge of the nearest road `which` accepts, within about `BUCKET` units."""
        bx = math.floor(x / BUCKET)
        bz = math.floor(z / BUCKET)
        distance = INFINITY
        road: Road | None = None
        for i in range(bx - 1, bx + 2):
            for j in range(bz - 1, bz + 2):
                for s in self._segments_in(i, j):
                    d = segment_distance(x, z, s) - s.half_width
                    if d < distance and which(s.road):
                        distance = d
                        road = s.road
        return Nearest(distance, road)

    def clear_of(self, x: float, z: float, clearance: float) -> bool:
        """Whether no road edge is closer than `clearance` to (`x`, `z`) among those `nearest`
        sees. Only the buckets a road in reach can be in are searched, up to the first road in
        reach."""
        around = clearance + self._reach
        if around > BUCKET:
            return self.nearest(x, z, lambda _road: True).distance >= clearance
        bx = math.floor(x / BUCKET)
        bz = math.floor(z / BUCKET)
        i0 = math.floor((x - around) / BUCKET)
        i1 = math.floor((x + around) / BUCKET)
        j0 = math.floor((z - around) / BUCKET)
        j1 = math.floor((z + around) / BUCKET)
        for i in range(max(i0, bx - 1), min(i1, bx + 1) + 1):
            for j in range(max(j0, bz - 1), min(j1, bz + 1) + 1):
                for s in self._segments_in(i, j):
                    if segment_distance(x, z, s) - s.half_width < clearance:
                        return False
        return True


def add_slots(road: Road, spacing: float, slots: list[RoadSlot]) -> None:
    """Adds to `slots` the slots every `spacing` along `road`, on both sides, numbered on from
    them."""
    travelled = spacing / 2
    points = road.points
    for i in range(len(points)):
        if i + 1 >= len(points):
            continue
        a = points[i]
        b = points[i + 1]
        length = math.hypot(b.x - a.x, b.z - a.z)
        if length == 0:
            continue
        tx = (b.x - a.x) / length
        tz = (b.z - a.z) / length
        while travelled < length:
            t = travelled / length
            x = a.x + (b.x - a.x) * t
            z = a.z + (b.z - a.z) * t
            index = len(slots)
            slots.append(RoadSlot(road, index, x, z, tz, -tx))
            slots.append(RoadSlot(road, index + 1, x, z, -tz, tx))
            travelled += spacing
        travelled -= length
