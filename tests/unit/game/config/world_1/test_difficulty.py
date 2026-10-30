"""Unit tests of `src/game/config/world_1/difficulty.py`."""

from helpers.config_checks import assert_level_difficulty

from game.config.world_1.difficulty import WORLD_1_DIFFICULTY


def test_p06_r08_the_world_has_a_difficulty_for_each_of_its_levels() -> None:
    assert sorted(WORLD_1_DIFFICULTY.keys()) == [f"1-{i}" for i in range(1, 6)]


def test_p06_r08_difficulty_never_goes_down_from_one_level_to_the_next() -> None:
    assert_level_difficulty(WORLD_1_DIFFICULTY)
