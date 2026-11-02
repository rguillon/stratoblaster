# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/props/crag_props.py` (GFX-PROP-19, WLD-1-31)."""

from typing import Any

import pytest
from helpers.geometry_checks import bounds, check_prop

from game.config.cliffs import CRAG_BLOCK_IDS, MESA_BLOCK_IDS
from game.view.props.crag_props import CRAG_MODELS, MESA_MODELS

# A box has 12 triangles; a boulder of pushed facets has many more.
BOX_TRIANGLES = 12


def _models() -> list[Any]:
    return [CRAG_MODELS[i] for i in CRAG_BLOCK_IDS] + [MESA_MODELS[i] for i in MESA_BLOCK_IDS]


def _colors(geo: Any) -> set[tuple[float, ...]]:
    return {tuple(geo.colors[k : k + 3]) for k in range(0, len(geo.colors), 4)}


@pytest.mark.parametrize("factory", _models())
def test_gfx_prop_19_a_block_is_a_rough_boulder_not_a_box(factory: Any) -> None:
    prop = factory()
    assert check_prop(prop) > 0
    structure = prop.structure
    assert len(structure.indices) // 3 > 4 * BOX_TRIANGLES
    # Each facet its own shade.
    assert len(_colors(structure)) > 8


@pytest.mark.parametrize("factory", _models())
def test_gfx_prop_19_a_block_stands_on_the_ground_about_a_unit_wide_and_high(factory: Any) -> None:
    low, high = bounds(factory().structure)
    assert -0.15 < low[1] < 0.15
    assert 0.85 < high[1] < 1.15
    assert 0.8 < high[0] - low[0] < 1.4
    assert 0.8 < high[2] - low[2] < 1.4


def test_gfx_prop_19_the_three_shapes_differ_and_the_mesa_rock_is_red() -> None:
    crag = [CRAG_MODELS[i]().structure for i in CRAG_BLOCK_IDS]
    assert len({tuple(round(x, 4) for x in geo.positions) for geo in crag}) == 3
    for i in MESA_BLOCK_IDS:
        for color in _colors(MESA_MODELS[i]().structure):
            assert color[0] > color[2] + 0.2
