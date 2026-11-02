# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/cars.py`."""

from game.config.cars import CAR_IDS, CAR_RULES
from game.config.tile_buildings import TILE


def test_gfx_car_01_every_car_id_is_a_kind_of_the_car_rules() -> None:
    assert set(CAR_IDS.values()) == set(CAR_RULES.kinds)


def test_gfx_car_01_car_ids_are_unique() -> None:
    assert len(set(CAR_RULES.kinds)) == len(CAR_RULES.kinds)


def test_gfx_car_06_car_traffic_numbers_are_in_range() -> None:
    """Also GFX-CAR-04 (the scale) and GFX-CAR-07 (the lift)."""
    assert 0 < CAR_RULES.density <= 1
    assert 0 < CAR_RULES.lift < 1
    assert 0 < CAR_RULES.scale <= 1
    low, high = CAR_RULES.speed
    assert 0 < low < high


def test_gfx_car_07_cars_sit_on_the_tile_sidewalk() -> None:
    assert CAR_RULES.sidewalk == TILE.sidewalk
