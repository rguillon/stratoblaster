# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `tests/ai/learn.py`, `tests/ai/rollout.py` and `tests/ai/rate.py`."""

import random  # noqa: TID251  # the curriculum draws from a `random.Random`
from pathlib import Path

import numpy as np
import pytest
import torch
from ai import learn as learn_module
from ai.brain import Brain, BrainShape
from ai.game_env import LEVEL_IDS, MAX_WEAPON_LEVEL, SHIP_IDS, WEAPON_IDS, EpisodeSetup
from ai.game_env import level_seconds as seconds_of
from ai.learn import Learner, Settings, advantages
from ai.rate import EpisodeResult, RatingSettings, play_episode, rate_level, setups
from ai.rollout import Curriculum, Player, _empty

SMALL = BrainShape(hidden=32, field_features=16, fovea_features=16, state_features=8)


def test_advantages_discount_the_rewards_and_stop_at_an_episode_end() -> None:
    rollout = _empty(3, 1, 4)
    rollout.rewards[:, 0] = [1.0, 0.0, 2.0]
    rollout.dones[:, 0] = [False, True, False]
    rollout.last_values[:] = 10.0
    adv, returns = advantages(rollout, gamma=0.5, lam=1.0)
    # Values are 0: the returns are the discounted rewards, cut at the end of the episode.
    assert returns[:, 0].tolist() == pytest.approx([1.0, 0.0, 2.0 + 0.5 * 10.0])
    assert adv.tolist() == returns.tolist()


def test_the_curriculum_draws_valid_episodes() -> None:
    rng = random.Random(3)  # noqa: S311  # not cryptography: episodes drawn at random
    curriculum = Curriculum()
    for _ in range(50):
        setup = curriculum.draw(rng)
        assert setup.level_id in LEVEL_IDS
        assert setup.ship_id in SHIP_IDS
        assert setup.weapon in WEAPON_IDS
        assert 0 <= setup.start_time <= seconds_of(setup.level_id)
        assert all(1 <= v <= MAX_WEAPON_LEVEL for v in setup.weapon_levels.values())
        assert setup.lives >= 1


def test_a_player_plays_a_round_and_the_learner_learns_from_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(learn_module, "BRAIN_FILE", tmp_path / "brain.pt")
    monkeypatch.setattr(learn_module, "TRAINER_FILE", tmp_path / "trainer.pt")
    torch.manual_seed(0)
    player = Player(SMALL, 2, 1, Curriculum(levels=("1-1",)))
    learner = Learner(Settings(chunk=4, minibatch_chunks=2, epochs=1), fresh=True)
    learner.brain = Brain(SMALL)
    learner.optimizer = torch.optim.Adam(learner.brain.parameters(), lr=1e-3)
    before = {k: v.clone() for k, v in learner.brain.state_dict().items()}
    rollout = player.play(learner.weights(), 8)
    assert rollout.field.shape[:2] == (8, 2)
    assert rollout.starts[0].all()  # the first step of each episode starts its memory over
    assert np.isfinite(rollout.values).all()
    losses = learner.update(rollout)
    assert set(losses) == {"policy", "value", "entropy", "kl"}
    after = learner.brain.state_dict()
    assert any(not torch.equal(before[k], after[k]) for k in before)


def test_an_episode_difficulty_is_one_less_the_mean_of_progress_and_health_left() -> None:
    def result(progress: float, health: float, outcome: str = "complete") -> EpisodeResult:
        return EpisodeResult("1-1", 1, outcome, progress, health, 0, 1.0, 0.0)

    assert result(1.0, 1.0).difficulty == 0.0
    assert result(1.0, 0.5).difficulty == 0.25
    assert result(0.5, 0.0, "over").difficulty == 0.75
    assert result(0.0, 0.0, "over").difficulty == 1.0
    rating = rate_level("1-1", [result(1.0, 1.0), result(0.5, 0.0, "over")])
    assert rating.difficulty == 37.5
    assert rating.completed == 0.5


def test_the_rating_plays_every_level_with_the_same_loadout() -> None:
    settings = RatingSettings(episodes=2, weapon_level=4)
    all_setups = setups(settings, ["1-1", "2-3"])
    assert [s.level_id for s in all_setups] == ["1-1", "1-1", "2-3", "2-3"]
    assert len({s.seed for s in all_setups[:2]}) == 2
    for s in all_setups:
        assert s.weapon_levels == dict.fromkeys(WEAPON_IDS, 4)
        assert (s.lives, s.bombs, s.start_time) == (3, 3, 0.0)


def test_a_rating_episode_is_played_to_its_end() -> None:
    brain = Brain(SMALL)
    seconds = seconds_of("1-1")
    setup = EpisodeSetup("1-1", start_time=seconds, extra_seconds=2)
    result = play_episode(brain, setup, greedy=True)
    assert result.outcome in ("timeout", "complete", "over")
    assert 0.0 <= result.health_left <= 1.0
    assert 0.0 <= result.difficulty <= 1.0
