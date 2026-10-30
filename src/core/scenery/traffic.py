"""Phase 4 review: cars driving along the streets and main roads (not the paths), right-hand
traffic, in one lane each way (two on 2×2 roads). All the cars of one lane drive at the same speed,
so they never catch up with each other. A car that reaches the end of its road goes round to its
start, hidden near both ends: streets end in the crossing street, main roads off the screen. Ported
from `core/scenery/traffic.ts`.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402

from core.scenery.scenery_level import CarRules  # noqa: E402

__pragma__("noskip")

from core.math.noise import hash_2d  # noqa: E402
from core.scenery.ground_boxes import GroundArea, PropPlacement  # noqa: E402
from core.scenery.road_types import Road  # noqa: E402

# `%` keeps JavaScript's sign rule, as in the TypeScript (see `_distance_along`).
__pragma__("jsmod")

# Z span of a bucket of the roads with cars (`Traffic._buckets`).
BUCKET = 256
HALF = 0.5
INFINITY_VALUE = float("Infinity")


def _bucket_of(z: float) -> int:
    return math.floor(z / BUCKET)


class Track:
    """A road as cars follow it: its points, their distance along it, and the road surface height
    there, worked out when a car is first placed on it."""

    def __init__(
        self,
        road: Road,
        along: list[float],
        length: float,
        z_min: float,
        z_max: float,
    ) -> None:
        self.road = road
        self.along = along
        self.heights: list[float] | None = None
        self.length_ = length
        self.z_min = z_min
        """Z range of the road, to skip the cars of roads out of view."""
        self.z_max = z_max


class Car:
    """A car on a track."""

    def __init__(
        self,
        kind: str,
        track: Track,
        side: int,
        offset: float,
        start: float,
        speed: float,
    ) -> None:
        self.kind = kind
        self.track = track
        self.side = side
        """1 on the right of the road's direction (driving along it), -1 on the left."""
        self.offset = offset
        """Distance from the centre line."""
        self.start = start
        """Distance along the road at time 0."""
        self.speed = speed


def _track_of(road: Road) -> Track:
    along = [0.0]
    points = road.points
    for i in range(len(points)):
        if i + 1 < len(points):
            p = points[i]
            nxt = points[i + 1]
            along.append(along[i] + math.hypot(nxt.x - p.x, nxt.z - p.z))
    zs = [p.z for p in points]
    z_min = min(zs) - road.width
    z_max = max(zs) + road.width
    length = along[len(along) - 1] if len(along) > 0 else 0
    return Track(road, along, length, z_min, z_max)


def _segment_at(track: Track, s: float) -> int:
    """Index of the segment of `track` that contains distance `s` (binary search)."""
    lo = 0
    hi = len(track.along) - 2
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if track.along[mid] <= s:
            lo = mid
        else:
            hi = mid - 1
    return lo


class _TrackEntry:
    """A road with cars, and its cars."""

    def __init__(self, track: Track, cars: list[Car]) -> None:
        self.track = track
        self.cars = cars


class Traffic:
    """The cars of `rules` on all the streets and main roads of a level, and where they are. The
    roads with cars are indexed by the buckets of Z they span, so finding the cars in an area only
    looks at the roads near it."""

    def __init__(
        self,
        roads: Sequence[Road],
        height: Callable[[float, float], float],
        rules: CarRules,
        seed: int,
    ) -> None:
        self._height = height
        self._rules = rules
        self._seed = seed
        self._tracks: list[_TrackEntry] = []
        """The roads with cars, in the order of the level's roads, each with its cars."""
        self._buckets: dict[str, list[int]] = {}
        """Indices in `_tracks` of the roads that span each bucket, by bucket."""
        self._lowest = INFINITY_VALUE
        self._highest = -INFINITY_VALUE
        self._count = 0
        self.add(roads)

    def add(self, roads: Sequence[Road]) -> None:
        """Adds the cars of `roads` (e.g. the runout's, which come later)."""
        for road in roads:
            if road.kind == "cross" or len(road.points) < 2:  # noqa: PLR2004 (a road needs 2 points)
                continue
            track = _track_of(road)
            cars: list[Car] = []
            for i in range(len(road.points)):
                car = self._car_at(track, i, self._seed)
                if car is not None:
                    cars.append(car)
            if len(cars) == 0:
                continue
            index = len(self._tracks)
            self._tracks.append(_TrackEntry(track, cars))
            first = _bucket_of(track.z_min)
            last = _bucket_of(track.z_max)
            for b in range(first, last + 1):
                k = str(b)
                if k in self._buckets:
                    self._buckets[k].append(index)
                else:
                    self._buckets[k] = [index]
            self._lowest = min(self._lowest, first)
            self._highest = max(self._highest, last)
            self._count += len(cars)

    @property
    def count(self) -> int:
        """Number of cars on the level."""
        return self._count

    def _roadway(self, road: Road) -> float:
        """Width of the part of `road` cars drive on: P15-R11, streets without their sidewalks."""
        if road.kind == "street":
            sidewalk = self._rules.sidewalk if self._rules.sidewalk is not None else 0
            return road.width - 2 * sidewalk
        return road.width

    def _car_at(self, track: Track, i: int, seed: int) -> Car | None:
        """The car that starts at point `i` of a road, if any: one chance per point."""
        road = track.road

        def r(draw: int) -> float:
            return hash_2d(road.index * 7 + draw, i, seed * 13 + 5)

        kinds = self._rules.kinds
        index = math.floor(r(2) * len(kinds))
        kind = kinds[index] if index < len(kinds) else None
        if r(0) >= self._rules.density or kind is None:
            return None
        side = 1 if r(1) < HALF else -1
        lane = math.floor(r(3) * road.lanes)
        # One speed per lane of the road, so cars of a lane keep their distance.
        lr = hash_2d(road.index, side * 3 + lane, seed * 17 + 9)
        slow = self._rules.speed[0]
        fast = self._rules.speed[1]
        return Car(
            kind,
            track,
            side,
            (self._roadway(road) / (2 * road.lanes)) * (lane + 0.5),
            track.along[i] if i < len(track.along) else 0,
            slow + (fast - slow) * lr,
        )

    def at(self, time: float, area: GroundArea) -> list[PropPlacement]:
        """The cars in `area` at `time` (seconds), facing the way they drive, in road order."""
        out: list[PropPlacement] = []
        for index in self._tracks_in(area):
            for car in self._tracks[index].cars:
                p = self._place(car, time)
                if (
                    p is not None
                    and p.x >= area.x_min
                    and p.x < area.x_max
                    and p.z >= area.z_min
                    and p.z < area.z_max
                ):
                    out.append(p)
        return out

    def _tracks_in(self, area: GroundArea) -> list[int]:
        """Indices of the roads with cars whose Z range meets `area`, in order."""
        # Within the buckets that have roads (the area may be endless).
        first = max(_bucket_of(area.z_min), self._lowest)
        last = min(_bucket_of(area.z_max), self._highest)
        found: list[int] = []
        b = first
        while b <= last:
            for index in self._buckets.get(str(b), []):
                track = self._tracks[index].track
                # Once per road: in the first bucket of the area it spans.
                if max(_bucket_of(track.z_min), first) != b:
                    continue
                if track.z_max >= area.z_min and track.z_min < area.z_max:
                    found.append(index)
            b += 1
        return sorted(found)

    def _distance(self, car: Car, time: float) -> float | None:
        """How far along its road `car` is at `time`; None near the ends, where it is hidden."""
        length = car.track.length_
        s = ((car.start + car.side * car.speed * time) % length + length) % length
        # Hidden near the ends, where it turns into the crossing street or leaves the screen.
        if s < self._rules.length_ or s > length - self._rules.length_:
            return None
        return s

    def _heights_of(self, track: Track) -> list[float]:
        """The road surface heights at the points of `track`, worked out on first use."""
        if track.heights is None:
            track.heights = [self._height(p.x, p.z) + self._rules.lift for p in track.road.points]
        return track.heights

    def _place(self, car: Car, time: float) -> PropPlacement | None:
        track = car.track
        side = car.side
        s = self._distance(car, time)
        if s is None:
            return None
        i = _segment_at(track, s)
        points = track.road.points
        if i + 1 >= len(points):
            return None
        a = points[i]
        b = points[i + 1]
        s0 = track.along[i] if i < len(track.along) else 0
        s1 = track.along[i + 1] if i + 1 < len(track.along) else 0
        if s1 <= s0:
            return None
        t = (s - s0) / (s1 - s0)
        dx = (b.x - a.x) / (s1 - s0)
        dz = (b.z - a.z) / (s1 - s0)
        heights = self._heights_of(track)
        h0 = heights[i] if i < len(heights) else 0
        h1 = heights[i + 1] if i + 1 < len(heights) else 0
        return PropPlacement(
            car.kind,
            a.x + (b.x - a.x) * t + dz * side * car.offset,
            h0 + (h1 - h0) * t,
            a.z + (b.z - a.z) * t - dx * side * car.offset,
            math.atan2(dx, dz) + (0 if side > 0 else math.pi),
            self._rules.scale,
        )
