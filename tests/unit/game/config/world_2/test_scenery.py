"""Unit tests of `src/game/config/world_2/scenery.py`."""

import pytest
from helpers.config_checks import assert_scenery_level

from game.config.world_2.scenery import LEVEL_2_1, LEVEL_2_2, LEVEL_2_3, LEVEL_2_4, LEVEL_2_5

LEVELS = [LEVEL_2_1, LEVEL_2_2, LEVEL_2_3, LEVEL_2_4, LEVEL_2_5]


@pytest.mark.parametrize("level", LEVELS)
def test_p08_r03_level_scenery_names_its_level_and_scrolls(level) -> None:
    assert level.id.startswith("world-2-")
    assert_scenery_level(level, level.id.removeprefix("world-"))


@pytest.mark.parametrize("level", LEVELS)
def test_p08_r03_level_sections_have_positive_lengths(level) -> None:
    assert level.sections
    for section in level.sections:
        assert section["seconds"] > 0
