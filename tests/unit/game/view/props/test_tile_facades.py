"""Unit tests of `src/game/view/props/tile_facades.py`: the facades of city buildings."""

from game.config.tile_buildings import TILE
from game.view.props.tile_city import city
from game.view.props.tile_facades import panels_left
from game.view.props.tile_kit import geometry_of, tile_kit


def test_p15_r09_the_facades_of_a_city_block_are_panelled_and_lit():
    k = tile_kit(20.0, 20.0, TILE.size, 4)
    city(k, [30.0, 40.0], [[0.6, 0.6, 0.6]], [[1.0, 0.9, 0.5]])
    prop = geometry_of(k)
    assert len(prop.structure.positions) > 0
    assert prop.lights is not None
    assert len(prop.lights.positions) > 0


def test_p15_r09_the_panels_left_of_a_lit_face_is_a_non_negative_span():
    k = tile_kit(20.0, 20.0, TILE.size, 4)
    assert panels_left(k.lights) >= 0
