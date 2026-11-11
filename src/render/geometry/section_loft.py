# Copyright (c) 2026 Renaud Guillon
"""A skin lofted through cross-sections along the Z axis, smooth on top, faceted below.

Each section is `[z, ring]`, the ring a closed loop of `[x, y]` points, every ring with the same
number of points. Neighbouring sections are joined point to point. The first `smooth_count` points
of each ring are the smooth part (a ship's upper half): the vertices there get normals averaged
over the faces round them, so the skin shades as one curved surface; the other faces are flat. A
section whose ring is a single repeated point closes the skin (a nose or a tail); an end section
with a real ring is closed by a flat cap.

Triangles are wound so their Babylon front normal, `(p2 - p0) x (p1 - p0)`, points out of the skin,
which the edge trim relies on (see `edge_trim.py`). Every triangle of the skin is wound the same
way round, from the order of the sections and of the ring points; which way is chosen once for the
whole skin, the way that faces away from the sections' centre line overall. Deciding it triangle by
triangle would turn round the faces of a hollow (the inner slope of a shoulder faces the centre
line), and the renderer would cull them, leaving holes.
"""

import math

from render.babylon import apply_vertex_data, new_mesh, vertex_data_of
from render.geometry.vec3 import cross, norm

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

Vec3 = list[float]
Section = list[Any]
# __pragma__ ("noskip")


def _minus(a: Vec3, b: Vec3) -> Vec3:
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def _dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _centre(section: Section) -> Vec3:
    """Return the middle of a section's ring, at its Z."""
    ring = section[1]
    x = sum(p[0] for p in ring) / len(ring)
    y = sum(p[1] for p in ring) / len(ring)
    return [x, y, section[0]]


def _point(section: Section, j: int) -> Vec3:
    p = section[1][j]
    return [p[0], p[1], section[0]]


class _Face:
    """A triangle of the skin: its corners' keys and points, its outward normal (area-weighted)."""

    def __init__(self, keys: list[str], points: list[Vec3], normal: Vec3, smooth: bool) -> None:
        self.keys = keys
        self.points = points
        self.normal = normal
        self.smooth = smooth


def _face(keys: list[str], points: list[Vec3], smooth: bool) -> _Face | None:
    """Return the triangle as given, or None when it has no area."""
    normal = cross(_minus(points[2], points[0]), _minus(points[1], points[0]))
    if _dot(normal, normal) < 1e-18:
        return None
    return _Face(keys, points, normal, smooth)


def _outwardness(face: _Face, inside: Vec3) -> float:
    """How much the face looks away from `inside` (negative when it looks towards it)."""
    middle = [sum(p[k] for p in face.points) / 3 for k in range(3)]
    return _dot(face.normal, _minus(middle, inside))


def _turn_round(face: _Face) -> None:
    face.keys = [face.keys[0], face.keys[2], face.keys[1]]
    face.points = [face.points[0], face.points[2], face.points[1]]
    face.normal = [-face.normal[0], -face.normal[1], -face.normal[2]]


def _turned_outward(faces: list[_Face], insides: list[Vec3]) -> list[_Face]:
    """Turn every face round when, taken together, they look inwards; return them."""
    total = 0.0
    for i in range(len(faces)):
        total += _outwardness(faces[i], insides[i])
    if total < 0:
        for face in faces:
            _turn_round(face)
    return faces


def _faces(sections: list[Section], smooth_count: int) -> list[_Face]:
    """Every triangle between neighbouring sections."""
    faces: list[_Face] = []
    insides: list[Vec3] = []
    count = len(sections[0][1])
    for s in range(len(sections) - 1):
        a = sections[s]
        b = sections[s + 1]
        ca = _centre(a)
        cb = _centre(b)
        inside = [(ca[k] + cb[k]) / 2 for k in range(3)]
        for j in range(count):
            k = (j + 1) % count
            smooth = j + 1 < smooth_count
            corners = [[s, j], [s, k], [s + 1, k], [s + 1, j]]
            keys = [str(c[0]) + ":" + str(c[1]) for c in corners]
            points = [_point(sections[c[0]], c[1]) for c in corners]
            for tri in [[0, 1, 2], [0, 2, 3]]:
                face = _face([keys[i] for i in tri], [points[i] for i in tri], smooth)
                if face is not None:
                    faces.append(face)
                    insides.append(inside)
    return _turned_outward(faces, insides)


def _cap(sections: list[Section], s: int, toward: int) -> list[_Face]:
    """Return the flat cap closing the end section `s`, facing away from section `toward`."""
    section = sections[s]
    centre = _centre(section)
    inside = _centre(sections[toward])
    count = len(section[1])
    faces: list[_Face] = []
    insides: list[Vec3] = []
    for j in range(count):
        k = (j + 1) % count
        keys = ["c" + str(s), str(s) + ":" + str(j), str(s) + ":" + str(k)]
        points = [centre, _point(section, j), _point(section, k)]
        face = _face(keys, points, False)
        if face is not None:
            faces.append(face)
            insides.append(inside)
    return _turned_outward(faces, insides)


def build_section_loft(
    sections: list[Section],
    smooth_count: int,
) -> tuple[list[float], list[int], list[float]]:
    """Return the positions, indices and normals of the skin through `sections`.

    Each face has its own vertices; the smooth part's share normals by ring point and section.
    """
    faces = _faces(sections, smooth_count)
    last = len(sections) - 1
    faces.extend(_cap(sections, 0, 1))
    faces.extend(_cap(sections, last, last - 1))
    shared: dict[str, Vec3] = {}
    for face in faces:
        if face.smooth:
            for key in face.keys:
                total = shared.get(key, [0.0, 0.0, 0.0])
                shared[key] = [total[k] + face.normal[k] for k in range(3)]
    positions: list[float] = []
    indices: list[int] = []
    normals: list[float] = []
    for face in faces:
        flat = norm(face.normal)
        for i in range(3):
            positions.extend(face.points[i])
            normals.extend(norm(shared[face.keys[i]]) if face.smooth else flat)
            indices.append(len(indices))
    return positions, indices, normals


def create_section_loft(label: str, sections: list[Section], smooth_count: int, scene: Any) -> Any:
    """Create the mesh of the skin through `sections` (see `build_section_loft`)."""
    positions, indices, normals = build_section_loft(sections, smooth_count)
    mesh = new_mesh(label, scene)
    apply_vertex_data(vertex_data_of(positions, indices, normals), mesh)
    return mesh


def rounded_polygon(sides: int, radius: float, rounding: float, steps: int) -> list[list[float]]:
    """Return a regular polygon's outline with rounded corners, as `[x, y]` points round the origin.

    `sides` corners, the first on +X, `radius` from the centre to a corner as if it were sharp;
    each corner is rounded by an arc of `steps` points (2 or more) whose radius is `rounding` times
    `radius`, tangent to both sides, so the sides stay where the sharp polygon's are. Counter
    clockwise. A `radius` of 0 gives every point at the origin (a closed end of a loft).
    """
    half = math.pi / sides
    arc = rounding * radius
    # The arc's centre, on the corner's bisector, `arc` from both sides.
    centre = radius - arc / math.cos(half)
    ring: list[list[float]] = []
    for k in range(sides):
        corner = 2 * math.pi * k / sides
        cx = centre * math.cos(corner)
        cy = centre * math.sin(corner)
        for s in range(steps):
            angle = corner - half + 2 * half * s / (steps - 1)
            ring.append([cx + arc * math.cos(angle), cy + arc * math.sin(angle)])
    return ring


def polygon_lathe_sections(
    profile: list[list[float]], sides: int, rounding: float, steps: int
) -> list[Section]:
    """Return the sections of a body round the Z axis with a rounded polygon section.

    `profile` as a lathe's (`[z, radius]` points); each section is `rounded_polygon` at that radius.
    """
    return [[p[0], rounded_polygon(sides, p[1], rounding, steps)] for p in profile]
