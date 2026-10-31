"""Unit tests of `src/render/scenery/road_sources.py` (D-217: the road atlas reaches every chunk
taken, from every stage on the same ground)."""

from types import SimpleNamespace
from typing import Any

import pytest

from render.scenery import road_sources
from render.scenery.road_sources import LocalRoadSource, WorkerRoadSource


class FakeRoadChunks:
    """A `TileRoadChunks`: the chunks in `grows` add to its atlas the first time they are made
    (made again, their pieces are in it already)."""

    made: list["FakeRoadChunks"] = []

    def __init__(self, roads: Any, tiles: Any, look: Any, ground: Any) -> None:
        self.look = look
        self.grows: set[int] = set()
        self.pixels = ["atlas of " + str(look)]
        self._dirty = False
        FakeRoadChunks.made.append(self)

    def chunk(self, index: int, z_min: float, z_max: float, grid: bool) -> Any:
        if index in self.grows:
            self.grows.discard(index)
            self.pixels.append(index)
            self._dirty = True
        return SimpleNamespace(index=index, atlas=None, atlas_version=0)

    def atlas_changed(self) -> bool:
        return self._dirty

    def atlas_pixels(self) -> Any:
        self._dirty = False
        return self.pixels


@pytest.fixture(autouse=True)
def _objects(monkeypatch: pytest.MonkeyPatch) -> None:
    """The plain JavaScript objects of the sources, as dicts; the road chunks, faked."""
    FakeRoadChunks.made = []
    monkeypatch.setattr(road_sources, "_new_object", dict)
    monkeypatch.setattr(road_sources, "_has", lambda c, k: k in c)
    monkeypatch.setattr(road_sources, "_get", lambda c, k: c[k])
    monkeypatch.setattr(road_sources, "_set", lambda c, k, v: c.__setitem__(k, v))
    monkeypatch.setattr(road_sources, "_delete", lambda c, k: c.pop(k, None))
    monkeypatch.setattr(road_sources, "TileRoadChunks", FakeRoadChunks)


def _span(index: int) -> list[Any]:
    return [index, index * 320, (index + 1) * 320]


def _local(look: Any, grows: set[int]) -> LocalRoadSource:
    source = LocalRoadSource("roads", "tiles", "ground")
    source.request([], look, False)
    FakeRoadChunks.made[-1].grows = grows
    return source


def test_d217_every_chunk_taken_carries_the_latest_atlas() -> None:
    look = "streets"
    source = _local(look, {0})
    source.request([_span(0), _span(1)], look, False)
    first = source.take(0)
    second = source.take(1)
    assert first.atlas is not None
    assert first.atlas_version == 1
    # The second chunk did not change the atlas: it still carries it, at the same version.
    assert second.atlas is first.atlas
    assert second.atlas_version == 1


def test_d217_a_second_stage_on_the_same_ground_gets_the_atlas() -> None:
    # A Retry: the ground is kept with its source, and the new stage asks for the chunks again.
    look = "streets"
    source = _local(look, {0})
    source.request([_span(0)], look, False)
    assert source.take(0).atlas is not None
    source.request([_span(0)], look, False)
    again = source.take(0)
    assert again.atlas is not None
    assert again.atlas_version == 1


def test_d217_the_atlas_version_grows_each_time_it_changes() -> None:
    look = "streets"
    source = _local(look, {0, 2})
    source.request([_span(0), _span(1), _span(2)], look, False)
    assert [source.take(i).atlas_version for i in range(3)] == [2, 2, 2]


def test_d217_another_look_drops_the_old_look_s_atlas() -> None:
    source = _local("old", {0})
    source.request([_span(0)], "old", False)
    source.request([_span(1)], "new", False)
    taken = source.take(1)
    # The new look's chunk made no atlas yet: the old one would not fit its texture coordinates.
    assert taken.atlas is None
    assert source.take(0) is None


def test_d217_the_worker_s_atlas_reaches_every_chunk_taken() -> None:
    asked: list[Any] = []
    source = WorkerRoadSource(lambda spans, look, grid, done: asked.append((spans, done)))
    source.request([_span(0), _span(1)], "streets", False)
    spans, done = asked[0]
    assert [s[0] for s in spans] == [0, 1]
    chunks = [SimpleNamespace(index=i, atlas=None, atlas_version=0) for i in range(2)]
    done(SimpleNamespace(chunks=chunks, atlas=["pixels"]))
    assert source.take(0).atlas == ["pixels"]
    assert source.take(1).atlas == ["pixels"]
    # Asked again (a Retry on the same ground), the worker sends no atlas: the source still has it.
    source.request([_span(0)], "streets", False)
    _, done = asked[1]
    chunk = SimpleNamespace(index=0, atlas=None, atlas_version=0)
    done(SimpleNamespace(chunks=[chunk], atlas=None))
    again = source.take(0)
    assert again.atlas == ["pixels"]
    assert again.atlas_version == 1


def test_d217_a_new_atlas_from_the_worker_replaces_the_old_one() -> None:
    asked: list[Any] = []
    source = WorkerRoadSource(lambda spans, look, grid, done: asked.append(done))
    source.request([_span(0)], "streets", False)
    source.request([_span(1)], "streets", False)
    asked[0](SimpleNamespace(chunks=[SimpleNamespace(index=0, atlas=None)], atlas=["a"]))
    asked[1](SimpleNamespace(chunks=[SimpleNamespace(index=1, atlas=None)], atlas=["a", "b"]))
    first = source.take(0)
    assert first.atlas == ["a", "b"]
    assert first.atlas_version == 2
    assert source.take(5) is None
