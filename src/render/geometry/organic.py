"""Builders of living shapes for low-poly, flat-shaded models (ported from
`render/geometry/organic.ts`): bodies of segments, shells, ribs, tendrils, membrane wings,
organs, veins and armour plates.

Game-agnostic: they draw into a `SolidBuilder` and know nothing of what they are used for.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.geometry.outline import hypot3, reversed_copy
from render.geometry.solids import LoftOptions, Placement, SolidBuilder, place_at

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402

from render.geometry.outline import OutlinePoint  # noqa: E402

Rgb = list[float]
Vec3 = list[float]
SectionPoint = list[float]

__pragma__("noskip")

# A rounded cross-section (counter-clockwise seen from the nose): a soft, swollen body.
ROUND_SECTION = [
    [0.4, 0.0],
    [0.9, 0.25],
    [1.0, 0.55],
    [0.65, 0.9],
    [0.0, 1.0],
    [-0.65, 0.9],
    [-1.0, 0.55],
    [-0.9, 0.25],
    [-0.4, 0.0],
]

# A shell's cross-section: low flanks rising to a ridge along its back.
SHELL_SECTION = [
    [0.7, 0.0],
    [1.0, 0.2],
    [0.75, 0.6],
    [0.3, 0.88],
    [0.0, 1.0],
    [-0.3, 0.88],
    [-0.75, 0.6],
    [-1.0, 0.2],
    [-0.7, 0.0],
]


def _swollen(t: float) -> float:
    return 0.35 + 0.65 * math.sin(math.pi * t)


class SegmentedBody:
    """A body of segments along Z, from its tail to its nose.

    `pinch` (how much thinner it is between two segments, 0 to 1) and `girth` (a function of t,
    from tail 0 to nose 1; a swollen middle by default) may be None for the defaults.
    `closed` is `[tail, nose]` (both closed to a point by default).
    """

    def __init__(  # noqa: PLR0913, PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        tail: float,
        nose: float,
        segments: int,
        width: float,
        bottom: float,
        top: float,
        pinch: float | None = None,
        girth: Callable[[float], float] | None = None,
        closed: list[bool] | None = None,
    ) -> None:
        # Z of the tail and nose ends.
        self.tail = tail
        self.nose = nose
        # Number of swollen segments.
        self.segments = segments
        # Half width at the widest segment; height of its bottom and top there.
        self.width = width
        self.bottom = bottom
        self.top = top
        self.pinch = pinch
        self.girth = girth
        self.closed = closed


def _stations(body: SegmentedBody, default_pinch: float) -> list[list[float]]:
    """The loft stations of a body: a bulge at each segment, a waist between."""
    pinch = body.pinch if body.pinch is not None else default_pinch
    girth = body.girth if body.girth is not None else _swollen
    closed = body.closed if body.closed is not None else [True, True]
    tail = body.tail
    nose = body.nose
    mid = (body.bottom + body.top) / 2
    segments = body.segments

    def station(t: float, k: float) -> list[float]:
        g = girth(t) * k
        return [
            tail + (nose - tail) * t,
            body.width * g,
            mid - (mid - body.bottom) * g,
            mid + (body.top - mid) * g,
        ]

    stations: list[list[float]] = []
    for i in range(2 * segments + 1):
        t = i / (2 * segments)
        # Even stations are the waists between segments, odd ones their swollen middles.
        stations.append(station(t, (1 - pinch) if i % 2 == 0 else 1))
    last = len(stations) - 1
    for index, close in [(0, closed[0]), (last, closed[1])]:
        s = stations[index]
        if close and s is not None:
            stations[index] = [s[0], 0, mid, mid]
    return stations


def segment_stations(body: SegmentedBody) -> list[list[float]]:
    """The loft stations of a `SegmentedBody` (pinch 0.3 by default)."""
    return _stations(body, 0.3)


def segmented_body(
    b: SolidBuilder,
    body: SegmentedBody,
    color: Rgb,
    place: Placement | None = None,
    section: list[SectionPoint] | None = None,
) -> SolidBuilder:
    """Draws a `SegmentedBody` with `section` (`ROUND_SECTION` by default)."""
    if place is None:
        place = Placement()
    if section is None:
        section = ROUND_SECTION
    return b.loft(section, segment_stations(body), color, place)


def carapace(
    b: SolidBuilder,
    body: SegmentedBody,
    colors: list[Rgb],
    place: Placement | None = None,
) -> SolidBuilder:
    """A shell over a body: plates along Z, alternately `colors[0]` and `colors[1]` (the seam),
    on a ridged section."""
    if place is None:
        place = Placement()
    color = colors[0]
    seam = colors[1]

    def paint(_side: int, band: int) -> Rgb | None:
        return seam if band % 2 == 1 else None

    return b.loft(
        SHELL_SECTION,
        _stations(body, 0.12),
        color,
        place,
        LoftOptions(False, paint),
    )


# A tendril follows a path of at least this many points.
MIN_TENDRIL_POINTS = 2
# Below this height along Y, a tangent is not nearly vertical: the first up axis is +Y.
UP_LIMIT = 0.9


def _with_first(first: OutlinePoint, rest: list[OutlinePoint]) -> list[OutlinePoint]:
    """`[first, ...rest]`."""
    result: list[OutlinePoint] = [first]
    for item in rest:
        result.append(item)
    return result


def _across(t: Vec3) -> list[Vec3]:
    """Two unit vectors across `t` (a unit tangent), for the rings of a tube along it."""
    # Any vector not along t, crossed with it.
    up: Vec3 = [0, 1, 0] if abs(t[1]) < UP_LIMIT else [1, 0, 0]
    nx = up[1] * t[2] - up[2] * t[1]
    ny = up[2] * t[0] - up[0] * t[2]
    nz = up[0] * t[1] - up[1] * t[0]
    n = hypot3(nx, ny, nz) or 1
    a: Vec3 = [nx / n, ny / n, nz / n]
    c: Vec3 = [t[1] * a[2] - t[2] * a[1], t[2] * a[0] - t[0] * a[2], t[0] * a[1] - t[1] * a[0]]
    return [a, c]


def _unit(v: Vec3) -> Vec3:
    n = hypot3(v[0], v[1], v[2]) or 1
    return [v[0] / n, v[1] / n, v[2] / n]


def tendril(
    b: SolidBuilder,
    path: list[Vec3],
    radii: list[float],
    sides: int,
    color: Rgb,
    place: Placement | None = None,
) -> SolidBuilder:
    """A tube along the polyline `path`, its radius going from `radii[0]` at the first point to
    `radii[1]` at the last (0 closes it to a point): a tendril, a sinew, a strut, a vein.
    `sides` facets round."""
    if place is None:
        place = Placement()
    if len(path) < MIN_TENDRIL_POINTS:
        raise ValueError("A tendril needs 2 points")
    r0 = radii[0]
    r1 = radii[1]
    last_index = len(path) - 1
    rings: list[list[Vec3]] = []
    for i in range(len(path)):
        p = path[i]
        prev = path[max(0, i - 1)]
        nxt = path[min(last_index, i + 1)]
        a, c = _across(_unit([nxt[0] - prev[0], nxt[1] - prev[1], nxt[2] - prev[2]]))
        r = r0 + ((r1 - r0) * i) / last_index
        ring: list[Vec3] = []
        for k in range(sides):
            angle = (2 * math.pi * k) / sides
            cos = math.cos(angle) * r
            sin = math.sin(angle) * r
            ring.append(
                [
                    p[0] + a[0] * cos + c[0] * sin,
                    p[1] + a[1] * cos + c[1] * sin,
                    p[2] + a[2] * cos + c[2] * sin,
                ]
            )
        rings.append(ring)
    for i in range(1, len(rings)):
        ring = rings[i]
        prev_ring = rings[i - 1]
        for k in range(sides):
            k1 = (k + 1) % sides
            a0 = prev_ring[k]
            a1 = prev_ring[k1]
            b0 = ring[k]
            b1 = ring[k1]
            if i == len(rings) - 1 and r1 == 0:
                b.face([a0, a1, b0], color, place)
            else:
                b.face([a0, a1, b1, b0], color, place)
    if r0 > 0:
        b.face(reversed_copy(rings[0]), color, place)
    if r1 > 0:
        b.face(rings[len(rings) - 1], color, place)
    return b


def curve(from_: Vec3, to: Vec3, bow: Vec3, points: int = 4) -> list[Vec3]:
    """Points along a curve from `from_` to `to`, bowed by `bow` (an offset at its middle)."""
    result: list[Vec3] = []
    for i in range(points + 1):
        t = i / points
        k = 4 * t * (1 - t)
        result.append(
            [
                from_[0] + (to[0] - from_[0]) * t + bow[0] * k,
                from_[1] + (to[1] - from_[1]) * t + bow[1] * k,
                from_[2] + (to[2] - from_[2]) * t + bow[2] * k,
            ]
        )
    return result


class RibSpec:
    """Ribs across a body: each is an arch `half_width` out to each flank and `height` up from
    `y`, of tube `thickness`."""

    def __init__(self, half_width: float, y: float, height: float, thickness: float) -> None:
        self.half_width = half_width
        self.y = y
        self.height = height
        self.thickness = thickness


def ribs(
    b: SolidBuilder,
    at: list[float],
    spec: RibSpec,
    color: Rgb,
    place: Placement | None = None,
) -> SolidBuilder:
    """Ribs across a body: at each Z of `at`, an arch over its back from one flank to the
    other."""
    if place is None:
        place = Placement()
    for z in at:
        arch: list[Vec3] = []
        for i in range(7):
            a = math.pi * (i / 6)
            arch.append(
                [
                    math.cos(a) * spec.half_width,
                    spec.y + math.sin(a) * spec.height,
                    z,
                ]
            )
        tendril(b, arch, [spec.thickness, spec.thickness], 3, color, place)
    return b


def organ(
    b: SolidBuilder,
    radius: float,
    sides: int,
    color: Rgb,
    place: Placement | None = None,
    stretch: float = 1,
) -> SolidBuilder:
    """An organ: a swollen, faceted bulb of `radius`, `stretch` times as tall, standing on its
    base."""
    if place is None:
        place = Placement()
    h = radius * 2 * stretch
    return b.lathe(
        [
            [0, 0],
            [radius * 0.75, h * 0.12],
            [radius, h * 0.45],
            [radius * 0.8, h * 0.8],
            [0, h],
        ],
        sides,
        color,
        place,
    )


class MembraneWing:
    """A wing: a membrane spread between its root and its tips, and a strut out to each tip.

    `root` is where the wing joins the body, `tips` the points of its membrane out to its tips.
    `y` is the height of the membrane, `thickness` its thickness, `strut` the struts' radius at
    the root.
    """

    def __init__(
        self,
        root: OutlinePoint,
        tips: list[OutlinePoint],
        y: float,
        thickness: float,
        strut: float,
    ) -> None:
        self.root = root
        self.tips = tips
        self.y = y
        self.thickness = thickness
        self.strut = strut


def membrane_wing(
    skin: SolidBuilder,
    bone: SolidBuilder,
    wing: MembraneWing,
    colors: list[Rgb],
    place: Placement | None = None,
) -> None:
    """Draws a `MembraneWing`: its membrane in `colors[0]` (from the root along the tips and
    back), a strut along each tip in `colors[1]`, thinning out to it."""
    if place is None:
        place = Placement()
    root = wing.root
    y = wing.y
    thickness = wing.thickness
    strut = wing.strut
    skin.slab(
        _with_first(root, wing.tips),
        [y - thickness / 2, y + thickness / 2],
        colors[0],
        place,
    )
    for tip in wing.tips:
        path = curve(
            [root[0], y, root[1]],
            [tip[0], y, tip[1]],
            [0, thickness * 2, 0],
            3,
        )
        tendril(bone, path, [strut, strut * 0.2], 4, colors[1], place)


def vein(
    b: SolidBuilder,
    path: list[Vec3],
    width: float,
    color: Rgb,
    place: Placement | None = None,
) -> SolidBuilder:
    """A glowing vein along `path`: a thin three-sided tube, `width` across."""
    return tendril(b, path, [width / 2, width / 4], 3, color, place)


def _offset(place: Placement, p: Vec3) -> Vec3:
    """`p` moved by the position of `place` (its turns left out: rivets are tiny)."""
    a = place.at if place.at is not None else [0, 0, 0]
    return [a[0] + p[0], a[1] + p[1], a[2] + p[2]]


def plate(
    b: SolidBuilder,
    outline: list[OutlinePoint],
    heights: list[float],
    colors: list[Rgb],
    place: Placement | None = None,
) -> SolidBuilder:
    """An armour plate grafted on: a bevelled slab of `outline` from `heights[0]` to
    `heights[1]`, and a rivet at each of its corners in `colors[1]`."""
    if place is None:
        place = Placement()
    y0 = heights[0]
    y1 = heights[1]
    t = y1 - y0
    b.bevel_slab(outline, [y0, y0, y1], [0, t * 0.8], colors[0], place)
    for p in outline:
        cx = p[0] * 0.82
        cz = p[1] * 0.82
        b.box(
            [t * 0.6, t * 0.4, t * 0.6],
            colors[1],
            place_at(place, _offset(place, [cx, y1, cz])),
        )
    return b


def grown(
    outline: list[OutlinePoint],
    amount: float,
    random: Callable[[], float],
) -> list[OutlinePoint]:
    """The outline with each point moved by up to `amount` at random: an uneven, grown edge
    instead of a drawn one. The same `random` sequence gives the same outline."""
    result: list[OutlinePoint] = []
    for p in outline:
        dx = (random() * 2 - 1) * amount
        dz = (random() * 2 - 1) * amount
        result.append([p[0] + dx, p[1] + dz])
    return result
