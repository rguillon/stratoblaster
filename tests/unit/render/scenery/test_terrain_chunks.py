"""Unit tests of `src/render/scenery/terrain_chunks.py`."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeNode, FakeScene, patch_babylon

from render.scenery import terrain_chunks, terrain_geometry
from render.scenery.terrain_chunks import TerrainChunkOptions, TerrainChunks


class Slope:
    def height(self, x: float, z: float) -> float:
        return z * 0.1

    def surface(self, z: float) -> Any:
        return None


class _Recorder:
    def __init__(self) -> None:
        self.updates: list[tuple[str, FakeNode]] = []
        self.updatable: list[FakeNode] = []


@pytest.fixture
def rec(monkeypatch: pytest.MonkeyPatch) -> _Recorder:
    patch_babylon(monkeypatch, terrain_chunks)
    patch_babylon(monkeypatch, terrain_geometry)
    recorder = _Recorder()

    def new_mesh(label: str, scene: FakeScene) -> FakeNode:
        node = scene.add_node(label, is_mesh=True)
        node.refreshBoundingInfo = lambda: None  # type: ignore[attr-defined]
        return node

    def apply_updatable(data: Any, mesh: FakeNode) -> None:
        recorder.updatable.append(mesh)

    def update(mesh: FakeNode, kind: str, values: Any) -> None:
        recorder.updates.append((kind, mesh))

    monkeypatch.setattr(terrain_chunks, "new_mesh", new_mesh)
    monkeypatch.setattr(terrain_chunks, "new_vertex_data", SimpleNamespace)
    monkeypatch.setattr(terrain_chunks, "apply_vertex_data_updatable", apply_updatable)
    monkeypatch.setattr(terrain_chunks, "update_vertices_data", update)
    monkeypatch.setattr(terrain_chunks, "vertex_buffer_kind", lambda key: key)
    monkeypatch.setattr(terrain_chunks, "_empty_map", dict)
    monkeypatch.setattr(terrain_chunks, "_map_size", len)
    monkeypatch.setattr(terrain_chunks, "_map_keys", list)
    monkeypatch.setattr(terrain_chunks, "_map_get", lambda c, k: c[k])
    monkeypatch.setattr(terrain_chunks, "_map_has", lambda c, k: k in c)
    monkeypatch.setattr(terrain_chunks, "_map_set", lambda c, k, v: c.__setitem__(k, v))
    monkeypatch.setattr(terrain_chunks, "_map_delete", lambda c, k: c.pop(k))
    return recorder


def _chunks(**overrides: Any) -> TerrainChunks:
    values: dict[str, Any] = {"length": 10, "cell": 2, "x_min": -4, "columns": 4}
    values.update(overrides)
    options = TerrainChunkOptions(
        values["length"], values["cell"], values["x_min"], values["columns"]
    )
    return TerrainChunks(FakeScene(), "material", options, Slope())


def test_a_chunk_spans_its_length_along_z(rec: _Recorder) -> None:
    chunks = _chunks()
    span = chunks.span(3)
    assert (span.index, span.z_min, span.z_max) == (3, 30, 40)


def test_the_rows_of_a_chunk_follow_its_length_and_cell_size(rec: _Recorder) -> None:
    chunks = _chunks(length=10, cell=2)
    assert chunks._rows == 5


def test_covering_a_stretch_adds_the_chunks_it_touches(rec: _Recorder) -> None:
    chunks = _chunks()
    changes = chunks.cover(0, 25)
    assert [s.index for s in changes.added] == [0, 1, 2]
    assert changes.removed == []
    assert chunks.count == 3


def test_chunks_that_scroll_out_of_view_are_hidden_and_their_meshes_reused(
    rec: _Recorder,
) -> None:
    chunks = _chunks()
    chunks.cover(0, 25)
    first_mesh = chunks.meshes[0]
    changes = chunks.cover(15, 25)
    assert changes.removed == [0]
    assert [s.index for s in changes.added] == []
    assert first_mesh.enabled is False
    # A new chunk takes a hidden mesh rather than a new one: the scene still has 3 meshes.
    changes = chunks.cover(40, 45)
    assert [s.index for s in changes.added] == [4]
    assert len(chunks.scene.meshes) == 3
    assert chunks.meshes[4].enabled is True


def test_a_new_mesh_is_an_unpickable_shadow_receiver_with_the_material(rec: _Recorder) -> None:
    seen: list[FakeNode] = []
    options = TerrainChunkOptions(10, 2, 0, 2)
    chunks = TerrainChunks(FakeScene(), "terrain", options, Slope(), on_mesh=seen.append)
    chunks.cover(0, 5)
    (mesh,) = seen
    assert mesh.material == "terrain"
    assert mesh.isPickable is False
    assert mesh.receiveShadows is True
    assert mesh.enabled is True


def test_filling_a_chunk_updates_its_three_vertex_buffers(rec: _Recorder) -> None:
    chunks = _chunks()
    chunks.cover(0, 5)
    kinds = [kind for kind, _ in rec.updates]
    assert kinds == ["PositionKind", "NormalKind", "ColorKind"]


def test_a_rebuild_refills_every_live_chunk_with_the_new_source(rec: _Recorder) -> None:
    chunks = _chunks()
    chunks.cover(0, 25)
    rec.updates.clear()
    chunks.rebuild(Slope())
    assert len(rec.updates) == 3 * chunks.count
