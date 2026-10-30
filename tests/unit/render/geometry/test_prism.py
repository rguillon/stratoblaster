"""Unit tests of `src/render/geometry/prism.py`."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_geometry import enclosed_volume, triangles

from render.geometry import prism
from render.geometry.prism import build_prism_vertex_data, create_prism

SQUARE = [[-1, -1], [1, -1], [1, 1], [-1, 1]]
# Clockwise seen from above (+Y): the same square, given the other way round.
SQUARE_CW = [[-1, -1], [-1, 1], [1, 1], [1, -1]]
L_SHAPE = [[0, 0], [2, 0], [2, 1], [1, 1], [1, 2], [0, 2]]


def test_a_square_prism_has_caps_and_side_faces() -> None:
    geo = build_prism_vertex_data(SQUARE, 2)
    tris = triangles(geo.positions, geo.indices)
    # Two triangles per cap (4) and two per side face (4 sides): 12 triangles, 36 vertices.
    assert len(tris) == 12
    assert len(geo.positions) == 36 * 3


@pytest.mark.parametrize(
    ("outline", "area"),
    [(SQUARE, 4), (SQUARE_CW, 4), (L_SHAPE, 3)],
    ids=["ccw-square", "cw-square", "l-shape"],
)
def test_the_faces_enclose_the_outline_area_times_the_thickness(
    outline: list[list[float]], area: float
) -> None:
    geo = build_prism_vertex_data(outline, 1)
    assert enclosed_volume(geo.positions, geo.indices) == pytest.approx(area)


def test_caps_sit_at_plus_and_minus_half_the_thickness() -> None:
    geo = build_prism_vertex_data(SQUARE, 4)
    ys = sorted({round(p[1], 9) for tri in triangles(geo.positions, geo.indices) for p in tri})
    assert ys == [-2, 2]


def test_the_winding_of_the_outline_does_not_matter() -> None:
    ccw = build_prism_vertex_data(SQUARE, 2)
    cw = build_prism_vertex_data(SQUARE_CW, 2)
    assert len(ccw.indices) == len(cw.indices)
    assert enclosed_volume(cw.positions, cw.indices) == pytest.approx(8)


def test_an_outline_needs_three_points() -> None:
    with pytest.raises(ValueError, match="at least 3 points"):
        build_prism_vertex_data([[0, 0], [1, 0]], 1)


def test_create_prism_hands_the_geometry_to_a_new_mesh(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, Any]] = []

    def fake_normals(positions: list[float], indices: list[Any]) -> str:
        calls.append(("normals", len(indices)))
        return "N"

    def fake_data(positions: list[float], indices: list[Any], normals: str) -> str:
        calls.append(("data", normals))
        return "D"

    def fake_mesh(label: str, scene: Any) -> SimpleNamespace:
        calls.append(("mesh", label, scene))
        return SimpleNamespace(label=label)

    def fake_apply(data: str, mesh: Any) -> None:
        calls.append(("apply", data, mesh.label))

    monkeypatch.setattr(prism, "compute_normals", fake_normals)
    monkeypatch.setattr(prism, "vertex_data_of", fake_data)
    monkeypatch.setattr(prism, "new_mesh", fake_mesh)
    monkeypatch.setattr(prism, "apply_vertex_data", fake_apply)

    mesh = create_prism("hull", SQUARE, 1, "scene")

    assert mesh.label == "hull"
    assert calls == [
        ("normals", 36),
        ("data", "N"),
        ("mesh", "hull", "scene"),
        ("apply", "D", "hull"),
    ]
