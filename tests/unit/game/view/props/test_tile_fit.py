"""Unit tests of `src/game/view/props/tile_fit.py`."""

import pytest
from helpers.geometry_checks import bounds, footprint

from game.config.tile_buildings import BUILDING_MARGIN, TILE
from game.view.props.tile_fit import fit_to_tiles, fitted, fitted_model, moved, on_tiles, tiles_for
from render.geometry.gradient_shapes import ColoredGeometry
from render.scenery.scenery_look import PropGeometry, PropPlume


def box(x0, x1, z0, z1, y1=3.0) -> ColoredGeometry:
    """A flat-shaded box footprint with corners at the given X and Z (a test shape)."""
    geo = ColoredGeometry()
    geo.positions = [
        x0,
        0,
        z0,
        x1,
        0,
        z0,
        x1,
        y1,
        z1,
        x0,
        y1,
        z1,
    ]
    geo.indices = [0, 1, 2, 0, 2, 3]
    geo.colors = [1, 1, 1, 1] * 4
    return geo


def test_p15_r07_a_footprint_is_a_whole_number_of_tiles_at_least_one():
    assert tiles_for(0) == 1
    assert tiles_for(TILE.size * 0.4) == 1
    assert tiles_for(TILE.size * 1.4) == 1
    assert tiles_for(TILE.size * 1.6) == 2
    assert tiles_for(TILE.size * 3) == 3


def test_p15_r07_a_footprint_of_tiles_is_its_width_less_the_margin():
    assert fitted(2) == pytest.approx(2 * TILE.size - 2 * BUILDING_MARGIN)
    assert fitted(1) == pytest.approx(TILE.size - 2 * BUILDING_MARGIN)


def test_p15_r07_moved_maps_x_and_z_and_keeps_the_heights_and_topology():
    geo = box(0, 2, 0, 4)
    result = moved(geo, lambda x, z: [x + 1, z * 2])
    assert result.positions[0] == 1
    assert result.positions[2] == 0
    assert result.positions[1] == geo.positions[1]
    assert result.indices == geo.indices
    assert result.colors == geo.colors
    assert result is not geo


def test_p15_r07_fit_to_tiles_stretches_the_footprint_to_whole_tiles():
    prop = PropGeometry(box(-3.0, 3.0, -4.0, 4.0))
    fitted_prop = fit_to_tiles(prop)
    width, depth = footprint(fitted_prop.structure)
    assert width == pytest.approx(fitted(tiles_for(6.0)))
    assert depth == pytest.approx(fitted(tiles_for(8.0)))


def test_p15_r07_fit_to_tiles_centres_the_footprint_on_the_origin():
    prop = PropGeometry(box(10.0, 14.0, 20.0, 26.0))
    low, high = bounds(fit_to_tiles(prop).structure)
    assert (low[0] + high[0]) / 2 == pytest.approx(0)
    assert (low[2] + high[2]) / 2 == pytest.approx(0)


def test_p15_r07_fit_to_tiles_keeps_the_heights():
    prop = PropGeometry(box(0, 5, 0, 5, y1=7.5))
    _, high = bounds(fit_to_tiles(prop).structure)
    assert high[1] == pytest.approx(7.5)


def test_p15_r07_lights_and_plumes_move_with_the_structure():
    lights = box(0, 5, 0, 5)
    plume = PropPlume((5.0, 2.0, 5.0), "smoke", 1.5)
    prop = PropGeometry(box(0, 5, 0, 5), lights, [plume])
    fitted_prop = fit_to_tiles(prop)
    assert fitted_prop.lights is not None
    assert fitted_prop.plumes[0].kind == "smoke"
    assert fitted_prop.plumes[0].scale == 1.5
    assert fitted_prop.plumes[0].at[1] == 2.0
    # The plume sat at the structure's corner: it is scaled with it, not left in place.
    assert fitted_prop.plumes[0].at[0] != 5.0


def test_p15_r07_a_prop_without_lights_or_plumes_keeps_none():
    fitted_prop = fit_to_tiles(PropGeometry(box(0, 5, 0, 5)))
    assert fitted_prop.lights is None
    assert fitted_prop.plumes is None


def test_p15_r07_an_empty_structure_is_returned_as_it_is():
    empty = PropGeometry(ColoredGeometry())
    assert fit_to_tiles(empty) is empty


def test_p15_r07_a_fitted_model_builds_its_prop_fitted():
    factory = fitted_model(lambda: PropGeometry(box(0, 3, 0, 3)))
    width, _ = footprint(factory().structure)
    assert width == pytest.approx(fitted(tiles_for(3.0)))


def test_p15_r07_on_tiles_wraps_every_model_of_a_table():
    table = on_tiles({"a": lambda: PropGeometry(box(0, 3, 0, 3))})
    assert set(table) == {"a"}
    width, _ = footprint(table["a"]().structure)
    assert width == pytest.approx(fitted(tiles_for(3.0)))
