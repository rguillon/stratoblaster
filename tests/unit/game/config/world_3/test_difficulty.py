"""Unit tests of `src/game/config/world_3/difficulty.py`."""

from helpers.config_checks import assert_level_difficulty

from game.config.world_3.difficulty import WORLD_3_DIFFICULTY


def test_p09_r08_the_world_has_a_difficulty_for_each_of_its_levels() -> None:
    assert sorted(WORLD_3_DIFFICULTY.keys()) == [f"3-{i}" for i in range(1, 6)]


def test_p09_r08_difficulty_never_goes_down_from_one_level_to_the_next() -> None:
    assert_level_difficulty(WORLD_3_DIFFICULTY)
