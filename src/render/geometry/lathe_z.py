"""Bodies of revolution around the Z axis (ported from `render/geometry/lathe-z.ts`)."""

import math

from org.transcrypt.stubs.browser import __pragma__

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

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

DEFAULT_TESSELLATION = 24


class LatheHalves:
    """A cross-section split into halves, with `upper` sides over the top (+Y) and `lower` over
    the bottom: a smooth top over a low-poly belly, for example."""

    def __init__(self, upper: int, lower: int) -> None:
        self.upper = upper
        self.lower = lower


def create_lathe_along_z(
    label: str,
    profile: list[list[float]],
    scene: Any,
    tessellation: int = DEFAULT_TESSELLATION,
) -> Any:
    """Revolves a profile `[z, radius]` around the Z axis (the ship's nose-to-tail axis). Start
    and end the profile with a radius of 0 to get a closed body. The profile may run in either
    direction."""
    # Lathe faces point outward when the profile runs towards +Z (tail to nose).
    ordered = _ordered_towards_nose(profile)
    shape = [vector3(p[1], p[0], 0) for p in ordered]
    mesh = create_lathe(label, shape, tessellation, scene)
    # Lathe revolves around Y; +90° around X maps +Y onto +Z.
    mesh.rotation.x = math.pi / 2
    bake_transform(mesh)
    return mesh


def _ordered_towards_nose(profile: list[list[float]]) -> list[list[float]]:
    """The profile running from tail to nose (+Z)."""
    if len(profile) > 0 and profile[0][0] > profile[len(profile) - 1][0]:
        return reversed_copy(profile)
    return profile


def section_angles(section: int | LatheHalves) -> list[float]:
    """Angles of the section's vertices, counter-clockwise from +X (towards +Y). The first one is
    always 0, and so is a vertex on -X when the section is split into halves."""
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
) -> tuple[list[float], list[float]]:
    """Revolves a profile around the Z axis with a polygonal section, flat-shaded (vertices are
    not shared between faces). Same profile rules as `create_lathe_along_z`. Returns the
    positions and the indices."""
    # Faces point outward when the profile runs towards +Z (tail to nose).
    ordered = _ordered_towards_nose(profile)
    angles = section_angles(section)
    positions: list[float] = []
    indices: list[float] = []

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
    """Like `create_lathe_along_z`, but polygonal and flat-shaded. With a number of sides, the
    section is regular with vertices on ±X (6 sides: flat top and bottom)."""
    positions, indices = build_faceted_lathe_vertex_data(profile, section)
    normals = compute_normals(positions, indices)
    data = vertex_data_of(positions, indices, normals)
    mesh = new_mesh(label, scene)
    apply_vertex_data(data, mesh)
    return mesh
