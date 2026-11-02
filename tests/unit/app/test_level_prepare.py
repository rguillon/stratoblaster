# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/level_prepare.py`."""
# (PERF-11, PERF-12, PERF-18): the level choices made ahead of play.

import itertools
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app import level_prepare
from app.level_prepare import (
    PREFETCH_AFTER,
    LevelPrefetcher,
    level_of,
    prefetch_level,
    prepare_level,
    scenery_with_runout,
    textures_ready,
)


def level(level_id: str, runout: float | None = 2.0) -> SimpleNamespace:
    scenery = SimpleNamespace(id=f"scenery-{level_id}", seed=7)
    return SimpleNamespace(id=level_id, scenery=scenery, runout=runout)


def game(*levels: SimpleNamespace) -> SimpleNamespace:
    looks = {
        level.scenery.id: SimpleNamespace(roads=SimpleNamespace(tiles=None)) for level in levels
    }
    return SimpleNamespace(
        game_levels=list(levels),
        view=SimpleNamespace(scenery=SimpleNamespace(looks=looks)),
    )


@pytest.fixture
def ground(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Return the ground request of the render layer: recorded, and ready at once."""
    request = MagicMock(return_value=True)
    monkeypatch.setattr(level_prepare, "request_level_ground", request)
    monkeypatch.setattr(
        level_prepare, "with_runout", lambda scenery, runout: ("with-runout", scenery.id, runout)
    )
    return request


def test_perf_08_a_level_is_found_by_its_id_and_an_unknown_one_is_refused() -> None:
    first = level("1-1")
    assert level_of(game(first, level("1-2")), "1-1") is first
    with pytest.raises(ValueError, match="cannot be played"):
        level_of(game(first), "9-9")


@pytest.mark.usefixtures("ground")
def test_perf_11_the_scenery_gets_its_runout_once_per_level() -> None:
    """Also GAME-LEVEL-08 (the runout)."""
    first = level("1-1", runout=3.0)
    scenery = scenery_with_runout(first)
    assert scenery == ("with-runout", "scenery-1-1", 3.0)
    assert scenery_with_runout(first) is scenery


@pytest.mark.usefixtures("ground")
def test_game_level_08_a_level_without_a_runout_gets_none_of_it() -> None:
    scenery = scenery_with_runout(level("1-2", runout=None))
    assert scenery == ("with-runout", "scenery-1-2", 0)


def test_perf_14_preparing_a_level_asks_for_its_ground(ground: MagicMock) -> None:
    assert prepare_level(game(level("1-1")), "1-1") is True
    ground.assert_called_once()


def test_perf_12_prefetching_needs_a_background_loader(ground: MagicMock) -> None:
    prefetch_level(game(level("1-1")), "1-1", None)
    ground.assert_not_called()


def test_perf_12_prefetching_a_level_makes_its_ground_and_its_textures(
    ground: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    jobs = ["texture-a"]
    monkeypatch.setattr(level_prepare, "scenery_texture_jobs", lambda _look, _seed: jobs)
    loader = MagicMock()
    fake = game(level("1-1"))
    prefetch_level(fake, "1-1", loader)
    ground.assert_called_once()
    loader.prefetch_textures.assert_called_once_with(jobs)


def test_perf_12_no_level_chosen_prefetches_nothing(ground: MagicMock) -> None:
    prefetch_level(game(level("1-1")), None, MagicMock())
    ground.assert_not_called()


def test_perf_12_the_prefetcher_waits_for_the_highlight_to_rest(
    ground: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(level_prepare, "scenery_texture_jobs", lambda _look, _seed: [])
    fetcher = LevelPrefetcher(game(level("1-1"), level("1-2")), MagicMock())
    fetcher.update(PREFETCH_AFTER / 2, "1-1")
    ground.assert_not_called()
    fetcher.update(PREFETCH_AFTER, "1-1")
    ground.assert_called_once()
    fetcher.update(1.0, "1-1")
    ground.assert_called_once()


def test_perf_12_moving_across_the_grid_does_not_queue_each_level(
    ground: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(level_prepare, "scenery_texture_jobs", lambda _look, _seed: [])
    fetcher = LevelPrefetcher(game(level("1-1"), level("1-2")), MagicMock())
    fetcher.update(0.1, "1-1")
    fetcher.update(0.1, "1-2")
    fetcher.update(0.1, None)
    ground.assert_not_called()


@pytest.mark.usefixtures("ground")
def test_perf_13_the_rested_level_is_reported_once_the_rest_is_long_enough(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(level_prepare, "scenery_texture_jobs", lambda _look, _seed: [])
    fetcher = LevelPrefetcher(game(level("1-1")), MagicMock())
    fetcher.update(0.3, "1-1")
    assert fetcher.rested_on(0.0) == "1-1"
    assert fetcher.rested_on(1.0) is None


def test_perf_12_starting_a_level_prefetches_it_at_once_only_once(
    ground: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(level_prepare, "scenery_texture_jobs", lambda _look, _seed: [])
    fetcher = LevelPrefetcher(game(level("1-1")), MagicMock())
    fetcher.start("1-1")
    fetcher.start("1-1")
    ground.assert_called_once()


def test_perf_09_textures_are_waited_for_only_while_the_worker_makes_them(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jobs = ["a", "b"]
    monkeypatch.setattr(level_prepare, "scenery_texture_jobs", lambda _look, _seed: jobs)
    made = {"a"}
    monkeypatch.setattr(level_prepare, "has_texture", lambda job: job in made)
    loader = MagicMock()
    fake = game(level("1-1"))
    assert textures_ready(fake, "1-1", loader, 0) is False
    loader.prefetch_textures.assert_called_with(jobs)
    made.add("b")
    assert textures_ready(fake, "1-1", loader, 1) is True


def test_perf_18_without_a_worker_or_after_the_wait_the_scene_makes_its_textures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(level_prepare, "scenery_texture_jobs", lambda _look, _seed: ["a"])
    monkeypatch.setattr(level_prepare, "has_texture", lambda _job: False)
    fake = game(level("1-1"))
    assert textures_ready(fake, "1-1", None, 0) is True
    assert textures_ready(fake, "1-1", MagicMock(), level_prepare.TEXTURE_WAIT_FRAMES + 1) is True


def test_perf_12_a_level_without_a_look_prefetches_only_its_ground(ground: MagicMock) -> None:
    fake = game(level("1-1"))
    fake.view.scenery.looks = {}
    loader = MagicMock()
    prefetch_level(fake, "1-1", loader)
    ground.assert_called_once()
    loader.prefetch_textures.assert_not_called()


def test_perf_18_a_level_without_a_look_makes_no_texture() -> None:
    fake = game(level("1-1"))
    fake.view.scenery.looks = {}
    loader = MagicMock()
    assert textures_ready(fake, "1-1", loader, 0) is True
    loader.prefetch_textures.assert_not_called()


class FakeRoads:
    """The street surfaces the worker makes: the requests, and the chunks made."""

    def __init__(self, made: set[int]) -> None:
        self.made = made
        self.requests: list[tuple[list[list[float]], object, bool]] = []

    def request(self, spans: list[list[float]], tiles: object, grid: bool) -> None:
        self.requests.append((spans, tiles, grid))

    def ready(self, index: int) -> bool:
        return index in self.made


class Grounds:
    """The level grounds asked for, whose street surfaces `source` makes (None: no streets)."""

    def __init__(self) -> None:
        self.source: FakeRoads | None = None
        self.asked: list[tuple[object, int]] = []

    def __call__(self, scenery: object, seed: int) -> SimpleNamespace:
        self.asked.append((scenery, seed))
        return SimpleNamespace(roads_source=self.source)


@pytest.fixture
def grounds(monkeypatch: pytest.MonkeyPatch) -> Grounds:
    made = Grounds()
    monkeypatch.setattr(
        level_prepare,
        "with_runout",
        lambda scenery, _runout: SimpleNamespace(id=scenery.id, seed=scenery.seed),
    )
    monkeypatch.setattr(level_prepare, "level_ground", made)
    return made


def tiled_game() -> SimpleNamespace:
    fake = game(level("1-1"))
    fake.view.scenery.looks["scenery-1-1"].roads.tiles = "tiles"
    return fake


def test_perf_17_the_streets_of_the_first_screens_are_waited_for(grounds: Grounds) -> None:
    length = level_prepare.SCENERY_STAGE_CONFIG.chunk_length
    source = FakeRoads(set())
    grounds.source = source
    fake = tiled_game()
    assert level_prepare.roads_ready(fake, "1-1", True, 0) is False
    ((spans, tiles, grid),) = source.requests
    assert (tiles, grid) == ("tiles", True)
    assert grounds.asked[0][1] == 7
    # From the chunk before the start, one after the other, past the first screens.
    assert spans[0] == [-1, -length, 0]
    for previous, span in itertools.pairwise(spans):
        assert span == [previous[0] + 1, previous[2], previous[2] + length]
    assert spans[-1][1] > level_prepare.FIRST_Z
    source.made = {int(span[0]) for span in spans}
    assert level_prepare.roads_ready(fake, "1-1", False, 1) is True


def test_perf_18_the_scene_makes_the_streets_itself_without_a_worker_or_after_the_wait(
    grounds: Grounds,
) -> None:
    fake = tiled_game()
    assert level_prepare.roads_ready(fake, "1-1", False, 0) is True
    source = FakeRoads(set())
    grounds.source = source
    late = level_prepare.ROAD_WAIT_FRAMES + 1
    assert level_prepare.roads_ready(fake, "1-1", False, late) is True
    assert level_prepare.roads_ready(fake, "9-9", False, 0) is True
    assert source.requests == []
    assert len(grounds.asked) == 1


def test_perf_17_a_level_without_street_tiles_or_a_look_waits_for_no_street(
    grounds: Grounds,
) -> None:
    source = FakeRoads(set())
    grounds.source = source
    fake = game(level("1-1"))
    assert level_prepare.roads_ready(fake, "1-1", False, 0) is True
    fake.view.scenery.looks = {}
    assert level_prepare.roads_ready(fake, "1-1", False, 0) is True
    assert source.requests == []
    assert len(grounds.asked) == 2
