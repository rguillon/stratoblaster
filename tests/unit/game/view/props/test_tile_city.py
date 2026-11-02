# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/props/tile_city.py`."""

from typing import Any

import pytest
from helpers.geometry_checks import check_colored, footprint, height

from game.config.tile_buildings import TILE
from game.view.props.tile_city import (
    build_car_park,
    build_midrise,
    build_office,
    build_park,
    build_plaza,
    build_skyscraper,
    build_tower,
    build_yard,
)
from game.view.props.tile_kit import geometry_of, tile_kit

BUILDERS = {
    "midrise": build_midrise,
    "office": build_office,
    "tower": build_tower,
    "skyscraper": build_skyscraper,
    "carPark": build_car_park,
    "yard": build_yard,
    "plaza": build_plaza,
    "park": build_park,
}


def built(builder: Any, w: Any = 20.0, d: Any = 20.0, seed: Any = 3) -> Any:
    k = tile_kit(w, d, TILE.size, seed)
    builder(k)
    return geometry_of(k)


@pytest.mark.parametrize("name", list(BUILDERS))
def test_gfx_bldg_09_each_city_building_stands_on_the_ground(name: Any) -> None:
    prop = built(BUILDERS[name])
    check_colored(prop.structure)
    assert height(prop.structure) > 0


def test_gfx_bldg_10_the_city_towers_rise_above_the_midrise_blocks() -> None:
    assert height(built(build_skyscraper).structure) > height(built(build_midrise).structure)


def test_gfx_bldg_11_the_open_lots_are_low_compared_with_the_towers() -> None:
    assert height(built(build_park).structure) < height(built(build_tower).structure)
    assert height(built(build_plaza).structure) < height(built(build_skyscraper).structure)


def test_gfx_bldg_03_a_building_fills_the_plot_it_is_given() -> None:
    width, depth = footprint(built(build_office, w=16.0, d=24.0).structure)
    assert width == pytest.approx(16.0, abs=0.5)
    assert depth == pytest.approx(24.0, abs=0.5)
