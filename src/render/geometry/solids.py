"""Low-poly, flat-shaded, vertex-coloured solids (ported from `render/geometry/solids.ts`).

Each face has its own vertices, so the normals computed later are per face. Vectors are
lists of 3 numbers, outlines are `[x, z]` lists (see `outline.py`).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.geometry.gradient_shapes import ColoredGeometry
from render.geometry.outline import inset_outline, reversed_copy, ring_at
from render.geometry.triangulate import triangulate_polygon

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

from render.geometry.outline import OutlinePoint  # noqa: E402

Rgb = list[float]
Vec3 = list[float]
ProfilePoint = list[float]
SectionPoint = list[float]
LoftStation = list[float]

__pragma__("noskip")


class Placement:
    """Where a solid goes: a position `at`, then turns around X (pitch), Z (roll) and Y (yaw),
    in radians."""

    def __init__(
        self,
        at: Vec3 | None = None,
        yaw: float = 0,
        pitch: float = 0,
        roll: float = 0,
    ) -> None:
        self.at = at
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll


def place_at(place: Placement, at: Vec3) -> Placement:
    """A copy of `place` moved to `at` (`{ ...place, at }`)."""
    return Placement(at, place.yaw, place.pitch, place.roll)


class LoftOptions:
    """Options of `SolidBuilder.loft` (its `open` and `paint`).

    `paint(side, band)` gives another colour for some faces (or None): side `side` of the
    section, between stations `band` and `band + 1`.
    """

    def __init__(self, open_: bool = False, paint: Callable[[int, int], Any] | None = None) -> None:
        self.open = open_
        self.paint = paint


def _rotate(p: Vec3, place: Placement) -> Vec3:
    x, y, z = p[0], p[1], p[2]
    yaw = place.yaw
    pitch = place.pitch
    roll = place.roll
    # Pitch (around X), then roll (around Z), then yaw (around Y).
    y1 = y * math.cos(pitch) - z * math.sin(pitch)
    z1 = y * math.sin(pitch) + z * math.cos(pitch)
    x2 = x * math.cos(roll) - y1 * math.sin(roll)
    y2 = x * math.sin(roll) + y1 * math.cos(roll)
    x3 = x2 * math.cos(yaw) + z1 * math.sin(yaw)
    z3 = -x2 * math.sin(yaw) + z1 * math.cos(yaw)
    return [x3, y2, z3]


def _double_area(outline: list[OutlinePoint]) -> float:
    """Twice the signed area of an outline in the XZ plane: positive when counter-clockwise."""
    total = 0.0
    for i in range(len(outline)):
        p = outline[i]
        q = ring_at(outline, i + 1)
        total = total + p[0] * q[1] - q[0] * p[1]
    return total


def _side_face(a0: Vec3, a1: Vec3, b1: Vec3, b0: Vec3, r_a: float, r_b: float) -> list[Vec3]:
    """A side facet of a body of revolution, a triangle where a ring closes to a point."""
    if r_a == 0:
        return [a1, b1, b0]
    if r_b == 0:
        return [a0, a1, b1]
    return [a0, a1, b1, b0]


def _at(p: OutlinePoint, y: float) -> Vec3:
    return [p[0], y, p[1]]


def _is_point(station: LoftStation) -> bool:
    """A loft station of no width and no height: the body closes to a point there."""
    return station[1] == 0 and station[2] == station[3]


class SolidBuilder:
    """Builds low-poly, flat-shaded, vertex-coloured solids into one `ColoredGeometry`.

    With `open_bottoms`, upright boxes and bodies of revolution get no bottom face: for
    buildings seen from above, standing on the ground or on another solid, it would never show.
    """

    def __init__(self, open_bottoms: bool = False) -> None:
        self.geometry = ColoredGeometry()
        self._open_bottoms = open_bottoms

    def _open_bottom(self, place: Placement) -> bool:
        """Whether the bottom face of a solid placed by `place` is left out."""
        return self._open_bottoms is True and not place.pitch and not place.roll

    def _point(self, p: Vec3, place: Placement) -> Vec3:
        r = _rotate(p, place)
        a = place.at if place.at != None else [0, 0, 0]  # noqa: E711 (undefined for an absent field)
        return [r[0] + a[0], r[1] + a[1], r[2] + a[2]]

    def face(
        self, corners: list[Vec3], color: Rgb, place: Placement | None = None
    ) -> "SolidBuilder":
        """A flat convex polygon. Its outward normal is (c1 - c0) × (c2 - c0): the corners go
        counter-clockwise seen from outside."""
        if place is None:
            place = Placement()
        geo = self.geometry
        base = len(geo.positions) // 3
        for corner in corners:
            geo.positions.extend(self._point(corner, place))
            geo.colors.extend([color[0], color[1], color[2], 1])
        # Babylon front faces have the normal (c - a) × (b - a), hence the swapped order.
        for i in range(1, len(corners) - 1):
            geo.indices.extend([base, base + i + 1, base + i])
        return self

    def _caps(self, profile: list[ProfilePoint], sides: int, color: Rgb, place: Placement) -> None:
        """Flat caps on the ends of a body of revolution that are not closed to a point."""
        ends = [(profile[0], False), (profile[len(profile) - 1], True)]
        for end, up in ends:
            if end is None or end[0] <= 0 or (not up and self._open_bottom(place)):
                continue
            r = end[0]
            y = end[1]
            corners: list[Vec3] = []
            for i in range(sides):
                k = (sides - i) if up else i
                a = (k / sides) * math.pi * 2
                corners.append([r * math.cos(a), y, r * math.sin(a)])
            self.face(corners, color, place)

    def box(
        self,
        size: Vec3,
        color: Rgb,
        place: Placement | None = None,
        top: Rgb | None = None,
    ) -> "SolidBuilder":
        """A box of size (w, h, d) standing on its base at `at`."""
        if place is None:
            place = Placement()
        if top is None:
            top = color
        w, h, d = size[0], size[1], size[2]
        x0 = -w / 2
        x1 = w / 2
        z0 = -d / 2
        z1 = d / 2
        self.face([[x0, h, z0], [x0, h, z1], [x1, h, z1], [x1, h, z0]], top, place)
        if not self._open_bottom(place):
            self.face([[x0, 0, z0], [x1, 0, z0], [x1, 0, z1], [x0, 0, z1]], color, place)
        self.face([[x0, 0, z0], [x0, h, z0], [x1, h, z0], [x1, 0, z0]], color, place)
        self.face([[x1, 0, z1], [x1, h, z1], [x0, h, z1], [x0, 0, z1]], color, place)
        self.face([[x0, 0, z1], [x0, h, z1], [x0, h, z0], [x0, 0, z0]], color, place)
        self.face([[x1, 0, z0], [x1, h, z0], [x1, h, z1], [x1, 0, z1]], color, place)
        return self

    def lathe(
        self,
        profile: list[ProfilePoint],
        sides: int,
        color: Rgb,
        place: Placement | None = None,
        caps: bool = True,
    ) -> "SolidBuilder":
        """A body of revolution around Y with `sides` flat facets: the profile goes from bottom
        to top. A profile point of radius 0 closes the body there; otherwise the ends are
        capped, unless `caps` is false."""
        if place is None:
            place = Placement()

        def ring(i: int) -> float:
            return (i / sides) * math.pi * 2

        def at(p: ProfilePoint, i: int) -> Vec3:
            return [p[0] * math.cos(ring(i)), p[1], p[0] * math.sin(ring(i))]

        for k in range(len(profile) - 1):
            a = profile[k]
            b = profile[k + 1]
            for i in range(sides):
                self.face(
                    _side_face(at(a, i + 1), at(a, i), at(b, i), at(b, i + 1), a[0], b[0]),
                    color,
                    place,
                )
        if caps:
            self._caps(profile, sides, color, place)
        return self

    def ring(
        self,
        radius: float,
        height: float,
        sides: int,
        color: Rgb,
        place: Placement | None = None,
    ) -> "SolidBuilder":
        """An open band around Y (no caps), e.g. a lit ring around a building."""
        return self.lathe([[radius, 0], [radius, height]], sides, color, place, False)

    def cylinder(
        self,
        radius: float,
        height: float,
        sides: int,
        color: Rgb,
        place: Placement | None = None,
        top_radius: float | None = None,
    ) -> "SolidBuilder":
        """A straight (or tapered) cylinder of `sides` facets standing on its base."""
        if top_radius is None:
            top_radius = radius
        return self.lathe([[radius, 0], [top_radius, height]], sides, color, place)

    def slab(
        self,
        outline: list[OutlinePoint],
        y_range: list[float],
        color: Rgb,
        place: Placement | None = None,
        top: Rgb | None = None,
    ) -> "SolidBuilder":
        """A flat slab: a simple polygon outline in the XZ plane (concave is fine, either
        winding), extruded from height `y_range[0]` up to `y_range[1]`."""
        if place is None:
            place = Placement()
        if top is None:
            top = color
        y0 = y_range[0]
        y1 = y_range[1]
        ring = list(outline) if _double_area(outline) > 0 else reversed_copy(outline)
        for a, b, c in triangulate_polygon(ring):
            pa = ring_at(ring, a)
            pb = ring_at(ring, b)
            pc = ring_at(ring, c)
            # Counter-clockwise in (x, z) faces down; reversed, it faces up.
            self.face([_at(pa, y1), _at(pc, y1), _at(pb, y1)], top, place)
            self.face([_at(pa, y0), _at(pb, y0), _at(pc, y0)], color, place)
        for i in range(len(ring)):
            p = ring[i]
            q = ring_at(ring, i + 1)
            self.face([_at(p, y0), _at(p, y1), _at(q, y1), _at(q, y0)], color, place)
        return self

    def bevel_slab(
        self,
        outline: list[OutlinePoint],
        heights: list[float],
        insets: list[float],
        color: Rgb,
        place: Placement | None = None,
        top: Rgb | None = None,
    ) -> "SolidBuilder":
        """A slab with bevelled edges: the outline at height `waist`, narrowing by `inset`
        (bottom, top) to a smaller bottom face at `y0` and top face at `y1`."""
        if place is None:
            place = Placement()
        if top is None:
            top = color
        y0 = heights[0]
        waist = heights[1]
        y1 = heights[2]
        ring = list(outline) if _double_area(outline) > 0 else reversed_copy(outline)
        bottom = inset_outline(ring, insets[0])
        upper = inset_outline(ring, insets[1])
        for a, b, c in triangulate_polygon(ring):
            ua = ring_at(upper, a)
            ub = ring_at(upper, b)
            uc = ring_at(upper, c)
            da = ring_at(bottom, a)
            db = ring_at(bottom, b)
            dc = ring_at(bottom, c)
            self.face([_at(ua, y1), _at(uc, y1), _at(ub, y1)], top, place)
            self.face([_at(da, y0), _at(db, y0), _at(dc, y0)], color, place)
        for i in range(len(ring)):
            p = ring[i]
            q = ring_at(ring, i + 1)
            pd = ring_at(bottom, i)
            qd = ring_at(bottom, i + 1)
            pu = ring_at(upper, i)
            qu = ring_at(upper, i + 1)
            if y0 < waist:
                self.face([_at(pd, y0), _at(p, waist), _at(q, waist), _at(qd, y0)], color, place)
            self.face([_at(p, waist), _at(pu, y1), _at(qu, y1), _at(q, waist)], color, place)
        return self

    def loft(
        self,
        section: list[SectionPoint],
        stations: list[LoftStation],
        color: Rgb,
        place: Placement | None = None,
        options: LoftOptions | None = None,
    ) -> "SolidBuilder":
        """A fuselage along Z: the `section` (counter-clockwise seen from the nose) stretched to
        each station, from tail to nose. A station of no width and no height closes the body to
        a point there; other ends are capped, unless `options.open`."""
        if place is None:
            place = Placement()
        if options is None:
            options = LoftOptions()

        def ring(st: LoftStation) -> list[Vec3]:
            return [[u * st[1], st[2] + v * (st[3] - st[2]), st[0]] for u, v in section]

        sides = len(section) - 1 if options.open else len(section)
        for k in range(len(stations) - 1):
            sa = stations[k]
            sb = stations[k + 1]
            self._loft_band(
                ring(sa),
                ring(sb),
                _is_point(sa),
                _is_point(sb),
                sides,
                k,
                color,
                options.paint,
                place,
            )
        if not options.open:
            rings = [ring(st) for st in stations]
            points = [_is_point(st) for st in stations]
            self._loft_caps(rings, points, color, place)
        return self

    def _loft_caps(
        self, rings: list[list[Vec3]], points: list[bool], color: Rgb, place: Placement
    ) -> None:
        """Caps on the ends of a loft (its first and last rings) that are not closed to a point."""
        first = rings[0]
        last = rings[len(rings) - 1]
        if len(first) > 0 and not points[0]:
            self.face(reversed_copy(first), color, place)
        if len(last) > 0 and not points[len(points) - 1]:
            self.face(last, color, place)

    def _loft_band(  # noqa: PLR0917 (positional: a private helper of loft)
        self,
        a: list[Vec3],
        b: list[Vec3],
        a_point: bool,
        b_point: bool,
        sides: int,
        band: int,
        color: Rgb,
        paint: Callable[[int, int], Any] | None,
        place: Placement,
    ) -> None:
        """The faces between two loft rings, triangles where one of them is a point."""
        for i in range(sides):
            a0 = ring_at(a, i)
            a1 = ring_at(a, i + 1)
            b0 = ring_at(b, i)
            b1 = ring_at(b, i + 1)
            face_color = color
            if paint is not None:
                painted = paint(i, band)
                if painted is not None:
                    face_color = painted
            if a_point:
                self.face([a0, b1, b0], face_color, place)
            elif b_point:
                self.face([a0, a1, b1], face_color, place)
            else:
                self.face([a0, a1, b1, b0], face_color, place)
