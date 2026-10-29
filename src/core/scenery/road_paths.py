"""Paths from points of the main roads to past the screen edge, every `cross_spacing` (P04-R07).
Each one tries both directions and a few bends, and is dropped if none stays on buildable ground
(and, without crossings, clear of the roads and the paths laid before it). Ported from
`core/scenery/road-paths.ts`."""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402

from core.math.rng import Random  # noqa: E402
from core.scenery.districts import ZRange  # noqa: E402
from core.scenery.road_segments import Nearest  # noqa: E402
from core.scenery.road_types import Road  # noqa: E402
from core.scenery.scenery_level import RoadRules  # noqa: E402

__pragma__("noskip")

from core.math.noise import smoothstep  # noqa: E402
from core.math.rng import random_in  # noqa: E402
from core.scenery.road_types import RoadPoint  # noqa: E402

INFINITY = float("Infinity")

# A path starts at most this many points from where it was asked for along its road.
PATH_START_SLACK = 4
# Chance of the other direction (a coin toss).
HALF = 0.5
# Directions (same / other side) and bends (share of the drawn bend) a path tries in turn.
PATH_TRIES = [
    (1, 1),
    (1, -1),
    (1, 0),
    (-1, 1),
    (-1, -1),
    (-1, 0),
]


class PathGround:
    """What laying the paths needs from the road network (TypeScript `PathGround`)."""

    def __init__(
        self,
        rules: RoadRules,
        span: ZRange,
        open_: Callable[[float, float], bool],
        nearest: Callable[[float, float, Callable[[Road], bool]], Nearest],
        lay: Callable[[list[RoadPoint]], None],
    ) -> None:
        self.rules = rules
        """The road rules of the level."""
        self.span = span
        """Z range covered by the roads."""
        self.open = open_
        """Whether a path may go at (`x`, `z`): buildable, out of the districts."""
        self.nearest = nearest
        """The edge of the nearest road `which` accepts, within about 64 units."""
        self.lay = lay
        """Adds a path to the network."""


class _Main:
    """A main road a path may start from, with the point it starts at."""

    def __init__(self, main: Road, p: RoadPoint) -> None:
        self.main = main
        self.p = p


def lay_paths(ground: PathGround, random: Random, mains: Sequence[Road]) -> None:
    """Paths from points of the main roads to past the screen edge, every `cross_spacing`."""
    rules = ground.rules
    cross_spacing = rules.cross_spacing
    cross_bend = rules.cross_bend
    offscreen_x = rules.offscreen_x
    step = rules.step
    if len(mains) == 0:
        return
    z_min = ground.span.z_min
    z_max = ground.span.z_max
    z = z_min + random_in(random, cross_spacing[0], cross_spacing[1])
    while z < z_max:
        # A point on screen near `z` of each main road piece that passes there; without crossings,
        # where it runs along the level (where a piece comes in from the side, a path would run on
        # top of it).
        near = step * PATH_START_SLACK
        starts: list[_Main] = []
        for main in mains:
            i = _find_index(main.points, z, offscreen_x)
            p = main.points[i] if 0 <= i < len(main.points) else None
            along = rules.no_crossings is None or _runs_along(main, i)
            if p is not None and p.z - z <= near and along:
                starts.append(_Main(main, p))
        pick = random()
        direction = -1 if random() < HALF else 1
        bend = random_in(random, -cross_bend, cross_bend)
        start = starts[math.floor(pick * len(starts))] if len(starts) > 0 else None
        if start is not None:
            path: list[RoadPoint] | None = None
            for d, b in PATH_TRIES:
                line = _path_through(
                    ground, _path_line(rules, start.p, d * direction, b * bend), start.main
                )
                if line is not None:
                    path = line
                    break
            if path is not None:
                ground.lay(path)
        z = z + random_in(random, cross_spacing[0], cross_spacing[1])


def _find_index(points: Sequence[RoadPoint], z: float, offscreen_x: float) -> int:
    """The index of the first point at or past `z` and on screen (-1 when there is none)."""
    for i, q in enumerate(points):
        if q.z >= z and abs(q.x) < offscreen_x:
            return i
    return -1


def _runs_along(road: Road, i: int) -> bool:
    """Whether `road` runs more along the level than across it at its point `i`."""
    points = road.points
    p = points[i] if 0 <= i < len(points) else None
    if i + 1 < len(points):
        q = points[i + 1]
    elif i - 1 >= 0 and i - 1 < len(points):
        q = points[i - 1]
    else:
        q = None
    if p is None or q is None:
        return True
    return abs(q.z - p.z) >= abs(q.x - p.x)


class _Walk:
    """A path checked point by point (`noCrossings`)."""

    def __init__(self, clear: float) -> None:
        self.clear = clear
        """How far from every road but the one it joins a path keeps."""
        self.left = False
        """Whether it is clear of its own road yet."""
        self.closing = INFINITY
        """Distance to the road it is running into, once near it."""


def _path_through(
    ground: PathGround, line: Sequence[RoadPoint], from_: Road
) -> list[RoadPoint] | None:
    """`line` if a path can go there from its road `from_`: on open ground and, without crossings,
    `gap` clear of every road and path, except where it ends on another main road or street (cut
    there). None if it cannot."""
    no_crossings = ground.rules.no_crossings
    if no_crossings is None:
        for p in line[1:]:
            if not ground.open(p.x, p.z):
                return None
        return list(line)
    walk = _Walk(ground.rules.cross_width / 2 + no_crossings.gap)
    for i in range(1, len(line)):
        verdict = _path_point(ground, walk, line[i], from_)
        if verdict == "blocked":
            return None
        if verdict == "end":
            return list(line[0 : i + 1])
    return list(line)


def _path_point(ground: PathGround, walk: _Walk, p: RoadPoint, from_: Road) -> str:
    """Whether a path goes on through `p`, ends there on another road, or is blocked: 'on', 'end'
    or 'blocked'."""
    if not ground.open(p.x, p.z):
        return "blocked"
    # Off its own road for good once clear of it.
    own = ground.nearest(p.x, p.z, lambda road: road is from_).distance
    if own >= walk.clear:
        walk.left = True
    elif walk.left:
        return "blocked"
    other = ground.nearest(p.x, p.z, lambda road: road is not from_)
    if other.distance >= walk.clear:
        return "on"
    # Near another road: only a main road or a street, which it must run straight into.
    if (other.road is not None and other.road.kind == "cross") or other.distance > walk.closing:
        return "blocked"
    if other.distance <= 0:
        return "end"
    walk.closing = other.distance
    return "on"


def _path_line(rules: RoadRules, start: RoadPoint, direction: int, bend: float) -> list[RoadPoint]:
    """A path from `start` to past the screen edge on the `direction` side, bending by `bend`."""
    step = rules.step
    count = math.ceil((rules.offscreen_x - direction * start.x) / step) + 1
    return [
        RoadPoint(
            start.x + direction * i * step,
            start.z + bend * math.sin((math.pi * i) / (2 * count)),
            _path_width(rules, i * step),
        )
        for i in range(count + 1)
    ]


def _path_width(rules: RoadRules, distance: float) -> float:
    """Width of a path `distance` from its junction: wide at the road, narrowing smoothly."""
    t = smoothstep(0, rules.junction.length_, distance)
    return rules.junction.width + (rules.cross_width - rules.junction.width) * t
