# Copyright (c) 2026 Renaud Guillon
"""Bodies of revolution around the Z axis (faceted lathes: GFX-ART-09)."""

import math

from render.babylon import (
    apply_vertex_data,
    bake_transform,
    compute_normals,
    create_lathe,
    new_mesh,
    vector3,
    vertex_data_of,
)
from render.geometry.outline import reversed_copy

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


DEFAULT_TESSELLATION = 24


class LatheHalves:
    """A cross-section split into halves: `upper` sides over the top (+Y), `lower` over the bottom.

    For example a smooth top over a low-poly belly.
    """

    def __init__(self, upper: int, lower: int) -> None:
        self.upper = upper
        self.lower = lower


def create_lathe_along_z(
    label: str,
    profile: list[list[float]],
    scene: Any,
    tessellation: int = DEFAULT_TESSELLATION,
) -> Any:
    """Revolves a profile `[z, radius]` around the Z axis (the ship's nose-to-tail axis).

    Start and end the profile with a radius of 0 to get a closed body. The profile may run in either
    direction.
    """
    # Lathe faces point outward when the profile runs towards +Z (tail to nose).
    ordered = _ordered_towards_nose(profile)
    shape = [vector3(p[1], p[0], 0) for p in ordered]
    mesh = create_lathe(label, shape, tessellation, scene)
    # Lathe revolves around Y; +90° around X maps +Y onto +Z.
    mesh.rotation.x = math.pi / 2
    bake_transform(mesh)
    return mesh


def _ordered_towards_nose(profile: list[list[float]]) -> list[list[float]]:
    """Return the profile running from tail to nose (+Z)."""
    if len(profile) > 0 and profile[0][0] > profile[len(profile) - 1][0]:
        return reversed_copy(profile)
    return profile


def section_angles(section: int | LatheHalves) -> list[float]:
    """Angles of the section's vertices, counter-clockwise from +X (towards +Y).

    The first one is always 0, and so is a vertex on -X when the section is split into halves.
    """
    if isinstance(section, LatheHalves):
        upper = section.upper
        lower = section.lower
        angles = [(math.pi * k) / upper for k in range(upper)]
        angles.extend([math.pi + (math.pi * k) / lower for k in range(lower)])
        return angles
    return [(2 * math.pi * k) / section for k in range(section)]


def _with_one_more(items: list[float], extra: float) -> list[float]:
    """`items` followed by `extra` (a copy)."""
    result = list(items)
    result.append(extra)
    return result


def _consecutive_pairs(items: list[Any]) -> list[list[Any]]:
    """Every pair of neighbouring items: `[a, b, c]` gives `[a, b]` and `[b, c]`."""
    return [[items[i], items[i + 1]] for i in range(len(items) - 1)]


def build_faceted_lathe_vertex_data(
    profile: list[list[float]],
    section: int | LatheHalves,
) -> tuple[list[float], list[int]]:
    """Revolves a profile around the Z axis with a polygonal section.

    Flat-shaded: vertices are not shared between faces.

    Same profile rules as `create_lathe_along_z`. Returns the positions and the indices.
    """
    # Faces point outward when the profile runs towards +Z (tail to nose).
    ordered = _ordered_towards_nose(profile)
    angles = section_angles(section)
    positions: list[float] = []
    indices: list[int] = []

    def vertex(p: list[float], angle: float) -> list[float]:
        return [p[1] * math.cos(angle), p[1] * math.sin(angle), p[0]]

    def tri(a: list[float], b: list[float], c: list[float]) -> None:
        base = len(positions) // 3
        positions.extend(a)
        positions.extend(b)
        positions.extend(c)
        indices.extend([base, base + 1, base + 2])

    # Facets between consecutive angles, closing the ring with a full turn.
    facets = _consecutive_pairs(_with_one_more(angles, 2 * math.pi))
    for p, q in _consecutive_pairs(ordered):
        for pair in facets:
            angle = pair[0]
            nxt = pair[1]
            # Skip the triangle that would collapse onto the axis.
            if p[1] > 0:
                tri(vertex(p, angle), vertex(q, angle), vertex(p, nxt))
            if q[1] > 0:
                tri(vertex(p, nxt), vertex(q, angle), vertex(q, nxt))
    return positions, indices


def create_faceted_lathe_along_z(
    label: str,
    profile: list[list[float]],
    section: int | LatheHalves,
    scene: Any,
) -> Any:
    """Like `create_lathe_along_z`, but polygonal and flat-shaded.

    With a number of sides, the section is regular with vertices on ±X (6 sides: flat top and
    bottom).
    """
    positions, indices = build_faceted_lathe_vertex_data(profile, section)
    normals = compute_normals(positions, indices)
    data = vertex_data_of(positions, indices, normals)
    mesh = new_mesh(label, scene)
    apply_vertex_data(data, mesh)
    return mesh


def smooth_profile(profile: list[list[float]], steps: int) -> list[list[float]]:
    """Return the profile `[z, radius]` with each segment cut into `steps`, along a smooth curve.

    The curve is a Catmull-Rom spline through the profile's points, so it keeps every one of them,
    the first and the last included. Radii that would dip under 0 are kept at 0.
    """
    count = len(profile)
    if count < 2 or steps < 2:
        return [list(p) for p in profile]

    def at(i: int) -> list[float]:
        return profile[max(0, min(count - 1, i))]

    result: list[list[float]] = []
    for i in range(count - 1):
        p0 = at(i - 1)
        p1 = at(i)
        p2 = at(i + 1)
        p3 = at(i + 2)
        for k in range(steps):
            t = k / steps
            t2 = t * t
            t3 = t2 * t
            point = [
                0.5
                * (
                    2 * p1[j]
                    + (p2[j] - p0[j]) * t
                    + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                    + (3 * p1[j] - p0[j] - 3 * p2[j] + p3[j]) * t3
                )
                for j in range(2)
            ]
            point[1] = max(0.0, point[1])
            result.append(point)
    last = profile[count - 1]
    result.append([last[0], last[1]])
    return result


def _surface_normal(angle: float, dz: float, dr: float) -> list[float]:
    """Return the unit outward normal of a body of revolution, at `angle`, where it runs (dz, dr).

    The surface (r(z) cos a, r(z) sin a, z) has the outward normal (cos a, sin a, -r'), times dz.
    """
    x = math.cos(angle) * dz
    y = math.sin(angle) * dz
    z = -dr
    length = math.sqrt(x * x + y * y + z * z)
    if length == 0:
        return [math.cos(angle), math.sin(angle), 0]
    return [x / length, y / length, z / length]


class _SmoothTopBuilder:
    """Accumulates the triangles of a smooth-top lathe, with their normals."""

    def __init__(self, ordered: list[list[float]]) -> None:
        self.ordered = ordered
        self.positions: list[float] = []
        self.indices: list[int] = []
        self.normals: list[float] = []

    def _tangent(self, i: int) -> list[float]:
        last = len(self.ordered) - 1
        before = self.ordered[max(0, i - 1)]
        after = self.ordered[min(last, i + 1)]
        return [after[0] - before[0], after[1] - before[1]]

    def corner(self, i: int, angle: float, flat: list[float] | None) -> None:
        """Add the vertex of profile point `i` at `angle`: its own normal, or `flat` if given."""
        p = self.ordered[i]
        self.positions.extend([p[1] * math.cos(angle), p[1] * math.sin(angle), p[0]])
        if flat is not None:
            self.normals.extend(flat)
            return
        t = self._tangent(i)
        self.normals.extend(_surface_normal(angle, t[0], t[1]))

    def facet(self, i: int, angle: float, nxt: float) -> None:
        """Add the facet between profile points `i` and `i + 1`, from `angle` to `nxt`.

        Upper facets (angles under pi) are smooth; lower ones get one normal.
        """
        p = self.ordered[i]
        q = self.ordered[i + 1]
        flat: list[float] | None = None
        if angle >= math.pi - 1e-9:
            flat = _surface_normal((angle + nxt) / 2, q[0] - p[0], q[1] - p[1])
        # Skip the triangle that would collapse onto the axis.
        if p[1] > 0:
            self._tri([[i, angle], [i + 1, angle], [i, nxt]], flat)
        if q[1] > 0:
            self._tri([[i, nxt], [i + 1, angle], [i + 1, nxt]], flat)

    def _tri(self, corners: list[list[float]], flat: list[float] | None) -> None:
        base = len(self.positions) // 3
        for c in corners:
            self.corner(int(c[0]), c[1], flat)
        self.indices.extend([base, base + 1, base + 2])


def build_smooth_top_lathe_vertex_data(
    profile: list[list[float]],
    halves: LatheHalves,
) -> tuple[list[float], list[int], list[float]]:
    """Revolve a profile around the Z axis: a smooth-shaded top over a flat-shaded faceted belly.

    The same triangles as `build_faceted_lathe_vertex_data` with these halves. The upper facets'
    vertices get the surface's own normal, so the top shades smoothly however few its facets; the
    lower facets get one normal each, flat. The chine where the halves meet stays a crisp edge.
    Returns the positions, the indices and the normals.
    """
    ordered = _ordered_towards_nose(profile)
    builder = _SmoothTopBuilder(ordered)
    facets = _consecutive_pairs(_with_one_more(section_angles(halves), 2 * math.pi))
    for i in range(len(ordered) - 1):
        for pair in facets:
            builder.facet(i, pair[0], pair[1])
    return builder.positions, builder.indices, builder.normals


def create_smooth_top_lathe_along_z(
    label: str,
    profile: list[list[float]],
    halves: LatheHalves,
    scene: Any,
) -> Any:
    """Like `create_faceted_lathe_along_z` with halves, but its top is smooth-shaded."""
    positions, indices, normals = build_smooth_top_lathe_vertex_data(profile, halves)
    data = vertex_data_of(positions, indices, normals)
    mesh = new_mesh(label, scene)
    apply_vertex_data(data, mesh)
    return mesh
