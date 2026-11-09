# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `tests/ai/learn.py`, `tests/ai/rollout.py` and `tests/ai/rate.py`."""

import random  # noqa: TID251  # the curriculum draws from a `random.Random`
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import pytest
import torch
from ai import learn as learn_module
from ai.brain import SMALL_SHAPE, Brain, BrainShape, LearnStats, save_brain
from ai.game_env import LEVEL_IDS, SHIP_IDS, WEAPON_IDS, EpisodeSetup
from ai.game_env import level_seconds as seconds_of
from ai.learn import (
    CPUS,
    LOG_COLUMNS,
    MIN_GAMES_FOR_BEST,
    Learner,
    Reporter,
    Settings,
    Workers,
    _keep_if_best,
    _log,
    _record_best_game,
    advantages,
    report,
)
from ai.observation import CH
from ai.rate import (
    EpisodeResult,
    RatingSettings,
    group_size,
    play_episode,
    play_episodes,
    rate_level,
    setups,
)
from ai.rollout import Curriculum, EpisodeReport, GameProgress, Rollout, RolloutBuffer

SMALL = BrainShape(hidden=32, field_features=16, fovea_features=16, state_features=8)


def _empty(path: Path, steps: int, envs: int, hidden: int) -> Rollout:
    return RolloutBuffer(path / "rollout.bin", steps, envs, hidden, create=True).rollout()


def test_advantages_discount_the_rewards_and_stop_at_an_episode_end(tmp_path: Path) -> None:
    rollout = _empty(tmp_path, 3, 1, 4)
    rollout.rewards[:, 0] = [1.0, 0.0, 2.0]
    rollout.dones[:, 0] = [False, True, False]
    rollout.last_values[:] = 10.0
    adv, returns = advantages(rollout, gamma=0.5, lam=1.0)
    # Values are 0: the returns are the discounted rewards, cut at the end of the episode.
    assert returns[:, 0].tolist() == pytest.approx([1.0, 0.0, 2.0 + 0.5 * 10.0])
    assert adv.tolist() == returns.tolist()


def test_d_271_each_episode_is_a_campaign_from_the_first_level_afresh() -> None:
    rng = random.Random(3)  # noqa: S311  # not cryptography: episodes drawn at random
    curriculum = Curriculum()
    for _ in range(20):
        env = curriculum.draw(rng)
        setup = env.setup
        assert env.campaign == LEVEL_IDS
        assert setup.level_id == LEVEL_IDS[0]
        assert (setup.weapon, setup.lives, setup.bombs) == (WEAPON_IDS[0], 3, 3)
        assert setup.start_time == 0
        assert setup.weapon_levels == dict.fromkeys(WEAPON_IDS, 1)
        assert setup.ship_id == "balanced"
    assert "balanced" in SHIP_IDS


def _game(score: float, cleared: int = 0, outcome: str = "over") -> EpisodeReport:
    level = LEVEL_IDS[min(cleared, len(LEVEL_IDS) - 1)]
    return EpisodeReport("balanced", outcome, score, level, cleared, 0.5, 3, 100)


def test_d_271_the_report_says_how_the_games_went_in_words() -> None:
    games = [_game(1000), _game(3000, 1), _game(5000, 2, "timeout"), _game(500)]
    stats = LearnStats(updates=7, decisions=2_500_000, hours=1.25, best_score=2400)
    playing = [GameProgress("1-1", 0, 1000, 900), GameProgress("1-3", 2, 8000, 2700)]
    _record_best_game(stats, games)
    text = report(games, stats, 190, 9000, True, playing)
    assert "3:10 in, 9,000 moves a second · in all: 1.2 h, 2.5 M moves, 7 updates" in text
    assert "Playing now    2 games, on average 1,800 moves in (2:00 of play)" in text
    assert "4,500 points; 1 (50%) past 1-1, furthest in 1-3" in text
    assert "Leading now    8,000 points, in 1-3 (2 levels cleared, 3:00 of play)" in text
    assert "4 since the last report: 3 (75%) game over, 1 (25%) too slow on a level" in text
    assert "0 (0%) cleared every level" in text
    assert "average 2,375, best 5,000 (reached 1-3)" in text
    assert "0.8 cleared on average, furthest reached 1-3; 2 (50%) got past 1-1" in text
    assert "Best game ever 5,000 points: reached 1-3 (2 levels cleared), 0:06 of play" in text
    assert "ended: too slow on a level, at update 7" in text
    assert "Best average   2,400 a game (this brain, saved in data/brain-best.pt)" in text
    quiet = report([], LearnStats(), 1, 0, False)
    assert "Games ended    none since the last report" in quiet
    assert "Playing now" not in quiet
    assert "Best game ever" not in quiet
    assert "Best average" not in quiet
    assert "an earlier brain" in report(games, LearnStats(best_score=9), 1, 1, False)


def test_d_271_the_best_game_is_kept_until_a_better_one_ends() -> None:
    stats = LearnStats(updates=3)
    _record_best_game(stats, [_game(1000), _game(4000, 1)])
    assert stats.best_game["score"] == 4000
    stats.updates = 9
    _record_best_game(stats, [_game(3000)])
    assert (stats.best_game["score"], stats.best_game["update"]) == (4000, 3)
    _record_best_game(stats, [_game(4500, 2)])
    assert (stats.best_game["score"], stats.best_game["reached"]) == (4500, "1-3")


def test_d_271_the_brain_whose_games_score_best_on_average_is_kept(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    best_file = tmp_path / "best.pt"
    monkeypatch.setattr(learn_module, "BEST_BRAIN_FILE", best_file)
    learner = SimpleNamespace(brain=Brain(SMALL), stats=LearnStats(best_score=1000))
    few = [_game(5000)] * (MIN_GAMES_FOR_BEST - 1)
    assert not _keep_if_best(learner, few)  # type: ignore[arg-type]
    assert not _keep_if_best(learner, [_game(900)] * MIN_GAMES_FOR_BEST)  # type: ignore[arg-type]
    assert not best_file.exists()
    assert _keep_if_best(learner, [_game(1500)] * MIN_GAMES_FOR_BEST)  # type: ignore[arg-type]
    assert learner.stats.best_score == 1500
    assert best_file.exists()


def test_d_271_a_log_of_other_columns_is_moved_aside(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    log = tmp_path / "learn-log.csv"
    monkeypatch.setattr(learn_module, "LOG_FILE", log)
    log.write_text("update,reward\n1,0.5\n")
    _log({"update": 1, "score": 10})
    _log({"update": 2, "score": 20})
    assert (tmp_path / "learn-log.old.csv").read_text() == "update,reward\n1,0.5\n"
    lines = log.read_text().splitlines()
    assert lines[0] == ",".join(LOG_COLUMNS)
    assert len(lines) == 3


def test_d_302_a_new_brain_has_the_shape_asked_for(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(learn_module, "BRAIN_FILE", tmp_path / "brain.pt")
    monkeypatch.setattr(learn_module, "TRAINER_FILE", tmp_path / "trainer.pt")
    learner = Learner(Settings(), fresh=True, shape=SMALL_SHAPE)
    assert learner.brain.shape == SMALL_SHAPE


def test_d_301_the_workers_play_a_round_and_the_learner_learns_from_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(learn_module, "BRAIN_FILE", tmp_path / "brain.pt")
    monkeypatch.setattr(learn_module, "TRAINER_FILE", tmp_path / "trainer.pt")
    torch.manual_seed(0)
    learner = Learner(Settings(chunk=4, minibatches=2, epochs=1), fresh=True)
    learner.brain = Brain(SMALL)
    learner.optimizer = torch.optim.Adam(learner.brain.parameters(), lr=1e-3)
    before = {k: v.clone() for k, v in learner.brain.state_dict().items()}
    # Worker processes of this Python (the tests' CPython; PyPy when learning).
    workers = Workers(Settings(workers=2, envs=2, steps=8), SMALL, seed=1)
    try:
        workers.start(learner.weights())
        rollout = workers.collect()
        assert rollout.field.shape[:2] == (8, 4)
        assert rollout.starts[0].all()  # the first step of each episode starts its memory over
        assert not rollout.starts[1:].any()
        assert np.isfinite(rollout.values).all()
        assert rollout.field[:, :, CH["ship"]].any(axis=(2, 3)).all()  # every episode saw its ship
        assert len(rollout.playing) == 4
        losses = learner.update(rollout)
    finally:
        workers.close()
    assert set(losses) == {"policy", "value", "entropy", "kl"}
    after = learner.brain.state_dict()
    assert any(not torch.equal(before[k], after[k]) for k in before)


def test_d_301_the_workers_play_in_pypy_when_it_is_installed() -> None:
    found = learn_module.find_pypy()
    assert found == "" or "pypy" in Path(found).name
    assert learn_module._runtime(Settings(worker_python="/x/pypy3.12")) == "PyPy"
    assert learn_module._runtime(Settings(worker_python="")) == "CPython"


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


def test_d_304_the_rating_gives_the_weapons_the_level_of_the_world() -> None:
    assert RatingSettings().weapon_level is None
    all_setups = setups(RatingSettings(episodes=1), ["1-1", "2-3", "3-5", "4-1"])
    assert [s.weapon_levels[WEAPON_IDS[0]] for s in all_setups] == [1, 2, 3, 4]
    for s in all_setups:
        assert len(set(s.weapon_levels.values())) == 1
        assert (s.lives, s.bombs, s.start_time) == (3, 3, 0.0)


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


def test_a_rollout_buffer_is_shared_by_whoever_maps_its_file(tmp_path: Path) -> None:
    path = tmp_path / "rollout.bin"
    learner_side = RolloutBuffer(path, 4, 6, 8, create=True)
    worker_side = RolloutBuffer(path, 4, 6, 8, create=False).rollout(2, 4)  # episodes 2 and 3
    worker_side.rewards[1] = [5.0, 6.0]
    worker_side.field[0, 1, 3, 2, 5] = 1.0
    worker_side.last_values[:] = 7.0
    whole = learner_side.rollout()
    assert whole.rewards.shape == (4, 6)
    assert whole.rewards[1].tolist() == [0, 0, 5, 6, 0, 0]
    assert whole.field[0, 3, 3, 2, 5] == 1
    assert whole.field.sum() == 1
    assert whole.last_values.tolist() == [0, 0, 7, 7, 0, 0]


def test_with_a_gpu_nearly_every_core_plays() -> None:
    gpu = Settings.for_device("cuda")
    assert gpu.device == "cuda"
    assert gpu.workers == max(1, CPUS - 3)  # the learner and the inference server: a core each
    cpu = Settings.for_device("cpu")
    assert cpu.device == "cpu"
    assert cpu.workers == max(1, CPUS // 2)
    assert cpu.server_threads == max(1, CPUS // 4)


def test_rating_groups_leave_no_worker_idle() -> None:
    assert group_size(160, 8) == 20  # D-303: each worker plays its episodes in one batch
    assert group_size(1000, 8) == 32
    assert group_size(160, 64) == 3
    assert group_size(10, 64) == 1


def test_a_sampled_rating_episode_plays_the_same_alone_or_with_others() -> None:
    """Its moves are drawn from its own seeded generator: ratings repeat on any machine."""
    assert RatingSettings().greedy is False  # moves drawn, as the brain learned to play
    torch.manual_seed(0)
    brain = Brain(SMALL)
    seconds = seconds_of("1-1")

    def setup(seed: int) -> EpisodeSetup:
        return EpisodeSetup("1-1", seed=seed, start_time=seconds - 20, extra_seconds=0)

    alone = play_episodes(brain, [setup(5)], greedy=False)[0]
    together = play_episodes(brain, [setup(7), setup(5)], greedy=False)[1]
    assert alone == together


def test_a_widened_brain_resumes_with_its_optimiser_started_over(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """D-282: the saved Adam moments of a brain with fewer channels no longer fit it."""
    monkeypatch.setattr(learn_module, "BRAIN_FILE", tmp_path / "brain.pt")
    monkeypatch.setattr(learn_module, "TRAINER_FILE", tmp_path / "trainer.pt")
    brain = Brain(SMALL)
    save_brain(brain, LearnStats(updates=1), tmp_path / "brain.pt")

    def trainer(model: torch.nn.Module) -> dict[str, Any]:
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
        sum(p.sum() for p in model.parameters()).backward()
        optimizer.step()
        return optimizer.state_dict()

    torch.save({"optimizer": trainer(Brain(SMALL))}, tmp_path / "trainer.pt")
    learner = Learner(Settings(chunk=4, minibatches=2, epochs=1), fresh=False)
    assert learner.optimizer.state_dict()["state"]
    narrow = Brain(SMALL)
    first = narrow.field_net[0]
    first.weight = torch.nn.Parameter(first.weight[:, :-1].detach().clone())
    torch.save({"optimizer": trainer(narrow)}, tmp_path / "trainer.pt")
    learner = Learner(Settings(chunk=4, minibatches=2, epochs=1), fresh=False)
    assert not learner.optimizer.state_dict()["state"]
    assert "starting it over" in capsys.readouterr().out
    (tmp_path / "brain.pt").unlink()
    learner.save()  # where the learner was told: never the brain of data/
    assert (tmp_path / "brain.pt").exists()
    assert (tmp_path / "trainer.pt").exists()


def test_d_271_short_reports_pool_their_games_to_choose_the_best_brain(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(learn_module, "BEST_BRAIN_FILE", tmp_path / "best.pt")
    learner = SimpleNamespace(brain=Brain(SMALL), stats=LearnStats())
    reporter = Reporter(0, learner.stats)  # type: ignore[arg-type]
    half = MIN_GAMES_FOR_BEST // 2
    reporter.add([_game(800)] * half, learner)  # type: ignore[arg-type]
    assert learner.stats.best_score == 0
    reporter.add([_game(1200)] * (MIN_GAMES_FOR_BEST - half), learner)  # type: ignore[arg-type]
    assert learner.stats.best_score == pytest.approx(1000)
    assert capsys.readouterr().out.count("Games ended") == 2
