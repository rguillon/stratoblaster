"""Unit tests of `src/game/view/props/tile_homesteads.py`."""

import pytest
from helpers.geometry_checks import check_colored, height

from game.config.tile_buildings import TILE
from game.view.props.tile_homesteads import build_homestead
from game.view.props.tile_kit import geometry_of, tile_kit


@pytest.mark.parametrize("seed", range(1, 9))
def test_p15_r09_a_homestead_is_a_well_formed_outpost_of_each_silhouette(seed):
    k = tile_kit(20.0, 20.0, TILE.size, seed)
    build_homestead(k)
    prop = geometry_of(k)
    check_colored(prop.structure)
    assert height(prop.structure) > 0


def test_p15_r09_homesteads_come_in_several_silhouettes():
    heights = set()
    for seed in range(1, 9):
        k = tile_kit(20.0, 20.0, TILE.size, seed)
        build_homestead(k)
        heights.add(round(height(geometry_of(k).structure), 3))
    assert len(heights) > 1
