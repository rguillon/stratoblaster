"""Small vector maths for the tests of `render/`: the triangles of a flat-shaded mesh, and the
normal Babylon gives each one (`(c - a) × (b - a)` for the index triple `(a, b, c)`)."""

from typing import Any

Vec = list[float]


def sub(p: Vec, q: Vec) -> Vec:
    return [p[0] - q[0], p[1] - q[1], p[2] - q[2]]


def cross(p: Vec, q: Vec) -> Vec:
    return [p[1] * q[2] - p[2] * q[1], p[2] * q[0] - p[0] * q[2], p[0] * q[1] - p[1] * q[0]]


def dot(p: Vec, q: Vec) -> float:
    return p[0] * q[0] + p[1] * q[1] + p[2] * q[2]


def points_of(positions: list[float]) -> list[Vec]:
    """The flat list of coordinates as a list of 3D points."""
    return [positions[i : i + 3] for i in range(0, len(positions), 3)]


def triangles(positions: list[float], indices: list[Any]) -> list[tuple[Vec, Vec, Vec]]:
    """Each index triple as its three points, in index order."""
    points = points_of(positions)
    return [(points[a], points[b], points[c]) for a, b, c in zip(*[iter(indices)] * 3, strict=True)]


def babylon_normal(tri: tuple[Vec, Vec, Vec]) -> Vec:
    """The normal of a triangle as Babylon takes it: `(c - a) × (b - a)`."""
    a, b, c = tri
    return cross(sub(c, a), sub(b, a))


def centroid(tri: tuple[Vec, Vec, Vec]) -> Vec:
    a, b, c = tri
    return [(a[i] + b[i] + c[i]) / 3 for i in range(3)]


def enclosed_volume(positions: list[float], indices: list[Any]) -> float:
    """The volume a closed mesh encloses (divergence theorem). It is positive when every face
    has its Babylon normal pointing outwards, so it also checks the winding of every face."""
    total = 0.0
    for tri in triangles(positions, indices):
        total += dot(tri[0], babylon_normal(tri)) / 6
    return total
