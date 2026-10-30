"""Unit tests of `src/game/view/props/tile_residences.py`."""

import pytest
from helpers.geometry_checks import check_colored, height

from game.config.tile_buildings import TILE
from game.view.props.tile_kit import geometry_of, tile_kit
from game.view.props.tile_residences import build_residence


@pytest.mark.parametrize("seed", range(1, 9))
def test_p15_r09_a_residence_is_a_well_formed_block_of_each_shape(seed):
    k = tile_kit(20.0, 20.0, TILE.size, seed)
    build_residence(k)
    prop = geometry_of(k)
    check_colored(prop.structure)
    assert height(prop.structure) > 0


def test_p15_r09_residences_come_in_several_shapes():
    shapes = set()
    for seed in range(1, 9):
        k = tile_kit(20.0, 20.0, TILE.size, seed)
        build_residence(k)
        shapes.add(round(height(geometry_of(k).structure), 3))
    assert len(shapes) > 1
