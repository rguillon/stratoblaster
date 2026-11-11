# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/geometry/section_loft.py` (GFX-SHIP-01, D-327)."""

import math
from types import SimpleNamespace
from typing import Any

import pytest

from render.geometry import section_loft
from render.geometry.section_loft import (
    build_section_loft,
    create_section_loft,
    polygon_lathe_sections,
    rounded_polygon,
)


def _ring(radius: float, count: int = 8, height: float = 1) -> list[list[float]]:
    """Return a ring round the axis: its first half over the top (y >= 0), then the bottom."""
    return [
        [
            radius * math.cos(2 * math.pi * k / count),
            height * radius * math.sin(2 * math.pi * k / count),
        ]
        for k in range(count)
    ]


# A spindle: a point, a ring, a wider ring, a point.
SPINDLE = [[2, _ring(0)], [1, _ring(0.5)], [0, _ring(1)], [-1, _ring(0)]]


def _faces(positions: list[float], normals: list[float]) -> list[tuple[list[float], list[float]]]:
    return [(positions[k : k + 9], normals[k : k + 9]) for k in range(0, len(positions), 9)]


def test_gfx_ship_01_the_loft_closes_on_point_sections_without_empty_triangles() -> None:
    positions, indices, normals = build_section_loft(SPINDLE, 5)
    # Two rings of 8 between the 3 bands: 8 triangles at each tip, 16 in the middle band.
    assert len(indices) == (8 + 16 + 8) * 3
    assert len(positions) == len(normals) == len(indices) * 3


def test_gfx_ship_01_the_front_normals_point_away_from_the_axis() -> None:
    """The Babylon front normal `(p2 - p0) x (p1 - p0)`, which the edge trim reads, faces out."""
    positions, _indices, normals = build_section_loft(SPINDLE, 5)
    for points, _ in _faces(positions, normals):
        p0, p1, p2 = points[0:3], points[3:6], points[6:9]
        u = [p2[k] - p0[k] for k in range(3)]
        v = [p1[k] - p0[k] for k in range(3)]
        front = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
        middle = [(p0[k] + p1[k] + p2[k]) / 3 for k in range(2)]
        assert front[0] * middle[0] + front[1] * middle[1] > 0


def test_gfx_ship_01_the_normals_are_unit_and_point_outward() -> None:
    positions, _indices, normals = build_section_loft(SPINDLE, 5)
    for k in range(0, len(positions), 3):
        n = normals[k : k + 3]
        assert math.hypot(*n) == pytest.approx(1)
    for points, ns in _faces(positions, normals):
        middle = [sum(points[i + k] for i in range(0, 9, 3)) / 3 for k in range(2)]
        assert ns[0] * middle[0] + ns[1] * middle[1] > 0


def test_gfx_ship_01_the_top_shares_its_normals_and_the_bottom_is_flat() -> None:
    positions, indices, normals = build_section_loft(SPINDLE, 5)
    seen: dict[tuple[float, ...], tuple[float, ...]] = {}
    for k in range(0, len(positions), 3):
        key = tuple(round(v, 6) for v in positions[k : k + 3])
        if key[1] > 1e-6 and abs(key[0]) < 0.999:
            n = tuple(round(v, 6) for v in normals[k : k + 3])
            assert seen.setdefault(key, n) == n
    for t in range(0, len(indices), 3):
        corners = [indices[t + j] * 3 for j in range(3)]
        if all(positions[c + 1] < -1e-6 for c in corners):
            for c in corners[1:]:
                assert normals[c : c + 3] == pytest.approx(normals[corners[0] : corners[0] + 3])


def test_gfx_ship_01_a_loft_mesh_is_made_from_its_vertex_data(monkeypatch: Any) -> None:
    made = SimpleNamespace(data=None)
    monkeypatch.setattr(section_loft, "vertex_data_of", lambda p, i, n: (p, i, n))
    monkeypatch.setattr(section_loft, "new_mesh", lambda label, _scene: SimpleNamespace(name=label))
    monkeypatch.setattr(
        section_loft, "apply_vertex_data", lambda data, _mesh: setattr(made, "data", data)
    )
    mesh = create_section_loft("hull", SPINDLE, 5, object())
    assert mesh.name == "hull"
    assert made.data is not None


def test_gfx_ship_01_an_open_end_is_closed_by_a_flat_cap_facing_out() -> None:
    """A tail cut off square (a real ring at the end) gets a flat cap facing away from the skin."""
    stub = [[2, _ring(0)], [1, _ring(0.5)], [0, _ring(1)]]
    positions, _indices, normals = build_section_loft(stub, 5)
    caps = [
        (points, ns)
        for points, ns in _faces(positions, normals)
        if all(abs(points[k]) < 1e-9 for k in [2, 5, 8])
    ]
    assert len(caps) == 8
    for _points, ns in caps:
        assert ns[2] == pytest.approx(-1)


def test_gfx_ship_01_a_hollow_keeps_its_faces_wound_like_the_rest() -> None:
    """D-327: a ring with a dip (two humps) has every face wound the same way round.

    Turned triangle by triangle, the dip's inner slopes would face the centre line and be culled.
    """
    humps = [[1, 0.4], [0.5, 0.8], [0.25, 0.3], [0, 0.25], [-0.25, 0.3], [-0.5, 0.8], [-1, 0.4]]
    belly = [[-0.5, -0.5], [0.5, -0.5]]
    ring = humps + belly
    sections = [[1, ring], [0, ring]]
    positions, _indices, normals = build_section_loft(sections, len(humps))
    for points, _ns in _faces(positions, normals):
        p0, p1, p2 = points[0:3], points[3:6], points[6:9]
        u = [p2[k] - p0[k] for k in range(3)]
        v = [p1[k] - p0[k] for k in range(3)]
        front_y = u[2] * v[0] - u[0] * v[2]
        middle_y = (p0[1] + p1[1] + p2[1]) / 3
        # Over the top, every front faces up, the dip's slopes included (the end caps aside).
        on_the_skin = len({p0[2], p1[2], p2[2]}) > 1
        if on_the_skin and middle_y > 0.2:
            assert front_y > 0


def test_eng_rounded_polygon_rounds_the_corners_and_keeps_the_sides() -> None:
    """D-330: a rounded hexagon: 3 points a corner, inside the sharp one, its sides kept."""
    ring = rounded_polygon(6, 1.0, 0.3, 3)
    assert len(ring) == 18
    apothem = math.cos(math.pi / 6)
    for x, y in ring:
        assert math.hypot(x, y) <= 1.0 + 1e-9
        assert math.hypot(x, y) >= apothem - 1e-9
    # The tangent points lie on the sharp hexagon's sides: at the apothem, square to them.
    first = ring[0]
    side_normal = [math.cos(-math.pi / 6), math.sin(-math.pi / 6)]
    assert first[0] * side_normal[0] + first[1] * side_normal[1] == pytest.approx(apothem)
    # The middle of the first corner's arc is on +X, short of the sharp corner.
    assert ring[1][1] == pytest.approx(0)
    assert ring[1][0] < 1.0
    assert all(p == pytest.approx([0, 0]) for p in rounded_polygon(6, 0, 0.3, 3))


def test_eng_a_polygon_lathe_is_a_section_per_profile_point() -> None:
    sections = polygon_lathe_sections([[1, 0], [0.5, 0.2], [0, 0]], 6, 0.3, 3)
    assert [z for z, _ring in sections] == [1, 0.5, 0]
    positions, indices, _normals = build_section_loft(sections, 18)
    assert len(indices) == len(positions) // 3
    assert len(indices) > 0
