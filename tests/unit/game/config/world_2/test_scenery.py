"""Unit tests of `src/game/config/world_2/scenery.py`."""

import pytest
from helpers.config_checks import assert_scenery_level

from game.config.world_2.scenery import LEVEL_2_1, LEVEL_2_2, LEVEL_2_3, LEVEL_2_4, LEVEL_2_5

LEVELS = [LEVEL_2_1, LEVEL_2_2, LEVEL_2_3, LEVEL_2_4, LEVEL_2_5]


@pytest.mark.parametrize("level", LEVELS)
def test_wld_2_01_level_scenery_names_its_level_and_scrolls(level) -> None:
    """Each level's identity (LVL-2-1-01 … LVL-2-5-01) and its own ground speed (WLD-2-04)."""
    assert level.id.startswith("world-2-")
    assert_scenery_level(level, level.id.removeprefix("world-"))


@pytest.mark.parametrize("level", LEVELS)
def test_wld_2_03_level_sections_have_positive_lengths(level) -> None:
    """The sections (LVL-2-1-04 … LVL-2-5-04) whose seconds make the duration
    (LVL-2-1-02 … LVL-2-5-02)."""
    assert level.sections
    for section in level.sections:
        assert section["seconds"] > 0
