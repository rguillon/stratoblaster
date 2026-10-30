"""Centre and lane lines of the roads (phase 4 review): a yellow line along the middle of the
streets (stopping where they cross) and of the main roads (dashed); on wider roads (2x2 to 4x4), a
double yellow line and white dashed lines between the lanes. Painted just above the road surface.

Ported from `render/scenery/road-lines.ts`.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.scenery.road_traffic import cached_street_lines, in_crossing, road_z_span

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402

from core.scenery.road_traffic import StreetLine  # noqa: E402
from core.scenery.road_types import Road, RoadPoint  # noqa: E402
from render.geometry.gradient_shapes import ColoredGeometry  # noqa: E402
from render.scenery.terrain_geometry import HeightSource  # noqa: E402

Rgb = tuple[float, float, float]
Point = tuple[float, float]
__pragma__("noskip")

# Lines are drawn in pieces this long, so they follow the ground and stop cleanly.
PIECE = 2

# Ground heights under a line that differ from the straight line between its ends by at most this
# are one flat quad (reviewer, 2026-10-28: far fewer quads on flat cities).
FLAT = 0.02


def _hypot(a: float, b: float) -> float:
    """`Math.hypot(a, b)`: JavaScript's rounding, not `math.hypot`."""
    __pragma__("js", "{}", "return Math.hypot(a, b);")
    return 0


class CentreLineLook:
    """How the road markings are painted."""

    def __init__(
        self,
        color: Rgb,
        lane_color: Rgb,
        width: float,
        dash: float,
        lift: float,
    ) -> None:
        self.color = color
        """Colour of the lines between the lanes of 2x2 roads."""
        self.laneColor = lane_color
        self.width = width
        """Length of the dashes, and of the gaps between them."""
        self.dash = dash
        """Height above the road surface."""
        self.lift = lift


class Painter:
    """What the lines are painted into: the geometry, the ground, the look and the road's lift."""

    def __init__(
        self,
        geo: ColoredGeometry,
        ground: HeightSource,
        look: CentreLineLook,
        road_lift: float,
    ) -> None:
        self.geo = geo
        self.ground = ground
        self.look = look
        """Height of the road surface above the ground."""
        self.road_lift = road_lift


class Stripe:
    """A line along a road: its offset from the centre line, its colour, and if it is dashed."""

    def __init__(self, offset: float, color: Rgb, dashed: bool) -> None:
        self.offset = offset
        self.color = color
        self.dashed = dashed


def _stripes(road: Road, look: CentreLineLook) -> list[Stripe]:
    """The lines painted on `road`."""
    if road.lanes == 1:
        return [Stripe(0, look.color, road.kind == "main")]
    lane = road.width / (2 * road.lanes)
    # Between the lanes of each side, `lane` apart from the middle.
    between: list[Stripe] = []
    for i in range(road.lanes - 1):
        offset = (i + 1) * lane
        between.append(Stripe(-offset, look.laneColor, True))
        between.append(Stripe(offset, look.laneColor, True))
    out = [Stripe(-look.width, look.color, False), Stripe(look.width, look.color, False)]
    out.extend(between)
    return out


def _quad(
    paint: Painter,
    stripe: Stripe,
    a: Point,
    b: Point,
    ha: float,
    hb: float,
) -> None:
    """One flat quad of `stripe` from `a` to `b` of the centre line, at heights ha, hb."""
    geo = paint.geo
    look = paint.look
    ax, az = a
    bx, bz = b
    length = _hypot(bx - ax, bz - az)
    if length == 0:
        length = 1
    ux = (bz - az) / length
    uz = -(bx - ax) / length
    nx = ux * (look.width / 2)
    nz = uz * (look.width / 2)
    sx = ux * stripe.offset
    sz = uz * stripe.offset
    base = len(geo.positions) // 3
    lift = paint.road_lift + look.lift
    corners = [
        (ax + sx - nx, az + sz - nz, ha),
        (ax + sx + nx, az + sz + nz, ha),
        (bx + sx - nx, bz + sz - nz, hb),
        (bx + sx + nx, bz + sz + nz, hb),
    ]
    for x, z, h in corners:
        geo.positions.extend([x, h + lift, z])
        geo.colors.extend([stripe.color[0], stripe.color[1], stripe.color[2], 1])
    # Front faces up, as the road ribbons.
    geo.indices.extend([base, base + 1, base + 2, base + 1, base + 3, base + 2])


def _height_under(paint: Painter, stripe: Stripe, p: Point, d: Point) -> float:
    """Ground height under `stripe` at the centre-line point `p` of a piece going along `d`."""
    x, z = p
    dx, dz = d
    return paint.ground.height(x + dz * stripe.offset, z - dx * stripe.offset)


def _straight(heights: list[float], frm: int, to: int) -> bool:
    """Whether the heights between `frm` and `to` lie on the line between theirs."""
    a = heights[frm]
    b = heights[to]
    for k in range(frm + 1, to):
        expected = a + ((b - a) * (k - frm)) / (to - frm)
        if abs(heights[k] - expected) > FLAT:
            return False
    return True


def _paint_run(paint: Painter, stripe: Stripe, at: list[Point], d: Point) -> None:
    """Paints `stripe` over the pieces between the centre-line points `at`, one quad for as many
    pieces in a row as the ground under them stays straight."""
    heights = [_height_under(paint, stripe, p, d) for p in at]
    frm = 0
    while frm < len(at) - 1:
        to = frm + 1
        while to + 1 < len(at) and _straight(heights, frm, to + 1):
            to += 1
        _quad(paint, stripe, at[frm], at[to], heights[frm], heights[to])
        frm = to


def _crossed(
    road: Road,
    lines: list[StreetLine],
    at: Callable[[int], Point],
    pieces: int,
) -> list[bool]:
    """Whether each of the `pieces` pieces of a segment of `road` touches a street crossing it."""
    ends: list[bool] = []
    for k in range(pieces + 1):
        p = at(k)
        ends.append(road.kind == "street" and in_crossing(lines, road.index, p[0], p[1], 0.5))
    return [ends[k] or ends[k + 1] for k in range(pieces)]


def _paint_segment(
    paint: Painter,
    road: Road,
    a: RoadPoint,
    b: RoadPoint,
    lines: list[StreetLine],
    start: float,
) -> None:
    """Paints the lines of the segment from `a` to `b` of `road`, `start` along it."""
    length = _hypot(b.x - a.x, b.z - a.z)
    pieces = max(1, math.floor(length / PIECE + 0.5))
    unit = length if length != 0 else 1
    d: Point = ((b.x - a.x) / unit, (b.z - a.z) / unit)

    def at(k: int) -> Point:
        return (a.x + ((b.x - a.x) * k) / pieces, a.z + ((b.z - a.z) * k) / pieces)

    blocked = _crossed(road, lines, at, pieces)

    # Dashes and gaps by the distance along the road.
    def gap(k: int) -> bool:
        return math.floor((start + (length * (k + 0.5)) / pieces) / paint.look.dash) % 2 == 1

    for stripe in _stripes(road, paint.look):
        run: list[Point] = []
        for k in range(pieces + 1):
            if k < pieces and not blocked[k] and not (stripe.dashed and gap(k)):
                run.append(at(k))
            elif len(run) > 0:
                tail = list(run)
                tail.append(at(k))
                _paint_run(paint, stripe, tail, d)
                run = []


def paint_centre_lines(
    paint: Painter,
    roads: list[Road],
    z_min: float,
    z_max: float,
) -> None:
    """Appends to `paint.geo` the lines of the streets and main roads whose segments start in
    [z_min, z_max), so neighbouring terrain chunks paint each segment once."""
    lines = cached_street_lines(roads)
    for road in roads:
        if road.kind == "cross":
            continue
        # P13-R04: a road with no point in the range has no segment starting there.
        z_low, z_high = road_z_span(road)
        if z_high < z_min or z_low >= z_max:
            continue
        along = 0.0
        for i, a in enumerate(road.points):
            if i + 1 >= len(road.points):
                break
            b = road.points[i + 1]
            if a.z >= z_min and a.z < z_max:
                _paint_segment(paint, road, a, b, lines, along)
            along += _hypot(b.x - a.x, b.z - a.z)
