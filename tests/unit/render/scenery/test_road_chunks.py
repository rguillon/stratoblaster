"""Unit tests of `src/render/scenery/road_chunks.py`."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import patch_babylon

from render.scenery import road_chunks
from render.scenery.road_chunks import GRID_COLOR, TileRoadChunks


class Ground:
    def height(self, x: float, z: float) -> float:
        return x + z


@pytest.fixture
def chunks(monkeypatch: pytest.MonkeyPatch) -> TileRoadChunks:
    patch_babylon(monkeypatch, road_chunks)
    pieces = [SimpleNamespace(x=0, z=0, size=1)]
    monkeypatch.setattr(road_chunks, "cached_road_pieces", lambda roads, tiles: pieces)
    monkeypatch.setattr(road_chunks, "RoadAtlas", _FakeAtlas)
    monkeypatch.setattr(
        road_chunks,
        "build_road_surfaces",
        lambda pieces, tiles, look, atlas, height, z_min, z_max: (
            ("surfaces", z_min, z_max, height(1, 2)),
            ("layered", len(pieces)),
        ),
    )
    monkeypatch.setattr(
        road_chunks,
        "build_tile_grid",
        lambda pieces, tiles, height, z_min, z_max, colour: ("grid", colour),
    )
    return TileRoadChunks(["roads"], "tiles", "look", Ground())


class _FakeAtlas:
    def __init__(self, tiles: Any, look: Any) -> None:
        self.data = "pixels"
        self.dirty = True


def test_a_chunk_has_its_surfaces_its_layered_pieces_and_no_grid(chunks: TileRoadChunks) -> None:
    chunk = chunks.chunk(3, 0, 10, grid=False)
    assert chunk.index == 3
    assert chunk.surfaces == ("surfaces", 0, 10, 3)
    assert chunk.layered == ("layered", 1)
    assert chunk.grid is None


def test_a_chunk_with_the_grid_option_has_the_tile_grid(chunks: TileRoadChunks) -> None:
    chunk = chunks.chunk(0, 0, 10, grid=True)
    assert chunk.grid == ("grid", GRID_COLOR)


def test_the_atlas_pixels_are_sent_once_after_they_change(chunks: TileRoadChunks) -> None:
    assert chunks.atlas_changed() is True
    assert chunks.atlas_pixels() == "pixels"
    assert chunks.atlas_changed() is False
