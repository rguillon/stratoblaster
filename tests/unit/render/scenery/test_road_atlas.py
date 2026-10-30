"""Unit tests of `src/render/scenery/road_atlas.py`."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeTypedArray, patch_babylon

from render.scenery import road_atlas
from render.scenery.road_atlas import ATLAS_PX, ATLAS_SIZE, PAD, SLOT, SLOT_TILES, SLOTS, RoadAtlas


@pytest.fixture(autouse=True)
def _painter(monkeypatch: pytest.MonkeyPatch) -> list[tuple[Any, int]]:
    patch_babylon(monkeypatch, road_atlas)
    monkeypatch.setattr(road_atlas, "_uint8_array", FakeTypedArray)
    painted: list[tuple[Any, int]] = []

    def paint(piece: Any, tile: Any, look: Any, n: int) -> list[Any]:
        painted.append((piece, n))
        # A piece of one colour everywhere, so its pixels are easy to find.
        return [(1.0, 0.0, 0.0)] * (n * n)

    monkeypatch.setattr(road_atlas, "paint_piece", paint)
    return painted


def _piece(size: int, tag: int | None = None) -> Any:
    """A piece of `size` tiles. Pieces with different `tag`s have different looks (their open
    side is `tag` long)."""
    side = None if tag is None else SimpleNamespace(size=tag, offset=0)
    return SimpleNamespace(size=size, sides=[side, None, None, None])


def _look() -> Any:
    return SimpleNamespace(sidewalk=(0.0, 1.0, 0.0))


def test_the_atlas_is_a_square_of_slots_of_padded_tiles() -> None:
    assert SLOT == SLOT_TILES * ATLAS_PX + 2 * PAD
    assert ATLAS_SIZE == SLOT * SLOTS
    atlas = RoadAtlas(SimpleNamespace(), _look())
    assert len(atlas.data) == ATLAS_SIZE * ATLAS_SIZE * 4
    assert atlas.dirty is False


def test_a_new_piece_is_painted_into_the_first_slot_and_its_rect_is_returned(
    _painter: list[tuple[Any, int]],
) -> None:
    atlas = RoadAtlas(SimpleNamespace(), _look())
    rect = atlas.rect_of(_piece(2))
    assert rect == pytest.approx(
        (
            PAD / ATLAS_SIZE,
            PAD / ATLAS_SIZE,
            (PAD + 2 * ATLAS_PX) / ATLAS_SIZE,
            (PAD + 2 * ATLAS_PX) / ATLAS_SIZE,
        )
    )
    assert _painter[0][1] == 2 * ATLAS_PX
    assert atlas.dirty is True


def test_a_piece_of_the_same_look_is_not_painted_twice(
    _painter: list[tuple[Any, int]],
) -> None:
    atlas = RoadAtlas(SimpleNamespace(), _look())
    first = atlas.rect_of(_piece(1))
    atlas.dirty = False
    second = atlas.rect_of(_piece(1))
    assert second == first
    assert len(_painter) == 1
    assert atlas.dirty is False


def test_the_next_slot_is_to_the_right_then_the_next_row() -> None:
    atlas = RoadAtlas(SimpleNamespace(), _look())
    first = atlas.rect_of(_piece(1, 1))
    second = atlas.rect_of(_piece(1, 2))
    assert second[0] - first[0] == pytest.approx(SLOT / ATLAS_SIZE)
    assert second[1] == pytest.approx(first[1])
    # Slots 2 to 7 fill the first row; the next piece starts the second row.
    for i in range(3, SLOTS + 1):
        atlas.rect_of(_piece(1, i))
    row_start = atlas.rect_of(_piece(1, SLOTS + 1))
    assert row_start[0] == pytest.approx(first[0])
    assert row_start[1] - first[1] == pytest.approx(SLOT / ATLAS_SIZE)


def test_a_piece_too_big_for_a_slot_has_no_rect() -> None:
    atlas = RoadAtlas(SimpleNamespace(), _look())
    assert atlas.rect_of(_piece(SLOT_TILES + 1)) is None


def test_a_full_atlas_has_no_room_for_a_new_piece() -> None:
    atlas = RoadAtlas(SimpleNamespace(), _look())
    for i in range(SLOTS * SLOTS):
        assert atlas.rect_of(_piece(1, i)) is not None
    assert atlas.rect_of(_piece(1, -1)) is None


def test_the_painted_pixels_are_written_with_their_edges_repeated_into_the_pad(
    _painter: list[tuple[Any, int]],
) -> None:
    atlas = RoadAtlas(SimpleNamespace(), _look())
    atlas.rect_of(_piece(1))
    data = atlas.data
    # The first pixel of the tile (after the pad) is red, opaque.
    origin = ((PAD) * ATLAS_SIZE + PAD) * 4
    assert list(data[origin : origin + 4]) == [255, 0, 0, 255]
    # The pad above it repeats the tile's edge.
    above = ((PAD - 1) * ATLAS_SIZE + PAD) * 4
    assert list(data[above : above + 4]) == [255, 0, 0, 255]


def test_a_transparent_pixel_takes_the_sidewalk_colour(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(road_atlas, "paint_piece", lambda p, t, look, n: [None] * (n * n))
    atlas = RoadAtlas(SimpleNamespace(), _look())
    atlas.rect_of(_piece(1))
    origin = (PAD * ATLAS_SIZE + PAD) * 4
    assert list(atlas.data[origin : origin + 4]) == [0, 255, 0, 255]
