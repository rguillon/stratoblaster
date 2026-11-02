# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/world_4/scenery.py`."""

from typing import Any

import pytest
from helpers.config_checks import assert_scenery_level
from helpers.geometry_checks import height

from config.scenery_stage import SCENERY_STAGE_CONFIG
from core.scenery.height_field import terrain_ceiling
from game.config.record import record
from game.config.scenery_look import BASE_SCENERY_LOOK, PLAYFIELD_CAMERA
from game.config.world_4.scenery import (
    CITY_GROUND,
    LEVEL_4_1,
    LEVEL_4_2,
    LEVEL_4_3,
    LEVEL_4_4,
    LEVEL_4_5,
    city_only,
)
from game.sim.scenery_build import scenery_level
from game.view.props.tile_models import TILE_MODELS, build_tile_model

LEVELS = [LEVEL_4_1, LEVEL_4_2, LEVEL_4_3, LEVEL_4_4, LEVEL_4_5]


@pytest.mark.parametrize("level", LEVELS)
def test_wld_4_01_level_scenery_names_its_level_and_scrolls(level: Any) -> None:
    """Each level's identity and ground speed (LVL-4-1-01 … LVL-4-5-01)."""
    assert level.id.startswith("world-4-")
    assert_scenery_level(level, level.id.removeprefix("world-"))


@pytest.mark.parametrize("level", LEVELS)
def test_wld_4_02_level_sections_have_positive_lengths(level: Any) -> None:
    """The sections of each level (LVL-4-1-02 … LVL-4-5-02)."""
    assert level.sections
    for section in level.sections:
        assert section["seconds"] > 0


def _tallest_building() -> float:
    return max(height(build_tile_model(m).structure) for m in TILE_MODELS)


@pytest.mark.parametrize("level", LEVELS)
def test_wld_4_10_the_tallest_roof_stays_under_the_lowest_cloud_layer(level: Any) -> None:
    """Also GFX-SKY-12."""
    # The skyscrapers poked through the clouds, or met them and z-fought: the city ground is low
    # enough that the tallest roof stays the clouds' clearance under the lowest layer.
    scale = PLAYFIELD_CAMERA.groundScale
    roof = (terrain_ceiling(scenery_level(level)) + _tallest_building()) * scale
    lowest = min(layer.altitude for layer in BASE_SCENERY_LOOK.clouds)
    assert roof + SCENERY_STAGE_CONFIG.cloud_clearance <= lowest


def test_wld_4_09_a_city_section_has_no_water_and_no_flattened_strip() -> None:
    """Also WLD-4-08: only buildings and roads, on flat paved ground."""
    river = record({
        "name": "riverside",
        "seconds": 10,
        "relief": {"base": 40},
        "treeDensity": 0.4,
        "surface": {"lush": 1},
        "channel": {"halfWidth": 30},
        "lakes": {"spacing": 200},
        "shore": {"width": 40},
        "flatten": {"halfWidth": 20},
    })
    city = city_only(river)
    for water in ("channel", "lakes", "shore", "flatten"):
        assert water not in city
    assert city.relief == CITY_GROUND
    assert city.treeDensity == 0
    assert (city.surface.paved, city.surface.lush) == (1, 0)
    assert city["name"] == "riverside"
    assert "channel" in river
    plain = city_only(record({"name": "plain", "seconds": 5}))
    assert "lakes" not in plain
