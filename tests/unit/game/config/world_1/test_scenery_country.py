"""Unit tests of `src/game/config/world_1/scenery_country.py`."""

import pytest
from helpers.config_checks import assert_scenery_level

from game.config.world_1.scenery_country import LEVEL_1_3

LEVELS = [LEVEL_1_3]


@pytest.mark.parametrize("level", LEVELS)
def test_wld_1_01_level_scenery_names_its_level_and_scrolls(level) -> None:
    """The level's identity (LVL-1-3-01) and its own ground speed (WLD-1-04)."""
    assert level.id.startswith("world-1-")
    assert_scenery_level(level, level.id.removeprefix("world-"))


@pytest.mark.parametrize("level", LEVELS)
def test_wld_1_03_level_sections_have_positive_lengths(level) -> None:
    """The sections (LVL-1-3-04) whose seconds make the duration (LVL-1-3-02)."""
    assert level.sections
    for section in level.sections:
        assert section["seconds"] > 0
