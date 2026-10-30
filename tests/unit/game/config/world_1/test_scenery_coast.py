"""Unit tests of `src/game/config/world_1/scenery_coast.py`."""

import pytest
from helpers.config_checks import assert_scenery_level

from game.config.world_1.scenery_coast import LEVEL_1_1, LEVEL_1_2

LEVELS = [LEVEL_1_1, LEVEL_1_2]


@pytest.mark.parametrize("level", LEVELS)
def test_p06_r05_level_scenery_names_its_level_and_scrolls(level) -> None:
    assert level.id.startswith("world-1-")
    assert_scenery_level(level, level.id.removeprefix("world-"))


@pytest.mark.parametrize("level", LEVELS)
def test_p06_r05_level_sections_have_positive_lengths(level) -> None:
    assert level.sections
    for section in level.sections:
        assert section["seconds"] > 0
