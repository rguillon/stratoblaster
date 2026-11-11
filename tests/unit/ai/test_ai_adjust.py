# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `tests/ai/adjust.py` (D-305, D-307)."""

import itertools
import shutil
from collections.abc import Callable
from pathlib import Path

import numpy as np
import pytest
from ai import SRC
from ai import adjust as adjust_module
from ai.adjust import (
    Outcome,
    Search,
    Step,
    adjust_all,
    linear_targets,
    next_factor,
    rising,
    search_factor,
    write_factor,
)
from ai.game_env import LEVEL_IDS, GameEnv, level_enemies
from ai.rate import RatingSettings, setups

from game.config.level_enemies import LEVEL_ENEMIES

Rater = Callable[[float, int], tuple[float, float, float]]


def _rater(
    slope: float = 40.0, noise: float = 0.0, seed: int = 1
) -> tuple[Rater, list[tuple[float, int]]]:
    """Return a rating going up with the enemies factor, from 20 % at 1, with some noise."""
    draw = np.random.default_rng(seed)
    calls: list[tuple[float, int]] = []

    def rate_at(enemies: float, episodes: int) -> tuple[float, float, float]:
        calls.append((enemies, episodes))
        rating = min(100.0, max(0.0, 20 + slope * (enemies - 1) + float(draw.normal(0, noise))))
        return rating, noise / episodes**0.5, 0.5

    return rate_at, calls


def _quiet(_step: object) -> None:
    pass


def test_d_305_the_search_reaches_the_target_on_a_steady_rating() -> None:
    rate_at, _ = _rater()
    outcome = search_factor(1.0, Search(50), rate_at, _quiet)
    assert outcome.status == "reached"
    assert abs(outcome.best.rating - 50) <= 2


def test_d_305_the_search_reaches_the_target_through_noise() -> None:
    rate_at, calls = _rater(noise=3.0)
    search = Search(50, episodes=16, max_episodes=64, max_steps=12)
    outcome = search_factor(1.0, search, rate_at, _quiet)
    assert outcome.status == "reached"
    assert abs(outcome.best.rating - 50) <= 2 * 3.0
    # The episodes double once the target is bracketed.
    assert calls[-1][1] > calls[0][1]


def test_d_305_the_search_makes_a_level_easier_too() -> None:
    rate_at, _ = _rater()
    outcome = search_factor(1.0, Search(5), rate_at, _quiet)
    assert outcome.status == "reached"
    assert outcome.best.enemies < 1


def test_d_305_the_search_says_when_the_factor_runs_out() -> None:
    rate_at, _ = _rater(slope=5)
    outcome = search_factor(1.0, Search(90, highest=4), rate_at, _quiet)
    assert outcome.status == "saturated"
    assert outcome.best.enemies <= 4


def test_d_312_more_enemies_have_no_limit_by_default() -> None:
    """A level that needs ten times its enemies gets them."""
    rate_at, _ = _rater(slope=5)
    outcome = search_factor(1.0, Search(65), rate_at, _quiet)
    assert outcome.status == "reached"
    assert outcome.best.enemies > 9


def test_d_312_more_enemies_stop_at_the_most_steps() -> None:
    rate_at, calls = _rater(slope=0.1)
    outcome = search_factor(1.0, Search(90, max_steps=5), rate_at, _quiet)
    assert outcome.status == "unfinished"
    assert len(calls) == 5


def test_d_305_the_next_factor_interpolates_within_the_bracket() -> None:
    steps = [Step(1.0, 16, 40, 1, 0), Step(1.5, 16, 80, 1, 0)]
    assert next_factor(steps, 60, 0.25, 4) == pytest.approx(1.25)
    # Below the target only: more enemies by the stride.
    assert next_factor(steps[:1], 60, 0.25, 4) == pytest.approx(1.4)


def test_d_307_the_level_s_factor_comes_from_its_config() -> None:
    assert level_enemies("4-4") == LEVEL_ENEMIES["4-4"]


def test_d_307_a_rating_episode_plays_with_the_enemies_tried() -> None:
    every = setups(RatingSettings(episodes=1), ["2-3"], 2.0)
    more = GameEnv(every[0]).level
    usual = GameEnv(setups(RatingSettings(episodes=1), ["2-3"], 1.0)[0]).level
    assert sum(w["count"] for w in more.waves) > 1.2 * sum(w["count"] for w in usual.waves)
    assert more.bosses[0].kind == usual.bosses[0].kind
    assert (more.difficulty.bullet_speed, more.difficulty.fire_rate) == (1, 1)


def test_d_307_the_factor_is_written_into_the_level_s_line(tmp_path: Path) -> None:
    config = tmp_path / "game" / "config"
    config.mkdir(parents=True)
    source = SRC / "game" / "config" / "level_enemies.py"
    shutil.copy(source, config / "level_enemies.py")
    path = write_factor("4-4", 1.234, tmp_path)
    before = source.read_text().splitlines()
    after = path.read_text().splitlines()
    changed = [(a, b) for a, b in zip(before, after, strict=True) if a != b]
    assert changed == [(f'    "4-4": {LEVEL_ENEMIES["4-4"]:g},', '    "4-4": 1.23,')]


def test_d_308_the_targets_rise_evenly_from_the_first_level_to_the_last() -> None:
    targets = linear_targets(10, 99, list(LEVEL_IDS))
    assert targets[0] == ("1-1", 10)
    assert targets[-1] == ("4-5", 99)
    assert [level for level, _ in targets] == list(LEVEL_IDS)
    steps = [b - a for (_, a), (_, b) in itertools.pairwise(targets)]
    assert all(abs(step - 89 / 19) < 0.11 for step in steps)


def test_d_308_every_level_is_adjusted_in_turn(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, float]] = []

    def fake(level_id: str, search: Search, *_: object) -> Outcome:
        calls.append((level_id, search.target))
        return Outcome("reached", Step(1.0, 16, search.target, 1, 1))

    monkeypatch.setattr(adjust_module, "adjust", fake)
    targets = [("1-1", 10.0), ("1-2", 20.0)]
    outcomes = adjust_all(targets, Search(0), RatingSettings(), 1, Path("brain.pt"))
    assert calls == targets
    assert [o.best.rating for o in outcomes] == [10, 20]


def test_d_309_the_search_follows_ratings_that_fall_with_more_enemies() -> None:
    """Were more enemies easier (more bonuses), the search would still find the target."""

    def rate_at(enemies: float, _episodes: int) -> tuple[float, float, float]:
        return max(0.0, 60 - 30 * (enemies - 1)), 0.0, 0.5

    harder = search_factor(1.0, Search(80), rate_at, _quiet)
    assert harder.status == "reached"
    assert harder.best.enemies < 1
    easier = search_factor(1.0, Search(30), rate_at, _quiet)
    assert easier.status == "reached"
    assert easier.best.enemies > 1


def test_d_309_the_ratings_direction_is_measured() -> None:
    up = [Step(1.0, 16, 20, 1, 0), Step(1.4, 16, 30, 1, 0)]
    down = [Step(1.0, 16, 30, 1, 0), Step(1.4, 16, 20, 1, 0)]
    assert rising(up)
    assert not rising(down)
    assert rising(up[:1])


def test_d_310_each_rating_plays_a_hundred_episodes() -> None:
    rate_at, calls = _rater(noise=3.0)
    search_factor(1.0, Search(50), rate_at, _quiet)
    assert {episodes for _, episodes in calls} == {100}
