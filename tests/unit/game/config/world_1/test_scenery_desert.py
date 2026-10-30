"""Unit tests of `src/game/config/world_1/scenery_desert.py`."""

import pytest
from helpers.config_checks import assert_scenery_level

from game.config.scenery_look import BASE_SCENERY_LOOK
from game.config.world_1.scenery_desert import LEVEL_1_4, LEVEL_1_5

LEVELS = [LEVEL_1_4, LEVEL_1_5]


@pytest.mark.parametrize("level", LEVELS)
def test_p06_r05_level_scenery_names_its_level_and_scrolls(level) -> None:
    assert level.id.startswith("world-1-")
    assert_scenery_level(level, level.id.removeprefix("world-"))


@pytest.mark.parametrize("level", LEVELS)
def test_p06_r05_level_sections_have_positive_lengths(level) -> None:
    assert level.sections
    for section in level.sections:
        assert section["seconds"] > 0


# D-200: an American desert, dried land, not sand dunes.


@pytest.mark.parametrize("level", LEVELS)
def test_d200_the_desert_has_no_dunes(level) -> None:
    for section in level.sections:
        assert section.get("dunes") is None, section["name"]


def test_d200_the_dry_lake_lies_low_enough_for_the_cracked_hardpan() -> None:
    lake = next(s for s in LEVEL_1_4.sections if s["name"] == "dry lake")
    relief = lake["relief"]
    assert relief["base"] + relief["amplitude"] < BASE_SCENERY_LOOK.terrain.lowHeight


def test_d200_the_buttes_stand_flat_topped_under_the_flight() -> None:
    section = next(s for s in LEVEL_1_5.sections if s["name"] == "buttes")
    relief = section["relief"]
    assert relief["style"] == "smooth"
    assert relief["maxHeight"] < relief["base"] + relief["amplitude"]
