# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/level_prepare.py`."""
# (PERF-11, PERF-12, PERF-18): the level choices made ahead of play.

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
