# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/world_3/scenery.py`."""

from typing import Any

import pytest
from helpers.config_checks import assert_scenery_level

from game.config.world_3.scenery import LEVEL_3_1, LEVEL_3_2, LEVEL_3_3, LEVEL_3_4, LEVEL_3_5

LEVELS = [LEVEL_3_1, LEVEL_3_2, LEVEL_3_3, LEVEL_3_4, LEVEL_3_5]


@pytest.mark.parametrize("level", LEVELS)
def test_wld_3_01_level_scenery_names_its_level_and_scrolls(level: Any) -> None:
    """Each level's identity and ground speed (LVL-3-1-01 … LVL-3-5-01)."""
    assert level.id.startswith("world-3-")
    assert_scenery_level(level, level.id.removeprefix("world-"))


@pytest.mark.parametrize("level", LEVELS)
def test_wld_3_02_level_sections_have_positive_lengths(level: Any) -> None:
    """The sections of each level (LVL-3-1-02 … LVL-3-5-02)."""
    assert level.sections
    for section in level.sections:
        assert section["seconds"] > 0
