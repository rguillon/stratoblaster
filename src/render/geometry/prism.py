"""Flat-shaded prisms from a planform outline (ported from `render/geometry/prism.ts`)."""

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import apply_vertex_data, compute_normals, new_mesh, vertex_data_of
from render.geometry.outline import reversed_copy, ring_at
from render.geometry.triangulate import triangulate_polygon

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from render.geometry.outline import OutlinePoint  # noqa: E402

__pragma__("noskip")


# A prism needs a polygon of at least this many corners.
MIN_OUTLINE_POINTS = 3


class PrismGeometry:
    """Raw geometry of a prism, before it is turned into a Babylon mesh."""

    def __init__(self, positions: list[float], indices: list[float]) -> None:
        self.positions = positions
        self.indices = indices


def _signed_area(outline: list[OutlinePoint]) -> float:
    area = 0.0
    for i in range(len(outline)):
        p = outline[i]
        q = ring_at(outline, i + 1)
        area = area + p[0] * q[1] - q[0] * p[1]
    return area / 2


def build_prism_vertex_data(outline: list[OutlinePoint], thickness: float) -> PrismGeometry:
    """Extrudes a planform outline (in the XZ plane) into a flat prism of the given thickness,
    centred on Y = 0. Faces are flat-shaded (vertices are not shared between faces). The outline
    must be a simple polygon (concave is fine); either winding order is accepted."""
    if len(outline) < MIN_OUTLINE_POINTS:
        raise ValueError("A prism outline needs at least 3 points")
    # Babylon front faces: outward normal = (c - a) × (b - a); caps need a CCW outline.
    pts = reversed_copy(outline) if _signed_area(outline) < 0 else list(outline)
    h = thickness / 2
    positions: list[float] = []
    indices: list[float] = []

    def tri(a: list[float], b: list[float], c: list[float]) -> None:
        base = len(positions) // 3
        positions.extend(a)
        positions.extend(b)
        positions.extend(c)
        indices.extend([base, base + 1, base + 2])

    def at(i: int, y: float) -> list[float]:
        p = ring_at(pts, i)
        return [p[0], y, p[1]]

    for a, b, c in triangulate_polygon(pts):
        tri(at(a, h), at(b, h), at(c, h))
        tri(at(a, -h), at(c, -h), at(b, -h))
    for i in range(len(pts)):
        tri(at(i, h), at(i, -h), at(i + 1, h))
        tri(at(i + 1, h), at(i, -h), at(i + 1, -h))
    return PrismGeometry(positions, indices)


def create_prism(
    label: str,
    outline: list[OutlinePoint],
    thickness: float,
    scene: Any,
) -> Any:
    """Creates a flat-shaded prism mesh from a planform outline (see
    `build_prism_vertex_data`)."""
    geometry = build_prism_vertex_data(outline, thickness)
    normals = compute_normals(geometry.positions, geometry.indices)
    data = vertex_data_of(geometry.positions, geometry.indices, normals)
    mesh = new_mesh(label, scene)
    apply_vertex_data(data, mesh)
    return mesh
