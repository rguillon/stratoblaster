"""Unit tests of `src/game/config/cars.py`."""

from game.config.cars import CAR_IDS, CAR_RULES
from game.config.tile_buildings import TILE


def test_p15_r11_every_car_id_is_a_kind_of_the_car_rules() -> None:
    assert set(CAR_IDS.values()) == set(CAR_RULES.kinds)


def test_p15_r11_car_ids_are_unique() -> None:
    assert len(set(CAR_RULES.kinds)) == len(CAR_RULES.kinds)


def test_p15_r11_car_traffic_numbers_are_in_range() -> None:
    assert 0 < CAR_RULES.density <= 1
    assert 0 < CAR_RULES.lift < 1
    assert 0 < CAR_RULES.scale <= 1
    low, high = CAR_RULES.speed
    assert 0 < low < high


def test_p15_r11_cars_sit_on_the_tile_sidewalk() -> None:
    assert CAR_RULES.sidewalk == TILE.sidewalk
