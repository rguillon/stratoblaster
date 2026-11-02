# Copyright (c) 2026 Renaud Guillon
"""Unit tests of the prop models against the levels that place them (GFX-PROP-03)."""

from game.config.world_1.scenery_coast import LEVEL_1_1, LEVEL_1_2
from game.config.world_1.scenery_country import LEVEL_1_3
from game.config.world_1.scenery_desert import LEVEL_1_4, LEVEL_1_5
from game.config.world_2.scenery import LEVEL_2_1, LEVEL_2_2, LEVEL_2_3, LEVEL_2_4, LEVEL_2_5
from game.config.world_3.scenery import LEVEL_3_1, LEVEL_3_2, LEVEL_3_3, LEVEL_3_4, LEVEL_3_5
from game.config.world_4.scenery import LEVEL_4_1, LEVEL_4_2, LEVEL_4_3, LEVEL_4_4, LEVEL_4_5
from game.view.props.prop_models import PROP_MODELS
from game.view.props.road_kit import ROAD_KIT, ROAD_SAMPLE_ID
from render.scenery.prop_field import level_prop_kinds

SCENERY_LEVELS = [
    LEVEL_1_1,
    LEVEL_1_2,
    LEVEL_1_3,
    LEVEL_1_4,
    LEVEL_1_5,
    LEVEL_2_1,
    LEVEL_2_2,
    LEVEL_2_3,
    LEVEL_2_4,
    LEVEL_2_5,
    LEVEL_3_1,
    LEVEL_3_2,
    LEVEL_3_3,
    LEVEL_3_4,
    LEVEL_3_5,
    LEVEL_4_1,
    LEVEL_4_2,
    LEVEL_4_3,
    LEVEL_4_4,
    LEVEL_4_5,
]


def _placed_kinds() -> set[str]:
    """Every prop kind and car kind some level places (checked over every level)."""
    placed: set[str] = set()
    for level in SCENERY_LEVELS:
        placed.update(level_prop_kinds(level))
        cars = level.props.cars
        if cars is not None:
            placed.update(cars.kinds)
    return placed


def test_gfx_prop_03_every_prop_model_is_placed_by_some_level_but_the_road_kit() -> None:
    """The road kit is shown by the props viewer only.

    The road kit (its pieces and its sample) is the one exception: the levels draw their streets.
    """
    placed = _placed_kinds()
    road_kit = {kit.id for kit in ROAD_KIT} | {ROAD_SAMPLE_ID}
    unplaced = sorted(kind for kind in PROP_MODELS if kind not in road_kit and kind not in placed)
    assert unplaced == []
    assert road_kit.isdisjoint(placed)
