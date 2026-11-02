# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/world_1/scenery_desert.py`."""

from typing import Any

import pytest
from helpers.config_checks import assert_scenery_level

from game.config.scenery_look import BASE_SCENERY_LOOK
from game.config.world_1.scenery_desert import LEVEL_1_4, LEVEL_1_5

LEVELS = [LEVEL_1_4, LEVEL_1_5]


@pytest.mark.parametrize("level", LEVELS)
def test_wld_1_01_level_scenery_names_its_level_and_scrolls(level: Any) -> None:
    """Each level's identity (LVL-1-4-01, LVL-1-5-01) and its own ground speed (WLD-1-04)."""
    assert level.id.startswith("world-1-")
    assert_scenery_level(level, level.id.removeprefix("world-"))


@pytest.mark.parametrize("level", LEVELS)
def test_wld_1_03_level_sections_have_positive_lengths(level: Any) -> None:
    """The sections (LVL-1-4-04, LVL-1-5-04) whose seconds make the duration.

    Duration: LVL-1-4-02, LVL-1-5-02.
    """
    assert level.sections
    for section in level.sections:
        assert section["seconds"] > 0


# D-200: an American desert, dried land, not sand dunes (WLD-1-10, GFX-TERRAIN-11).


@pytest.mark.parametrize("level", LEVELS)
def test_d200_the_desert_has_no_dunes(level: Any) -> None:
    for section in level.sections:
        assert section.get("dunes") is None, section["name"]


def test_d200_the_dry_lake_lies_low_enough_for_the_cracked_hardpan() -> None:
    """1-4's dry lake (LVL-1-4-05)."""
    lake = next(s for s in LEVEL_1_4.sections if s["name"] == "dry lake")
    relief = lake["relief"]
    assert relief["base"] + relief["amplitude"] < BASE_SCENERY_LOOK.terrain.lowHeight


def test_d200_the_buttes_stand_flat_topped_under_the_flight() -> None:
    """1-5's buttes (LVL-1-5-05)."""
    section = next(s for s in LEVEL_1_5.sections if s["name"] == "buttes")
    relief = section["relief"]
    assert relief["style"] == "smooth"
    assert relief["maxHeight"] < relief["base"] + relief["amplitude"]


def test_wld_1_31_the_open_desert_is_hills_with_a_rocky_face_the_rest_has_none() -> None:
    hills_1_4 = [s["name"] for s in LEVEL_1_4.sections if s.get("scarps") is not None]
    hills_1_5 = [s["name"] for s in LEVEL_1_5.sections if s.get("scarps") is not None]
    assert hills_1_4 == ["dry grassland", "scrubland villages", "desert outskirts"]
    assert hills_1_5 == ["desert outskirts", "rocky pass"]
    for level in LEVELS:
        for section in level.sections:
            if section.get("streets") is not None:
                assert section.get("scarps") is None, section["name"]
