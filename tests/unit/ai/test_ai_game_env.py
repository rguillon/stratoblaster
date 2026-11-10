# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `tests/ai/game_env.py`: the game as an environment for the brain."""

import math

import pytest
from ai.game_env import (
    LEVEL_IDS,
    MOVES,
    STEP_SECONDS,
    WEAPON_IDS,
    Action,
    EpisodeSetup,
    GameEnv,
    StepInfo,
    level_seconds,
    weapon_levels_of,
)


def test_every_level_of_the_game_can_be_played() -> None:
    assert tuple(f"{w}-{lv}" for w in range(1, 5) for lv in range(1, 6)) == LEVEL_IDS
    for level_id in LEVEL_IDS:
        env = GameEnv(EpisodeSetup(level_id))
        env.step(Action(0))
        assert env.run.phase == "playing"
        assert level_seconds(level_id) > 60


def test_the_moves_are_still_then_eight_unit_directions() -> None:
    assert MOVES[0] == (0.0, 0.0)
    assert len(MOVES) == 9
    for dx, dy in MOVES[1:]:
        assert math.hypot(dx, dy) == pytest.approx(1.0)


def test_a_step_plays_frame_skip_steps_of_the_simulation_and_moves_the_ship() -> None:
    env = GameEnv(EpisodeSetup("1-1"), frame_skip=4)
    x = env.run.ship.x
    for _ in range(10):
        env.step(Action(3))  # east
    assert env.time == pytest.approx(40 * STEP_SECONDS)
    assert env.run.ship.x > x


def test_the_setup_gives_the_weapons_and_supplies() -> None:
    levels = dict.fromkeys(WEAPON_IDS, 4)
    env = GameEnv(EpisodeSetup("2-1", weapon="laser", weapon_levels=levels, lives=2, bombs=1))
    assert env.run.shots.weapon.id == "laser"
    assert env.run.shots.level == 4
    assert env.run.hull is not None
    assert env.run.hull.lives == 2
    assert env.run.bombs is not None
    assert env.run.bombs.count == 1
    assert weapon_levels_of(env.run) == dict.fromkeys(WEAPON_IDS, 4.0)


def test_switch_and_bomb_act_once_per_decision() -> None:
    env = GameEnv(EpisodeSetup("1-1"))
    _, info = env.step(Action(0, bomb=True, switch=True))
    assert env.run.shots.weapon.id == WEAPON_IDS[1]
    assert info.bombed
    assert info.switched
    assert env.run.bombs is not None
    assert env.run.bombs.count == 2


def test_a_start_time_skips_into_the_level() -> None:
    env = GameEnv(EpisodeSetup("1-1", start_time=100))
    assert env.start_progress == pytest.approx(100 * env.level.scenery.scroll_speed)
    assert env.progress_fraction == 0


def test_the_episode_times_out_past_its_limit() -> None:
    seconds = level_seconds("1-1")
    env = GameEnv(EpisodeSetup("1-1", start_time=seconds, extra_seconds=1))
    while not env.done:
        env.step(Action(0))
    assert env.outcome in ("timeout", "complete", "over")
    assert env.time <= env.limit + 4 * STEP_SECONDS


def test_d_272_the_reward_is_the_points_scored_and_a_little_for_staying_alive() -> None:
    env = GameEnv(EpisodeSetup("1-1"))
    w = env.weights
    assert env.reward(StepInfo()) == pytest.approx(w.alive)
    assert env.reward(StepInfo(score=2000)) == pytest.approx(1.0 + w.alive)
    hurt = StepInfo(damage=env.max_health / 2, picked=["weapon"])
    assert env.reward(hurt) == pytest.approx(w.alive - w.damage / 2)
    lost = StepInfo(damage=env.max_health, lives_lost=1, outcome="over")
    assert env.reward(lost) == pytest.approx(w.alive - w.damage - w.life)


def test_d_315_a_bomb_and_a_switch_cost_something() -> None:
    env = GameEnv(EpisodeSetup("1-1"))
    w = env.weights
    assert env.reward(StepInfo(bombed=True)) == pytest.approx(w.alive - w.bomb)
    assert env.reward(StepInfo(switched=True)) == pytest.approx(w.alive - w.switch)
    assert w.bomb > 0
    assert w.switch > 0
    _, info = env.step(Action(0))
    assert not info.switched


def _clear(env: GameEnv) -> StepInfo:
    """Have the level under way cleared, and play the decision that sees it."""
    env.run._phase = "complete"  # as if its last boss were destroyed
    _, info = env.step(Action(0))
    return info


def test_d_271_a_campaign_goes_on_with_what_the_level_cleared_ended_with() -> None:
    env = GameEnv(EpisodeSetup("1-1", seed=5), campaign=LEVEL_IDS)
    run = env.run
    assert run.hull is not None
    assert run.bombs is not None
    run.hull.lives = 2
    run.bombs.count = 5
    run.arsenal.level_up(2)
    run.enemies.score = 1200
    info = _clear(env)
    assert info.cleared == "1-1"
    assert info.outcome == ""
    assert not env.done
    assert env.setup.level_id == "1-2"
    assert env.cleared == ["1-1"]
    assert env.run is not run
    assert env.run.hull is not None
    assert env.run.bombs is not None
    assert (env.run.hull.lives, env.run.bombs.count) == (2, 5)
    assert env.run.shots.level == 3
    assert env.run.track.progress == 0
    assert env.score == 1200
    assert env.time == 0
    env.reset()
    assert (env.setup.level_id, env.cleared, env.score) == ("1-1", [], 0)


def test_d_271_a_campaign_ends_when_its_last_level_is_cleared() -> None:
    env = GameEnv(EpisodeSetup("4-4"), campaign=LEVEL_IDS)
    _clear(env)
    assert env.setup.level_id == "4-5"
    info = _clear(env)
    assert info.outcome == "complete"
    assert env.done
    assert env.cleared == ["4-4"]
    alone = GameEnv(EpisodeSetup("1-1"))
    assert alone.next_level() is None
    assert _clear(alone).outcome == "complete"


def test_the_health_budget_counts_every_life() -> None:
    env = GameEnv(EpisodeSetup("1-1", lives=3))
    hull = env.run.hull
    assert hull is not None
    assert env.health_budget() == 3 * hull.max_health
    hull.health = hull.max_health / 2
    assert env.health_budget() == 2.5 * hull.max_health
    hull.lives = 0
    assert env.health_budget() == 0
