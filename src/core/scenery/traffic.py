# Copyright (c) 2026 Renaud Guillon
"""Phase 4 review (GFX-CAR-06).

Cars driving along the streets and main roads (not the paths), right-hand traffic, in one lane each
way (two on 2x2 roads). All the cars of one lane drive at the same speed, so they never catch up
with each other. A car that reaches the end of its road goes round to its start, hidden near both
ends: streets end in the crossing street, main roads off the screen.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.math.noise import hash_2d
from core.scenery.ground_boxes import GroundArea, PropPlacement
from core.scenery.road_types import Road

# isort: split
# __pragma__ ("skip")
from collections.abc import Callable, Sequence
from typing import Any

from core.scenery.scenery_level import CarRules

# __pragma__ ("noskip")

# `%` keeps JavaScript's sign rule.
__pragma__("jsmod")


# Z span of a bucket of the roads with cars (`Traffic._buckets`).
BUCKET = 256
# How far past the view (Z, each way) a road's cars are looked for, so the look is kept while the
# view scrolls that far (`_look_between`).
WINDOW_PAD = 48
HALF = 0.5
INFINITY_VALUE = float("Infinity")


def _bucket_of(z: float) -> int:
    return math.floor(z / BUCKET)


class Track:
    """A road as cars follow it.

    Its points, their distance along it, and the road surface height there, worked out when a car is
    first placed on it.
    """

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
        kind_index: int = 0,
    ) -> None:
        self.kind = kind
        self.kind_index = kind_index
        """Where `kind` is in the rules' kinds."""
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
    return _segment(track.along, len(track.along) - 2, s)


def _segment(along: list[float], last: int, s: float) -> int:
    """Index (at most `last`) of the segment that contains distance `s` of the distances `along`."""
    lo = 0
    hi = last
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if along[mid] <= s:
            lo = mid
        else:
            hi = mid - 1
    return lo


# Numbers per car in `CarsInView.values`.
CAR_VALUES = 5


class CarsInView:
    """The cars in an area at a time, as numbers in one list (`Traffic.fill`, D-422).

    `CAR_VALUES` per car, in road order: the index of its kind in the rules' kinds, its x, y
    (the road's surface) and z, and its turn around the vertical axis (radians). The list is kept
    from one frame to the next, so placing the cars makes no object.
    """

    def __init__(self) -> None:
        self.values: list[Any] = []
        self.count = 0


class _TrackEntry:
    """A road with cars, and its cars."""

    def __init__(self, track: Track, cars: list[Car]) -> None:
        self.track = track
        self.cars = cars
        reach = 0.0
        for car in cars:
            if car.offset > reach:
                reach = car.offset
        self.reach = reach
        """The farthest a car is from the road's centre line."""
        # D-422: the distances along the road at which a car may be in the Z range `from_z` to
        # `to_z` (none when `s_first` > `s_last`), worked out again when the view leaves the range.
        self.from_z = INFINITY_VALUE
        self.to_z = -INFINITY_VALUE
        self.s_first = 0.0
        self.s_last = 0.0


def _look_between(entry: _TrackEntry, z_low: float, z_high: float, hide: float) -> None:
    """Work out where along its road a car of `entry` may be between `z_low` and `z_high`.

    From the first to the last of the road's segments that meet that Z range, `WINDOW_PAD` wider
    each way so the view can scroll before the next look, and never within `hide` of the road's
    ends. A car elsewhere along the road is on a segment wholly out of the range.
    """
    track = entry.track
    points = track.road.points
    entry.from_z = z_low - WINDOW_PAD
    entry.to_z = z_high + WINDOW_PAD
    first = -1
    last = -1
    for i in range(len(points) - 1):
        a = points[i].z
        b = points[i + 1].z
        if (a >= entry.from_z or b >= entry.from_z) and (a <= entry.to_z or b <= entry.to_z):
            if first < 0:
                first = i
            last = i
    if first < 0:
        entry.s_first = 1.0
        entry.s_last = 0.0
        return
    s_first = track.along[first]
    s_last = track.along[last + 1]
    entry.s_first = max(hide, s_first)
    far = track.length_ - hide
    entry.s_last = min(far, s_last)


class Traffic:
    """The cars of `rules` on all the streets and main roads of a level, and where they are.

    The roads with cars are indexed by the buckets of Z they span, so finding the cars in an area
    only looks at the roads near it (GFX-CAR-08, PERF-24).
    """

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
        """Add the cars of `roads` (e.g. the runout's, which come later)."""
        for road in roads:
            if road.kind == "cross" or len(road.points) < 2:
                continue
            track = _track_of(road)
            # A road of one point repeated has no length to drive along.
            if track.length_ <= 0:
                continue
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
        """Width of the part of `road` cars drive on (GFX-CAR-07).

        On streets, that is the road without its sidewalks.
        """
        if road.kind == "street":
            sidewalk = self._rules.sidewalk if self._rules.sidewalk is not None else 0
            return road.width - 2 * sidewalk
        return road.width

    def _car_at(self, track: Track, i: int, seed: int) -> Car | None:
        """Return the car that starts at point `i` of a road, if any: one chance per point."""
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
            index,
        )

    def at(self, time: float, area: GroundArea) -> list[PropPlacement]:
        """Return the cars in `area` at `time` (seconds), in road order.

        They face the way they drive. Each car is hidden near the ends of its road, where it turns
        into the crossing street or leaves the screen. The cars of `fill`, as placements.
        """
        cars = CarsInView()
        self.fill(time, area, cars)
        out: list[PropPlacement] = []
        kinds = self._rules.kinds
        scale = self._rules.scale
        values = cars.values
        for n in range(cars.count):
            at = n * CAR_VALUES
            out.append(
                PropPlacement(
                    kinds[values[at]],
                    values[at + 1],
                    values[at + 2],
                    values[at + 3],
                    values[at + 4],
                    scale,
                )
            )
        return out

    def fill(self, time: float, area: GroundArea, cars: CarsInView) -> None:
        """Put the cars in `area` at `time` (seconds) into `cars`, in road order.

        D-412: worked out in one loop, a car's height only once it is in `area`. D-422: as
        numbers written into the list `cars` keeps, not a placement made for each car, each frame.
        """
        values = cars.values
        values.clear()
        count = 0
        hide = self._rules.length_
        x_min = area.x_min
        x_max = area.x_max
        z_min = area.z_min
        z_max = area.z_max
        for index in self._tracks_in(area):
            entry = self._tracks[index]
            track = entry.track
            length = track.length_
            points = track.road.points
            along = track.along
            heights: list[float] | None = None
            # Only the cars on the stretch of the road near the area's Z range can be in it.
            z_low = z_min - entry.reach
            z_high = z_max + entry.reach
            if z_low < entry.from_z or z_high > entry.to_z:
                _look_between(entry, z_low, z_high, hide)
            s_first = entry.s_first
            s_last = entry.s_last
            if s_first > s_last:
                continue
            last = len(along) - 2
            for car in entry.cars:
                side = car.side
                s = ((car.start + side * car.speed * time) % length + length) % length
                # Hidden near the ends of its road, and out of the area on the rest of it.
                if s < s_first or s > s_last:
                    continue
                # A segment that ends after `s` (< length): s0 <= s < s1.
                i = _segment(along, last, s)
                a = points[i]
                b = points[i + 1]
                s0 = along[i]
                s1 = along[i + 1]
                t = (s - s0) / (s1 - s0)
                dx = (b.x - a.x) / (s1 - s0)
                dz = (b.z - a.z) / (s1 - s0)
                x = a.x + (b.x - a.x) * t + dz * side * car.offset
                z = a.z + (b.z - a.z) * t - dx * side * car.offset
                if x < x_min or x >= x_max or z < z_min or z >= z_max:
                    continue
                if heights is None:
                    heights = self._heights_of(track)
                # One height per point of the road: `i + 1` is always one of them.
                h0 = heights[i]
                values.append(car.kind_index)
                values.append(x)
                values.append(h0 + (heights[i + 1] - h0) * t)
                values.append(z)
                values.append(math.atan2(dx, dz) + (0 if side > 0 else math.pi))
                count += 1
        cars.count = count

    def _tracks_in(self, area: GroundArea) -> list[int]:
        """Return the indices of the roads with cars whose Z range meets `area`, in order."""
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

    def _heights_of(self, track: Track) -> list[float]:
        """Return the road surface heights at the points of `track` (PERF-27).

        They are worked out on first use.
        """
        if track.heights is None:
            track.heights = [self._height(p.x, p.z) + self._rules.lift for p in track.road.points]
        return track.heights
