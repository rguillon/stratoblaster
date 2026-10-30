"""Unit tests of `src/game/config/world_4/scenery.py`."""

import pytest
from helpers.config_checks import assert_scenery_level

from game.config.world_4.scenery import LEVEL_4_1, LEVEL_4_2, LEVEL_4_3, LEVEL_4_4, LEVEL_4_5

LEVELS = [LEVEL_4_1, LEVEL_4_2, LEVEL_4_3, LEVEL_4_4, LEVEL_4_5]


@pytest.mark.parametrize("level", LEVELS)
def test_p10_r03_level_scenery_names_its_level_and_scrolls(level) -> None:
    assert level.id.startswith("world-4-")
    assert_scenery_level(level, level.id.removeprefix("world-"))


@pytest.mark.parametrize("level", LEVELS)
def test_p10_r03_level_sections_have_positive_lengths(level) -> None:
    assert level.sections
    for section in level.sections:
        assert section["seconds"] > 0
