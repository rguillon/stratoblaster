# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/world_1/scenery_coast.py`."""

from typing import Any

import pytest
from helpers.config_checks import assert_scenery_level

from game.config.world_1.scenery_coast import LEVEL_1_1, LEVEL_1_2, SCARP_ANGLE, SCARP_FACE

LEVELS = [LEVEL_1_1, LEVEL_1_2]


@pytest.mark.parametrize("level", LEVELS)
def test_wld_1_01_level_scenery_names_its_level_and_scrolls(level: Any) -> None:
    """Each level's identity (LVL-1-1-01, LVL-1-2-01) and its own ground speed (WLD-1-04)."""
    assert level.id.startswith("world-1-")
    assert_scenery_level(level, level.id.removeprefix("world-"))


@pytest.mark.parametrize("level", LEVELS)
def test_wld_1_03_level_sections_have_positive_lengths(level: Any) -> None:
    """The sections (LVL-1-1-04, LVL-1-2-04) whose seconds make the duration.

    Duration: LVL-1-1-02, LVL-1-2-02.
    """
    assert level.sections
    for section in level.sections:
        assert section["seconds"] > 0


# WLD-1-31: hills with one rocky face.


def test_wld_1_31_the_sea_has_no_hills_but_the_coast_and_the_land_do() -> None:
    """Also LVL-1-1-04 (D-318): the rocky islands at the start of 1-1 have rocky faces."""
    assert LEVEL_1_1.sections[0]["name"] == "rocky islands"
    assert LEVEL_1_1.sections[0]["scarps"] is not None
    for section in LEVEL_1_1.sections[1:-1]:
        assert section.get("scarps") is None, section["name"]
    assert LEVEL_1_1.sections[-1]["scarps"] is not None
    for section in LEVEL_1_2.sections:
        assert section["scarps"] is not None, section["name"]


def test_wld_1_31_the_hills_faces_look_one_way_and_are_short_and_steep() -> None:
    for section in LEVEL_1_2.sections:
        scarps = section["scarps"]
        assert scarps["angleDeg"] == SCARP_ANGLE
        assert scarps["face"] == SCARP_FACE
        assert scarps["face"] < 0.15
        assert scarps["lowest"] == 0
        assert scarps["height"] > 0
        # The face is steep enough for the rock (a slope over 0.5) at its full height.
        assert scarps["height"] / (scarps["face"] * scarps["wavelength"]) > 0.5
