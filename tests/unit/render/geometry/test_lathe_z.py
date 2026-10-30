"""Unit tests of `src/render/geometry/lathe_z.py`."""

import math
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_geometry import babylon_normal, centroid, dot, triangles

from render.geometry import lathe_z
from render.geometry.lathe_z import (
    LatheHalves,
    build_faceted_lathe_vertex_data,
    create_faceted_lathe_along_z,
    create_lathe_along_z,
    section_angles,
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
    monkeypatch.setattr(lathe_z, "compute_normals", lambda p, i: "N")
    monkeypatch.setattr(lathe_z, "vertex_data_of", lambda p, i, n: ("D", n))
    monkeypatch.setattr(lathe_z, "new_mesh", lambda label, scene: SimpleNamespace(label=label))
    monkeypatch.setattr(lathe_z, "apply_vertex_data", lambda d, m: seen.append((d, m.label)))

    create_faceted_lathe_along_z("hull", CONE, 4, "scene")

    assert seen == [(("D", "N"), "hull")]
