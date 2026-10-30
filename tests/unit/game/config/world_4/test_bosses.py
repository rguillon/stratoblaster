"""Unit tests of `src/game/config/world_4/bosses.py`."""

from helpers.config_checks import assert_world_bosses

from game.config.world_4.bosses import WORLD_4_BOSSES
from game.sim.boss_kinds import BOSS_DESIGNS

BOSS_IDS = {design.id for design in BOSS_DESIGNS}


def test_p10_r11_each_level_names_a_mini_boss_and_a_final_boss_of_the_game() -> None:
    assert_world_bosses(WORLD_4_BOSSES, BOSS_IDS)


def test_p10_r11_the_bosses_of_the_world_are_not_reused_between_its_levels() -> None:
    names = [entry[key] for entry in WORLD_4_BOSSES.values() for key in ("mini", "final")]
    assert len(names) == len(set(names))
