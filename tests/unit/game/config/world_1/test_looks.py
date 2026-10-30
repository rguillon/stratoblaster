"""Unit tests of `src/game/config/world_1/looks.py`."""

import pytest

from game.config.world_1.looks import (
    LEVEL_1_1_LOOK,
    LEVEL_1_2_LOOK,
    LEVEL_1_3_LOOK,
    LEVEL_1_4_LOOK,
    LEVEL_1_5_LOOK,
)

LOOKS = [LEVEL_1_1_LOOK, LEVEL_1_2_LOOK, LEVEL_1_3_LOOK, LEVEL_1_4_LOOK, LEVEL_1_5_LOOK]
SECTIONS = ("sky", "fog", "sun", "ambient", "terrain", "clouds", "roads", "props", "glow")


def test_p06_r05_every_level_of_the_world_has_a_look() -> None:
    assert len(LOOKS) == 5


@pytest.mark.parametrize("look", LOOKS)
def test_p06_r05_a_look_has_every_section_the_scenery_reads(look) -> None:
    for section in SECTIONS:
        assert look[section] is not None, section


@pytest.mark.parametrize("look", LOOKS)
def test_p06_r05_sky_stops_are_colours_in_range(look) -> None:
    assert look.sky.stops
    for stop in look.sky.stops:
        assert len(stop.color) == 3
        assert all(0 <= c <= 1 for c in stop.color), stop.color


@pytest.mark.parametrize("look", LOOKS)
def test_p06_r05_fog_fades_out_between_its_start_and_end(look) -> None:
    assert 0 < look.fog.start < look.fog.end
