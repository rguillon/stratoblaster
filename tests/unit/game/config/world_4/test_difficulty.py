"""Unit tests of `src/game/config/world_4/difficulty.py`."""

from helpers.config_checks import assert_level_difficulty

from game.config.world_4.difficulty import WORLD_4_DIFFICULTY


def test_wld_4_19_the_world_has_a_difficulty_for_each_of_its_levels() -> None:
    """Each level's factors (LVL-4-1-05 … LVL-4-5-05)."""
    assert sorted(WORLD_4_DIFFICULTY.keys()) == [f"4-{i}" for i in range(1, 6)]


def test_wld_4_19_difficulty_never_goes_down_from_one_level_to_the_next() -> None:
    assert_level_difficulty(WORLD_4_DIFFICULTY)
