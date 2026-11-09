# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `tests/ai/adjust.py` (D-305)."""

import shutil
from collections.abc import Callable
from pathlib import Path

import numpy as np
import pytest
from ai import SRC
from ai.adjust import (
    MAX_FACTOR,
    Search,
    Step,
    base_factors,
    k_range,
    next_k,
    ordering_breaks,
    scaled,
    search_dial,
    spec_files,
    write_factors,
)
from ai.game_env import EpisodeSetup, GameEnv
from ai.rate import RatingSettings, setups

from game.config.world_4.difficulty import WORLD_4_DIFFICULTY

Rater = Callable[[tuple[float, float, float], int], tuple[float, float, float]]


def _rater(
    slope: float = 60.0, noise: float = 0.0, seed: int = 1
) -> tuple[Rater, list[tuple[tuple[float, float, float], int]]]:
    """Return a rating going up with the bullet speed factor, from 20 % at 1, with some noise."""
    draw = np.random.default_rng(seed)
    calls: list[tuple[tuple[float, float, float], int]] = []

    def rate_at(factors: tuple[float, float, float], episodes: int) -> tuple[float, float, float]:
        calls.append((factors, episodes))
        rating = min(100.0, max(0.0, 20 + slope * (factors[0] - 1) + float(draw.normal(0, noise))))
        return rating, noise / episodes**0.5, 0.5

    return rate_at, calls


def _quiet(_step: object) -> None:
    pass


def test_d_305_the_search_reaches_the_target_on_a_steady_rating() -> None:
    rate_at, _ = _rater()
    outcome = search_dial((1.0, 1.0, 1.0), Search(50), rate_at, _quiet)
    assert outcome.status == "reached"
    assert abs(outcome.best.rating - 50) <= 2
    assert outcome.best.factors[0] == outcome.best.factors[1] == outcome.best.factors[2]


def test_d_305_the_search_reaches_the_target_through_noise() -> None:
    rate_at, calls = _rater(noise=3.0)
    outcome = search_dial((1.0, 1.0, 1.0), Search(60, max_steps=12), rate_at, _quiet)
    assert outcome.status == "reached"
    assert abs(outcome.best.rating - 60) <= 2 * 3.0
    # The episodes double once the target is bracketed.
    assert calls[-1][1] > calls[0][1]


def test_d_305_the_search_makes_a_level_easier_too() -> None:
    rate_at, _ = _rater()
    outcome = search_dial((1.0, 1.0, 1.0), Search(5), rate_at, _quiet)
    assert outcome.status == "reached"
    assert outcome.best.k < 1


def test_d_305_the_search_says_when_the_dial_runs_out() -> None:
    rate_at, _ = _rater(slope=5)
    outcome = search_dial((1.3, 1.3, 1.0), Search(90), rate_at, _quiet)
    assert outcome.status == "saturated"
    assert max(outcome.best.factors) <= MAX_FACTOR


def test_d_305_no_factor_goes_past_the_ceiling() -> None:
    low, high = k_range((1.35, 1.35, 1.0), Search(90))
    assert low == 0.5
    assert high == pytest.approx(2 / 1.35)
    assert max(scaled((1.35, 1.35, 1.0), high)) <= MAX_FACTOR


def test_d_305_the_next_k_interpolates_within_the_bracket() -> None:
    steps = [Step(1.0, (1, 1, 1), 16, 40, 1, 0), Step(1.5, (1.5, 1.5, 1.5), 16, 80, 1, 0)]
    assert next_k(steps, 60, 0.5, 2) == pytest.approx(1.25)
    # Below the target only: harder by the stride.
    assert next_k(steps[:1], 60, 0.5, 2) == pytest.approx(1.25)


def test_d_305_the_level_s_factors_come_from_its_config() -> None:
    entry = WORLD_4_DIFFICULTY["4-4"]
    assert base_factors("4-4") == (entry["bulletSpeed"], entry["fireRate"], entry["bossHealth"])


def test_d_305_a_rating_episode_plays_with_the_factors_tried() -> None:
    every = setups(RatingSettings(episodes=1), ["1-1"], (1.5, 1.6, 1.7))
    level = GameEnv(every[0]).level
    assert (
        level.difficulty.bullet_speed,
        level.difficulty.fire_rate,
        level.difficulty.boss_health,
    ) == (1.5, 1.6, 1.7)
    assert GameEnv(EpisodeSetup("1-1")).level.difficulty.boss_health == 1


def test_d_305_the_factors_are_written_into_the_level_s_line(tmp_path: Path) -> None:
    config = tmp_path / "game" / "config" / "world_4"
    config.mkdir(parents=True)
    source = SRC / "game" / "config" / "world_4" / "difficulty.py"
    shutil.copy(source, config / "difficulty.py")
    path = write_factors("4-4", (1.62, 1.6, 1.25), tmp_path)
    before = source.read_text().splitlines()
    after = path.read_text().splitlines()
    changed = [(a, b) for a, b in zip(before, after, strict=True) if a != b]
    assert changed == [
        (
            '    "4-4": {"bulletSpeed": 1.3, "fireRate": 1.3, "bossHealth": 1},  # LVL-4-4-05',
            '    "4-4": {"bulletSpeed": 1.62, "fireRate": 1.6, "bossHealth": 1.25},  # LVL-4-4-05',
        )
    ]


def test_d_305_a_level_made_easier_than_the_one_before_is_flagged() -> None:
    assert ordering_breaks("4-4", (1.0, 1.3, 1.0)) == ["bullet speed: 4-4 (1) is below 4-3 (1.2)"]
    assert ordering_breaks("4-4", (1.3, 1.3, 2.0)) == []


def test_d_305_the_specs_to_update_are_named() -> None:
    names = [path.name for path in spec_files("4-4")]
    assert names == ["4-4-business-district.md", "world.md"]
