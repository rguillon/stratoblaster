# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/world_2/looks.py`."""

from typing import Any

import pytest

from game.config.world_2.looks import (
    LEVEL_2_1_LOOK,
    LEVEL_2_2_LOOK,
    LEVEL_2_3_LOOK,
    LEVEL_2_4_LOOK,
    LEVEL_2_5_LOOK,
)

LOOKS = [LEVEL_2_1_LOOK, LEVEL_2_2_LOOK, LEVEL_2_3_LOOK, LEVEL_2_4_LOOK, LEVEL_2_5_LOOK]
SECTIONS = ("sky", "fog", "sun", "ambient", "terrain", "clouds", "roads", "props", "glow")


def test_wld_2_15_every_level_of_the_world_has_a_look() -> None:
    """Each level has its own time of day (WLD-2-15)."""
    assert len(LOOKS) == 5


@pytest.mark.parametrize("look", LOOKS)
def test_wld_2_12_a_look_has_every_section_the_scenery_reads(look: Any) -> None:
    for section in SECTIONS:
        assert look[section] is not None, section


@pytest.mark.parametrize("look", LOOKS)
def test_wld_2_15_sky_stops_are_colours_in_range(look: Any) -> None:
    assert look.sky.stops
    for stop in look.sky.stops:
        assert len(stop.color) == 3
        assert all(0 <= c <= 1 for c in stop.color), stop.color


@pytest.mark.parametrize("look", LOOKS)
def test_wld_2_15_fog_fades_out_between_its_start_and_end(look: Any) -> None:
    assert 0 < look.fog.start < look.fog.end
