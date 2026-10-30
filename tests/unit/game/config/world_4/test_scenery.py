"""Unit tests of `src/game/config/world_4/scenery.py`."""

import pytest
from helpers.config_checks import assert_scenery_level
from helpers.geometry_checks import height

from config.scenery_stage import SCENERY_STAGE_CONFIG
from core.scenery.height_field import terrain_ceiling
from game.config.scenery_look import BASE_SCENERY_LOOK, PLAYFIELD_CAMERA
from game.config.world_4.scenery import LEVEL_4_1, LEVEL_4_2, LEVEL_4_3, LEVEL_4_4, LEVEL_4_5
from game.sim.scenery_build import scenery_level
from game.view.props.tile_models import TILE_MODELS, build_tile_model

LEVELS = [LEVEL_4_1, LEVEL_4_2, LEVEL_4_3, LEVEL_4_4, LEVEL_4_5]


@pytest.mark.parametrize("level", LEVELS)
def test_p10_r03_level_scenery_names_its_level_and_scrolls(level) -> None:
    assert level.id.startswith("world-4-")
    assert_scenery_level(level, level.id.removeprefix("world-"))


@pytest.mark.parametrize("level", LEVELS)
def test_p10_r03_level_sections_have_positive_lengths(level) -> None:
    assert level.sections
    for section in level.sections:
        assert section["seconds"] > 0


def _tallest_building() -> float:
    return max(height(build_tile_model(m).structure) for m in TILE_MODELS)


@pytest.mark.parametrize("level", LEVELS)
def test_p10_r08_the_tallest_roof_stays_under_the_lowest_cloud_layer(level) -> None:
    # The skyscrapers poked through the clouds, or met them and z-fought: the city ground is low
    # enough that the tallest roof stays the clouds' clearance under the lowest layer.
    scale = PLAYFIELD_CAMERA.groundScale
    roof = (terrain_ceiling(scenery_level(level)) + _tallest_building()) * scale
    lowest = min(layer.altitude for layer in BASE_SCENERY_LOOK.clouds)
    assert roof + SCENERY_STAGE_CONFIG.cloud_clearance <= lowest
