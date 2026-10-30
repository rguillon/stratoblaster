"""Unit tests of `src/render/scenery/road_surface.py`."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_geometry import points_of

from render.scenery import road_surface
from render.scenery.road_surface import TexturedGeometry, build_road_surfaces, cuts

TILE = SimpleNamespace(size=2)
LOOK = SimpleNamespace(lift=0.5)


class Flat:
    def height(self, x: float, z: float) -> float:
        return 0.0


class _Atlas:
    """An atlas that has room for every piece, except those in `full`."""

    def __init__(self, full: set[int] | None = None) -> None:
        self.full = full or set()

    def rect_of(self, piece: Any) -> tuple[float, float, float, float] | None:
        return None if piece.z in self.full else (0.0, 0.0, 1.0, 1.0)


def _piece(x: int, z: int, size: int = 1) -> Any:
    return SimpleNamespace(x=x, z=z, size=size)


def test_cuts_split_a_span_at_every_cell_boundary_inside_it() -> None:
    assert cuts(0, 3, 1) == pytest.approx([0, 1, 2, 3])
    assert cuts(0.5, 2.5, 1) == pytest.approx([0.5, 1, 2, 2.5])


def test_a_span_inside_one_cell_is_not_cut() -> None:
    assert cuts(0, 1, 2) == pytest.approx([0, 1])


def test_a_surface_is_a_grid_of_cells_half_a_tile_wide_with_its_texture_coordinates() -> None:
    surfaces, layered = build_road_surfaces(
        [_piece(0, 0)], TILE, LOOK, _Atlas(), Flat().height, 0, 10
    )
    assert isinstance(surfaces, TexturedGeometry)
    # A tile of size 2 is cut into 2 x 2 cells: 3 x 3 vertices and 8 triangles.
    assert len(surfaces.positions) // 3 == 9
    assert len(surfaces.indices) == 8 * 3
    assert layered.positions == []
    uvs = [surfaces.uvs[i : i + 2] for i in range(0, len(surfaces.uvs), 2)]
    assert uvs[0] == pytest.approx([0, 0])
    assert uvs[-1] == pytest.approx([1, 1])


def test_the_surface_sits_on_the_ground_lifted_by_the_look() -> None:
    surfaces, _ = build_road_surfaces([_piece(0, 0)], TILE, LOOK, _Atlas(), lambda x, z: 3.0, 0, 10)
    assert {p[1] for p in points_of(surfaces.positions)} == {3.5}


def test_a_piece_the_atlas_cannot_hold_goes_to_the_layered_geometry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    added: list[Any] = []
    monkeypatch.setattr(
        road_surface, "add_piece", lambda geo, piece, tile, look, ground: added.append(piece)
    )
    surfaces, layered = build_road_surfaces(
        [_piece(0, 5)], TILE, LOOK, _Atlas(full={5}), Flat().height, 0, 100
    )
    assert surfaces.positions == []
    assert [p.z for p in added] == [5]


def test_a_piece_is_kept_when_its_middle_is_in_the_chunk() -> None:
    # The piece starts before the chunk and its middle is inside it: it is drawn.
    surfaces, _ = build_road_surfaces(
        [_piece(0, -1, size=2)], TILE, LOOK, _Atlas(), Flat().height, 0, 100
    )
    assert len(surfaces.positions) > 0


def test_a_piece_whose_middle_is_outside_the_chunk_is_skipped() -> None:
    surfaces, layered = build_road_surfaces(
        [_piece(0, 50)], TILE, LOOK, _Atlas(), Flat().height, 0, 10
    )
    assert surfaces.positions == [] and layered.positions == []
