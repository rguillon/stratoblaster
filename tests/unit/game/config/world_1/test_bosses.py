# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/world_1/bosses.py`."""

from helpers.config_checks import assert_world_bosses

from game.config.world_1.bosses import WORLD_1_BOSSES
from game.sim.boss_kinds import BOSS_DESIGNS

BOSS_IDS = {design.id for design in BOSS_DESIGNS}


def test_wld_1_26_each_level_names_a_mini_boss_and_a_final_boss_of_the_game() -> None:
    """Also BOSS-01, each level's mini boss and final boss (WLD-1-26), and its runout.

    Runout: LVL-1-1-14 … LVL-1-5-14.
    """
    assert_world_bosses(WORLD_1_BOSSES, BOSS_IDS)


def test_wld_1_26_the_bosses_of_the_world_are_not_reused_between_its_levels() -> None:
    """Also BOSS-01: no boss kind used by two levels."""
    names = [entry[key] for entry in WORLD_1_BOSSES.values() for key in ("mini", "final")]
    assert len(names) == len(set(names))
