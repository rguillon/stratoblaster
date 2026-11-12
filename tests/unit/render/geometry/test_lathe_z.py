# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/geometry/lathe_z.py` (GFX-ART-02, GFX-ART-09)."""

import math
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_geometry import babylon_normal, centroid, dot, triangles

from render.geometry import lathe_z
from render.geometry.lathe_z import (
    LatheHalves,
    build_faceted_lathe_vertex_data,
    build_smooth_top_lathe_vertex_data,
    create_faceted_lathe_along_z,
    create_lathe_along_z,
    create_smooth_top_lathe_along_z,
    section_angles,
    smooth_profile,
)

# A closed cone: a point at the tail (z = 0), a rim of radius 1 at z = 1, a point at the nose.
CONE = [[0, 0], [1, 1], [2, 0]]


def test_section_angles_of_a_whole_number_of_sides() -> None:
    angles = section_angles(4)
    assert angles == pytest.approx([0, math.pi / 2, math.pi, 3 * math.pi / 2])


def test_section_angles_of_halves_put_a_vertex_on_minus_x() -> None:
    angles = section_angles(LatheHalves(2, 2))
    assert angles == pytest.approx([0, math.pi / 2, math.pi, math.pi + math.pi / 2])


def test_a_profile_running_backwards_gives_the_same_body() -> None:
    forward = build_faceted_lathe_vertex_data(CONE, 6)
    backward = build_faceted_lathe_vertex_data(list(reversed(CONE)), 6)
    assert forward == backward


def test_a_closed_cone_has_one_triangle_per_facet_and_segment() -> None:
    positions, indices = build_faceted_lathe_vertex_data(CONE, 6)
    # Two segments, six facets each: the point at the axis gives one triangle, not two.
    assert len(indices) // 3 == 2 * 6
    assert len(positions) // 3 == len(indices)


def test_every_triangle_faces_away_from_the_axis() -> None:
    positions, indices = build_faceted_lathe_vertex_data(CONE, 8)
    for tri in triangles(positions, indices):
        radial = [centroid(tri)[0], centroid(tri)[1], 0]
        assert dot(babylon_normal(tri), radial) > 0


def test_a_tapering_profile_faces_out_with_halves_too() -> None:
    body = [[0, 0], [1, 1], [2, 1.5], [3, 0]]
    positions, indices = build_faceted_lathe_vertex_data(body, LatheHalves(3, 2))
    for tri in triangles(positions, indices):
        radial = [centroid(tri)[0], centroid(tri)[1], 0]
        assert dot(babylon_normal(tri), radial) > 0


def test_create_lathe_along_z_turns_the_mesh_onto_the_z_axis(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    shapes: list[Any] = []

    def fake_vector3(x: float, y: float, z: float) -> tuple[float, float, float]:
        return (x, y, z)

    def fake_create_lathe(label: str, shape: list[Any], tess: int, scene: Any) -> SimpleNamespace:
        shapes.append((label, shape, tess, scene))
        return SimpleNamespace(rotation=SimpleNamespace(x=0.0), baked=False)

    def fake_bake(mesh: SimpleNamespace) -> None:
        mesh.baked = True

    monkeypatch.setattr(lathe_z, "vector3", fake_vector3)
    monkeypatch.setattr(lathe_z, "create_lathe", fake_create_lathe)
    monkeypatch.setattr(lathe_z, "bake_transform", fake_bake)

    # Given from nose to tail: the shape is reversed so the faces point out.
    mesh = create_lathe_along_z("body", [[2, 0], [1, 1], [0, 0]], "scene", tessellation=5)

    assert shapes == [("body", [(0, 0, 0), (1, 1, 0), (0, 2, 0)], 5, "scene")]
    assert mesh.rotation.x == pytest.approx(math.pi / 2)
    assert mesh.baked


def test_create_faceted_lathe_hands_the_geometry_to_a_new_mesh(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[Any] = []
    monkeypatch.setattr(lathe_z, "compute_normals", lambda _p, _i: "N")
    monkeypatch.setattr(lathe_z, "vertex_data_of", lambda _p, _i, n: ("D", n))
    monkeypatch.setattr(lathe_z, "new_mesh", lambda label, _scene: SimpleNamespace(label=label))
    monkeypatch.setattr(lathe_z, "apply_vertex_data", lambda d, m: seen.append((d, m.label)))

    create_faceted_lathe_along_z("hull", CONE, 4, "scene")

    assert seen == [(("D", "N"), "hull")]


def test_smooth_profile_keeps_every_point_and_cuts_each_segment() -> None:
    profile = [[2, 0], [1, 0.5], [0, 0.4], [-1, 0]]
    smooth = smooth_profile(profile, 4)
    assert len(smooth) == 3 * 4 + 1
    for k, point in enumerate(profile):
        assert smooth[k * 4] == pytest.approx(point)
    assert all(p[1] >= 0 for p in smooth)


def test_smooth_profile_with_one_step_is_a_copy() -> None:
    assert smooth_profile(CONE, 1) == CONE
    assert smooth_profile([[0, 1]], 4) == [[0, 1]]


def test_a_smooth_top_lathe_has_the_faceted_lathes_triangles() -> None:
    halves = LatheHalves(8, 3)
    positions, indices, normals = build_smooth_top_lathe_vertex_data(CONE, halves)
    faceted_positions, faceted_indices = build_faceted_lathe_vertex_data(CONE, halves)
    assert positions == pytest.approx(faceted_positions)
    assert indices == faceted_indices
    assert len(normals) == len(positions)


def test_a_smooth_top_lathes_normals_are_unit_and_point_outward() -> None:
    profile = [[0, 0], [0.5, 0.8], [1.5, 1], [2, 0]]
    positions, _indices, normals = build_smooth_top_lathe_vertex_data(profile, LatheHalves(8, 3))
    for k in range(0, len(positions), 3):
        n = normals[k : k + 3]
        assert math.hypot(*n) == pytest.approx(1)
        radial = [positions[k], positions[k + 1]]
        if math.hypot(*radial) > 1e-9:
            assert n[0] * radial[0] + n[1] * radial[1] > 0


def test_a_smooth_top_shares_normals_across_facets_and_the_belly_is_flat() -> None:
    """The top's vertices at one point and angle share their normal.

    Each belly triangle has one normal.
    """
    profile = [[0, 0], [1, 1], [2, 1], [3, 0]]
    positions, indices, normals = build_smooth_top_lathe_vertex_data(profile, LatheHalves(6, 3))
    seen: dict[tuple[float, float, float], tuple[float, float, float]] = {}
    for k in range(0, len(positions), 3):
        key = tuple(round(v, 6) for v in positions[k : k + 3])
        normal = tuple(round(v, 6) for v in normals[k : k + 3])
        if key[1] > 1e-6:
            assert seen.setdefault(key, normal) == normal
    for t in range(0, len(indices), 3):
        corners = [indices[t + j] * 3 for j in range(3)]
        if all(positions[c + 1] < -1e-6 for c in corners):
            first = normals[corners[0] : corners[0] + 3]
            for c in corners[1:]:
                assert normals[c : c + 3] == pytest.approx(first)


def test_a_smooth_top_lathe_is_made_from_its_vertex_data(monkeypatch: Any) -> None:
    made = SimpleNamespace(data=None)
    monkeypatch.setattr(lathe_z, "vertex_data_of", lambda p, i, n: (p, i, n))
    monkeypatch.setattr(lathe_z, "new_mesh", lambda label, _scene: SimpleNamespace(name=label))
    monkeypatch.setattr(
        lathe_z, "apply_vertex_data", lambda data, _mesh: setattr(made, "data", data)
    )
    mesh = create_smooth_top_lathe_along_z("hull", CONE, LatheHalves(4, 2), object())
    assert mesh.name == "hull"
    assert made.data is not None


def test_a_point_where_the_profile_does_not_move_faces_straight_out() -> None:
    """A repeated profile point has no slope: its normal points away from the axis."""
    normal = lathe_z._surface_normal(math.pi / 2, 0, 0)
    assert normal == pytest.approx([0, 1, 0], abs=1e-12)
