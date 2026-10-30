"""Unit tests of `src/game/sim/scenery_build.py`."""

import pytest

from core.scenery.scenery_level import SceneryLevel, level_length
from game.config.world_1.scenery_coast import LEVEL_1_1
from game.config.world_4.scenery import LEVEL_4_5
from game.sim.levels import GAME_LEVELS
from game.sim.scenery_build import scenery_level


def test_a_level_keeps_its_sections_in_the_order_of_the_config() -> None:
    level = scenery_level(LEVEL_1_1)
    assert isinstance(level, SceneryLevel)
    assert [s.name for s in level.sections] == [s["name"] for s in LEVEL_1_1.sections]


def test_the_level_length_is_its_sections_seconds_at_its_scroll_speed() -> None:
    level = scenery_level(LEVEL_1_1)
    seconds = sum(s["seconds"] for s in LEVEL_1_1.sections)
    assert level_length(level) == pytest.approx(seconds * LEVEL_1_1.scrollSpeed)


def test_every_game_level_builds_a_scenery_with_a_positive_length() -> None:
    for game_level in GAME_LEVELS:
        assert level_length(game_level.scenery) > 0, game_level.id


def test_a_late_world_level_builds_its_scenery_too() -> None:
    level = scenery_level(LEVEL_4_5)
    assert len(level.sections) == len(LEVEL_4_5.sections)
