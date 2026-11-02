# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/props/tile_residences.py`."""

from typing import Any

import pytest
from helpers.geometry_checks import check_colored, footprint, height

from game.config.tile_buildings import TILE
from game.view.props.tile_kit import geometry_of, tile_kit
from game.view.props.tile_residences import build_residence, pods


@pytest.mark.parametrize("seed", range(1, 9))
def test_gfx_bldg_09_a_residence_is_a_well_formed_block_of_each_shape(seed: Any) -> None:
    k = tile_kit(20.0, 20.0, TILE.size, seed)
    build_residence(k)
    prop = geometry_of(k)
    check_colored(prop.structure)
    assert height(prop.structure) > 0


def test_gfx_bldg_09_residences_come_in_several_shapes() -> None:
    shapes = set()
    for seed in range(1, 9):
        k = tile_kit(20.0, 20.0, TILE.size, seed)
        build_residence(k)
        shapes.add(round(height(geometry_of(k).structure), 3))
    assert len(shapes) > 1


@pytest.mark.parametrize(("w", "d"), [(30.0, 10.0), (10.0, 30.0)])
def test_gfx_bldg_09_a_long_plot_takes_two_pods_along_its_length(w: float, d: float) -> None:
    k = tile_kit(w, d, TILE.size, 1)
    pods(k)
    structure = geometry_of(k).structure
    check_colored(structure)
    width, depth = footprint(structure)
    along, across = (width, depth) if w > d else (depth, width)
    # Two pods side by side along the plot's length, one deep across it.
    radius = min(w, d) * 0.38
    assert along == pytest.approx(max(w, d) * 0.5 + 2 * radius, rel=0.05)
    assert across == pytest.approx(2 * radius, rel=0.05)


def test_gfx_bldg_09_a_square_plot_takes_one_pod() -> None:
    k = tile_kit(10.0, 10.0, TILE.size, 1)
    pods(k)
    width, depth = footprint(geometry_of(k).structure)
    assert width == pytest.approx(depth, rel=0.05)
    assert width == pytest.approx(2 * 10.0 * 0.38, rel=0.05)
