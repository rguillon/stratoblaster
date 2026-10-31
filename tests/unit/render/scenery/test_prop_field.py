"""Unit tests of the chunks of `src/render/scenery/prop_field.py`: their placements and instance
matrices (D-212: a chunk's trees come a row at a time), on a field made without models (its
meshes set by hand)."""

from typing import Any

import pytest
from helpers.render_fakes import FakeTypedArray, patch_babylon

from core.scenery.ground_boxes import PropPlacement
from render.scenery import prop_field
from render.scenery.prop_field import (
    MATRIX_FLOATS,
    KindProps,
    PropField,
    PropMeshes,
    _matrices_for,
)

MADE: list[int] = []


def _fake_matrices(placements: list[PropPlacement]) -> Any:
    """One matrix per placement, all of its X (so a matrix tells which placement it is)."""
    MADE.append(len(placements))
    buffer = FakeTypedArray(len(placements) * MATRIX_FLOATS)
    for i, p in enumerate(placements):
        buffer.set([p.x] * MATRIX_FLOATS, i * MATRIX_FLOATS)
    return buffer


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_babylon(monkeypatch, prop_field)
    monkeypatch.setattr(prop_field, "instance_matrices", _fake_matrices)
    MADE.clear()


def tree(x: float, z: float) -> PropPlacement:
    return PropPlacement("tree", x, 0, z, 0, 1)


def field() -> PropField:
    f = PropField(None, {}, None)
    f._meshes = {"tree": PropMeshes(None, None, []), "hut": PropMeshes(None, None, [])}
    return f


def test_d212_trees_added_to_a_chunk_join_its_props() -> None:
    f = field()
    f.set_chunk(3, [PropPlacement("hut", 0, 0, 10, 0, 1)])
    f.add_to_chunk(3, [tree(1, 20), tree(2, 30)])
    f.add_to_chunk(3, [tree(3, 40)])
    assert f.count == 4
    assert [p.x for p in f._chunk_kinds[0]["tree"].placements] == [1, 2, 3]


def test_d212_trees_added_to_a_chunk_that_is_gone_are_dropped() -> None:
    f = field()
    f.set_chunk(3, [tree(1, 20)])
    f.remove_chunk(3)
    f.add_to_chunk(3, [tree(2, 30)])
    assert f.count == 0
    assert f._chunk_indices == []


def test_d212_trees_added_out_of_the_window_upload_nothing() -> None:
    f = field()
    f.set_chunk(3, [tree(1, 20)])
    f.set_window(0, 100, 10)
    f._dirty = False
    f.add_to_chunk(3, [tree(2, 500)])
    assert not f._dirty
    f.add_to_chunk(3, [tree(3, 50)])
    assert f._dirty


def test_a_chunk_set_again_replaces_its_props_and_a_missing_one_is_removed_quietly() -> None:
    f = field()
    f.set_chunk(1, [tree(1, 20)])
    f.set_chunk(2, [tree(2, 20)])
    f.set_chunk(1, [tree(3, 20), tree(4, 20)])
    assert f._chunk_indices == [1, 2]
    assert f.count == 3
    f._dirty = False
    f.remove_chunk(9)
    assert not f._dirty
    f.remove_chunk(1)
    assert f._dirty
    assert f._chunk_indices == [2]


def test_a_prop_without_a_model_is_refused() -> None:
    f = field()
    with pytest.raises(ValueError, match="No model"):
        f.set_chunk(1, [PropPlacement("ufo", 0, 0, 0, 0, 1)])
    f.set_chunk(1, [])
    with pytest.raises(ValueError, match="No model"):
        f.add_to_chunk(1, [PropPlacement("ufo", 0, 0, 0, 0, 1)])


def test_d212_the_matrices_are_made_once_and_only_those_of_new_trees_after() -> None:
    props = KindProps([tree(1, 0), tree(2, 0)])
    first = _matrices_for(props)
    # Made in one go the first time, and kept.
    assert MADE == [2]
    assert _matrices_for(props) is first
    assert MADE == [2]
    props.placements.append(tree(3, 0))
    grown = _matrices_for(props)
    assert MADE == [2, 1]
    assert list(grown) == [1] * MATRIX_FLOATS + [2] * MATRIX_FLOATS + [3] * MATRIX_FLOATS
    assert props.matrices is grown
