"""Road ribbons draped on the ground (phase 4 review, P04-R07): each road as one see-through
surface, its soft shoulders fading into the ground, cut on the terrain chunks.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.math.noise import hash_2d
from core.scenery.road_traffic import cached_street_lines, meeting_width, road_z_span
from core.scenery.road_types import RoadPoint
from render.geometry.gradient_shapes import ColoredGeometry
from render.scenery.road_lines import CentreLineLook, Painter, paint_centre_lines
from render.scenery.tile_road_geometry import TileRoadLook

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from core.scenery.road_traffic import StreetLine  # noqa: E402
from core.scenery.road_types import Road  # noqa: E402
from render.scenery.terrain_geometry import HeightSource  # noqa: E402

Rgb = tuple[float, float, float]
__pragma__("noskip")

# Offsets across a road (in half-widths) and opacity factors of its 4 vertex rows:
# (across, shoulder, opacity).
ROWS = [(-1, -1, 0), (-1, 0, 1), (1, 0, 1), (1, 1, 0)]

# The quad between rows 1 and 2: the even middle of a road, between its soft edges.
MIDDLE = 1


def _hypot(a: float, b: float) -> float:
    """`Math.hypot(a, b)`: JavaScript's rounding, not `math.hypot`."""
    __pragma__("js", "{}", "return Math.hypot(a, b);")
    return math.hypot(a, b)  # Only reached outside Transcrypt (CPython).


class RoadOpacity:
    """Opacity of the road surface (below 1, the ground texture shows through)."""

    def __init__(self, main: float, cross: float) -> None:
        self.main = main
        self.cross = cross


class RoadLook:
    """How roads are drawn on the ground."""

    def __init__(  # noqa: PLR0917
        self,
        main: Rgb,
        cross: Rgb,
        opacity: RoadOpacity,
        shoulder: float,
        street_shoulder: float,
        centre_line: CentreLineLook | None,
        wear: float,
        lift: float,
        tiles: TileRoadLook | None,
    ) -> None:
        """`main`: colour of the main roads; `cross`: colour of the paths. `shoulder`: width of the
        soft edge on each side, where the road fades into the ground. `streetShoulder`: narrower
        soft edge of the streets, so their crossings and corners stay clean. `centreLine`: the
        yellow line along the streets and main roads, if any. `wear`: how much (0..1) colour and
        opacity vary along a road, so it looks worn. `lift`: height of the road surface above the
        ground. `tiles` (phase 15): the road pieces of the districts laid on tiles."""
        self.main = main
        self.cross = cross
        self.opacity = opacity
        self.shoulder = shoulder
        self.streetShoulder = street_shoulder
        self.centreLine = centre_line
        self.wear = wear
        self.lift = lift
        self.tiles = tiles


def _runs(points: list[RoadPoint], z_min: float, z_max: float) -> list[list[RoadPoint]]:
    """Runs of consecutive points whose segments start inside [z_min, z_max)."""
    out: list[list[RoadPoint]] = []
    run: list[RoadPoint] = []
    for i, a in enumerate(points):
        b = points[i + 1] if i + 1 < len(points) else None
        if b is not None and a.z >= z_min and a.z < z_max:
            if len(run) == 0:
                run.append(a)
            run.append(b)
        elif len(run) > 0:
            out.append(run)
            run = []
    if len(run) > 0:
        out.append(run)
    return out


def _across(run: list[RoadPoint], i: int) -> tuple[float, float]:
    """Unit vector across the road at point `i` of a run (from the neighbouring points)."""
    a = run[max(0, i - 1)]
    b = run[min(len(run) - 1, i + 1)]
    if a is None or b is None:
        return (1, 0)
    length = _hypot(b.x - a.x, b.z - a.z)
    if length == 0:
        # Two equal points have no direction: as with a missing neighbour, the road runs along X.
        return (1, 0)
    return ((b.z - a.z) / length, -(b.x - a.x) / length)


def _ribbon_points(road: Road, lines: list[StreetLine]) -> list[RoadPoint]:
    """The points of a road; a street goes on past both ends by half the width of the street it
    meets there (its own if none), under it, so two streets meeting at a corner leave no notch and
    an avenue does not stick out past a narrower street (phase 4 review)."""
    points = road.points
    if road.kind != "street" or len(points) < 2:  # noqa: PLR2004
        return list(points)

    def past(end: RoadPoint, nxt: RoadPoint) -> RoadPoint:
        length = _hypot(end.x - nxt.x, end.z - nxt.z)
        if length == 0:
            length = 1
        widest = meeting_width(lines, road.index, end.x, end.z)
        width = widest if widest is not None else road.width
        k = width / 2 / length
        return RoadPoint(end.x + (end.x - nxt.x) * k, end.z + (end.z - nxt.z) * k, end.width)

    out = [past(points[0], points[1])]
    out.extend(points)
    out.append(past(points[len(points) - 1], points[len(points) - 2]))
    return out


def _worn(road: Road, p: RoadPoint, look: RoadLook) -> list[float]:
    """Colour and opacity of a point of a road, worn by a hash of its position (not streets)."""
    # Streets are opaque and even, so where they cross or meet they merge without a seam.
    if road.kind == "street":
        return [look.main[0], look.main[1], look.main[2], 1]
    rgb = look.main if road.kind == "main" else look.cross
    opacity = look.opacity.main if road.kind == "main" else look.opacity.cross
    shade = (
        1 + (hash_2d(math.floor(p.x + 0.5), math.floor(p.z + 0.5), road.index) - 0.5) * look.wear
    )
    fade = 1 - hash_2d(math.floor(p.z + 0.5), math.floor(p.x + 0.5), road.index + 1) * look.wear
    return [rgb[0] * shade, rgb[1] * shade, rgb[2] * shade, opacity * fade]


def _quad(to: ColoredGeometry, source: ColoredGeometry, corners: list[int]) -> None:
    """Copies the quad of `source`'s vertices `corners` into `to`, faces as the ribbons'."""
    base = len(to.positions) // 3
    for v in corners:
        to.positions.extend(source.positions[v * 3 : v * 3 + 3])
        to.colors.extend(source.colors[v * 4 : v * 4 + 4])
    to.indices.extend([base, base + 1, base + 2, base + 1, base + 3, base + 2])


def build_road_geometry(  # noqa: C901
    roads: list[Road],
    ground: HeightSource,
    z_min: float,
    z_max: float,
    look: RoadLook,
    middles: ColoredGeometry | None = None,
) -> ColoredGeometry:
    """Ribbons draped on the ground along the segments of `roads` that start in [z_min, z_max)
    (P04-R07), so neighbouring terrain chunks draw each segment once. The ribbon follows the width
    of each point (paths widen at their junction). Each ribbon has a slightly see-through, worn
    surface and soft shoulders that fade to nothing on both sides, so the road blends into the
    ground (phase 4 review). Streets and main roads get a yellow centre line. With `middles`, the
    even middles of the streets go there instead, to be drawn opaque (reviewer, 2026-10-28), their
    soft edges staying with the rest."""
    geo = ColoredGeometry()
    rows = len(ROWS)
    lines = cached_street_lines(roads)
    # How far past its points a street's ribbon may reach (see `_ribbon_points`).
    reach = 0.0
    for line in lines:
        reach = max(reach, line.width)
    reach = reach / 2 + 1
    for road in roads:
        # P13-R04: a road with no point near the chunk has no segment in it.
        z_low, z_high = road_z_span(road)
        if z_high < z_min - reach or z_low >= z_max + reach:
            continue
        shoulder = look.streetShoulder if road.kind == "street" else look.shoulder
        middle = middles if road.kind == "street" else None
        for run in _runs(_ribbon_points(road, lines), z_min, z_max):
            base = len(geo.positions) // 3
            for i, p in enumerate(run):
                nx, nz = _across(run, i)
                colour = _worn(road, p, look)
                for across, row_shoulder, row_opacity in ROWS:
                    offset = (across * p.width) / 2 + row_shoulder * shoulder
                    x = p.x + nx * offset
                    z = p.z + nz * offset
                    geo.positions.extend([x, ground.height(x, z) + look.lift, z])
                    geo.colors.extend([colour[0], colour[1], colour[2], colour[3] * row_opacity])
                if i == 0:
                    continue
                for k in range(rows - 1):
                    l0 = base + rows * (i - 1) + k
                    r0 = base + rows * (i - 1) + k + 1
                    l1 = base + rows * i + k
                    r1 = base + rows * i + k + 1
                    # Front faces up (Babylon: normal = (c - a) x (b - a)).
                    if middle is not None and k == MIDDLE:
                        _quad(middle, geo, [l0, r0, l1, r1])
                    else:
                        geo.indices.extend([l0, r0, l1, r0, r1, l1])
    # Painted after the ribbons, so they draw over them.
    if look.centreLine != None:  # noqa: E711 (optional record field: undefined when absent)
        paint_centre_lines(
            Painter(geo, ground, look.centreLine, look.lift),
            roads,
            z_min,
            z_max,
        )
    return geo
