# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/props/city_lots.py`."""

from typing import Any

import pytest
from helpers.geometry_checks import bounds, check_colored, height

from game.config.tile_buildings import TILE
from game.view.props.city_lots import (
    courtyard,
    crown,
    l_block,
    plinth,
    round_tower,
    slab,
    stepped_tower,
    volume,
)
from game.view.props.tile_city import lot_kit
from game.view.props.tile_kit import geometry_of, tile_kit

FACADES = [[0.6, 0.6, 0.6]]
LIGHTS = [[1.0, 0.9, 0.5]]
LOT = [0.0, 0.0, 16.0, 16.0]


def kit_for(seed: Any = 2) -> Any:
    k = tile_kit(16.0, 16.0, TILE.size, seed)
    return k, lot_kit(k, FACADES, LIGHTS)


def test_gfx_bldg_10_a_volume_is_a_box_up_to_its_height() -> None:
    k, kit = kit_for()
    volume(kit, LOT, 0.0, 12.0)
    prop = geometry_of(k)
    check_colored(prop.structure)
    low, high = bounds(prop.structure)
    assert high[1] == pytest.approx(12.0)
    assert low[1] == pytest.approx(0.0)


def test_d210_a_volume_under_a_floor_high_gets_no_windows() -> None:
    k, kit = kit_for()
    volume(kit, LOT, 0.0, 3.0)
    assert geometry_of(k).windows is not None
    assert len(geometry_of(k).windows.positions) == 0


def test_d210_a_volume_gets_one_window_quad_per_wall() -> None:
    """GFX-BLDG-13."""
    k, kit = kit_for()
    volume(kit, LOT, 0.0, 20.0)
    windows = geometry_of(k).windows
    check_colored(windows)
    assert len(windows.indices) == 4 * 6
    assert len(geometry_of(k).lights.positions) == 0


def test_gfx_bldg_10_the_plinth_covers_the_lot_and_returns_its_height() -> None:
    k, kit = kit_for()
    base = plinth(kit, LOT)
    assert 3 <= base <= 6
    assert height(geometry_of(k).structure) == pytest.approx(base)


@pytest.mark.parametrize("shape", [stepped_tower, round_tower, slab, courtyard, l_block])
def test_gfx_bldg_10_each_lot_shape_is_a_well_formed_volume(shape: Any) -> None:
    k, kit = kit_for()
    shape(kit, LOT)
    check_colored(geometry_of(k).structure)
    assert height(geometry_of(k).structure) > 0


def test_gfx_bldg_10_a_crown_sits_on_the_roof_at_the_given_point() -> None:
    k, kit = kit_for()
    # The point is (x, y, z): the crown stands at the top of its tower.
    crown(kit, [8.0, 12.0, 8.0], 2.0)
    check_colored(geometry_of(k).structure)
    _, high = bounds(geometry_of(k).structure)
    assert high[1] >= 12.0


def _fixed(value: float) -> Any:
    """Return a random generator stand-in that always draws `value`."""
    return lambda: value


def _half_width_at(geo: Any, y: float) -> float:
    """Return the largest |x| of the vertices of `geo` at height `y`."""
    xs = geo.positions[0::3]
    ys = geo.positions[1::3]
    return max(abs(x) for x, vy in zip(xs, ys, strict=True) if vy == pytest.approx(y))


def test_gfx_bldg_10_a_stepped_tower_steps_back_at_each_of_its_tiers() -> None:
    k, kit = kit_for()
    # Draws of 0.9: three tiers, each `shrink` times narrower than the one under it.
    kit.random = _fixed(0.9)
    stepped_tower(kit, LOT)
    structure = geometry_of(k).structure
    base = 3 + 3 * 0.9
    tier = 12 + 18 * 0.9
    width = 16 * (0.55 + 0.35 * 0.9)
    shrink = 0.6 + 0.2 * 0.9
    # The top of the third tier, under its crown.
    top = base + 3 * tier
    assert height(structure) > top
    assert _half_width_at(structure, base + tier) == pytest.approx(width / 2)
    assert _half_width_at(structure, top) == pytest.approx(width * shrink * shrink / 2)


@pytest.mark.parametrize(("draw", "lit"), [(0.1, True), (0.9, False)])
def test_gfx_bldg_10_a_slab_has_a_neon_sign_now_and_then(draw: float, lit: bool) -> None:
    k, kit = kit_for()
    kit.random = _fixed(draw)
    slab(kit, LOT)
    lights = geometry_of(k).lights
    assert (len(lights.positions) > 0) is lit
    if lit:
        check_colored(lights)
        # In front of the slab, from 3 up.
        low, _ = bounds(lights)
        assert low[2] < -LOT[3] / 2
        assert low[1] == pytest.approx(3)
