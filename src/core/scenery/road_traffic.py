"""Phase 4 review: where streets cross each other (the centre line stops there, and a street
meeting another goes on under it).

The memos are kept as one-entry memos by identity (`_LineCache`,
`_IndexCache`): the same answers, since the values are pure functions of their list.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Sequence  # noqa: E402

from core.scenery.road_types import Road  # noqa: E402

__pragma__("noskip")

INFINITY = float("Infinity")

# Z length of the buckets of a `StreetIndex`.
BUCKET = 32
# Margin the buckets are widened by around each street: queries reaching further scan them all.
BUCKET_REACH = 1
# How near a street must be to another for them to meet (`meeting_width`).
MEETING_REACH = 0.5


class StreetLine:
    """A straight street, from its first to its last point."""

    def __init__(self, road: int, ax: float, az: float, bx: float, bz: float, width: float) -> None:
        self.road = road
        """The number of the road (its index)."""
        self.ax = ax
        self.az = az
        self.bx = bx
        self.bz = bz
        self.width = width


def street_lines(roads: Sequence[Road]) -> list[StreetLine]:
    """The streets of `roads` as straight lines (streets are straight, see `street_runs`)."""
    lines: list[StreetLine] = []
    for road in roads:
        if road.kind != "street" or len(road.points) == 0:
            continue
        a = road.points[0]
        b = road.points[len(road.points) - 1]
        lines.append(StreetLine(road.index, a.x, a.z, b.x, b.z, road.width))
    return lines


class _LineCache:
    """The street lines of the last list of roads asked for (see the module doc)."""

    def __init__(self) -> None:
        self._roads: Sequence[Road] | None = None
        self._lines: list[StreetLine] = []

    def get(self, roads: Sequence[Road]) -> list[StreetLine]:
        if self._roads is None or self._roads is not roads:
            self._lines = street_lines(roads)
            self._roads = roads
        return self._lines


_LINE_CACHE = _LineCache()


def cached_street_lines(roads: Sequence[Road]) -> list[StreetLine]:
    """`street_lines` of `roads`, made once per list of roads (P13-R04)."""
    return _LINE_CACHE.get(roads)


def road_z_span(road: Road) -> tuple[float, float]:
    """The lowest and highest Z of the points of `road` (P13-R04)."""
    low = INFINITY
    high = -INFINITY
    for p in road.points:
        low = min(low, p.z)
        high = max(high, p.z)
    return low, high


def _distance(line: StreetLine, x: float, z: float) -> float:
    dx = line.bx - line.ax
    dz = line.bz - line.az
    denominator = dx * dx + dz * dz
    if not denominator:
        denominator = 1
    t = max(0, min(1, ((x - line.ax) * dx + (z - line.az) * dz) / denominator))
    return math.hypot(line.ax + t * dx - x, line.az + t * dz - z)


class StreetIndex:
    """The streets of a list of lines by bands of Z (P13-R04): each band holds the streets within
    `width / 2 + BUCKET_REACH` of it, so a point only checks the streets near it."""

    def __init__(self, lines: Sequence[StreetLine]) -> None:
        self._bands: dict[str, list[StreetLine]] = {}
        for line in lines:
            reach = line.width / 2 + BUCKET_REACH
            first = math.floor((min(line.az, line.bz) - reach) / BUCKET)
            last = math.floor((max(line.az, line.bz) + reach) / BUCKET)
            for band in range(first, last + 1):
                k = str(band)
                if k in self._bands:
                    self._bands[k].append(line)
                else:
                    self._bands[k] = [line]

    def near(self, z: float) -> Sequence[StreetLine]:
        return self._bands.get(str(math.floor(z / BUCKET)), [])


class _IndexCache:
    """The index of the last list of lines asked for (see the module doc)."""

    def __init__(self) -> None:
        self._lines: Sequence[StreetLine] | None = None
        self._index: StreetIndex | None = None

    def get(self, lines: Sequence[StreetLine]) -> StreetIndex:
        if self._index is None or self._lines is not lines:
            self._index = StreetIndex(lines)
            self._lines = lines
        return self._index


_INDEX_CACHE = _IndexCache()


def _lines_near(lines: Sequence[StreetLine], z: float, margin: float) -> Sequence[StreetLine]:
    """The lines that may be within `margin` of the edge of a street at (_, z): those of its band
    when `margin` is within the bands' reach (the same answers as all of them, faster), all of them
    otherwise. The index of `lines` is built on the first query and kept with them."""
    if margin > BUCKET_REACH:
        return lines
    return _INDEX_CACHE.get(lines).near(z)


def in_crossing(
    lines: Sequence[StreetLine],
    road: int,
    x: float,
    z: float,
    margin: float,
) -> bool:
    """Whether (x, z) of street `road` is within `margin` of the edge of another street."""
    for line in _lines_near(lines, z, margin):
        if line.road != road and _distance(line, x, z) < line.width / 2 + margin:
            return True
    return False


def meeting_width(
    lines: Sequence[StreetLine],
    road: int,
    x: float,
    z: float,
) -> float | None:
    """Width of the widest other street that (x, z) of street `road` lies on, if any."""
    widest: float | None = None
    for line in _lines_near(lines, z, MEETING_REACH):
        if line.road != road and _distance(line, x, z) < MEETING_REACH:
            widest = max(widest if widest is not None else 0, line.width)
    return widest
