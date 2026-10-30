"""Unit tests of `src/game/view/enemies/veteran_shapes.py`."""

import pytest
from helpers.view_probes import paths, recorder

from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies.veteran_shapes import (
    BAND_SECTION,
    WHITE,
    back_band,
    edge_strip,
    nose_gun,
    station_at,
)


def test_station_at_interpolates_between_the_two_stations_around_z():
    stations = [[0, 0, 0, 0], [2, 1, 2, 4], [4, 1, 1, 2]]
    # Between z = 0 and z = 2 the mix is halfway.
    assert station_at(stations, 1) == pytest.approx([1, 0.5, 1, 2])
    # Exactly on a station it is that station.
    assert station_at(stations, 2) == pytest.approx([2, 1, 2, 4])


def test_station_at_beyond_the_last_station_clamps_to_the_nose_station():
    stations = [[0, 1, 1, 1], [2, 3, 3, 3]]
    assert station_at(stations, 3) == pytest.approx([3, 3, 3, 3])


def test_station_at_with_equal_stations_does_not_divide_by_zero():
    stations = [[1, 1, 1, 1], [1, 2, 2, 2]]
    assert station_at(stations, 1) == pytest.approx([1, 1, 1, 1])


def test_station_at_without_stations_is_an_error():
    with pytest.raises(Exception, match="A loft needs stations"):
        station_at([], 0)


def test_nose_gun_grafts_a_barrel_with_a_muzzle_past_its_length():
    parts, log = recorder()
    nose_gun(parts, [1, 2, 3], 4, radius=0.5)
    assert paths(log) == ["hull.cylinder", "charge.cylinder", "muzzle"]
    radius, length, sides, color, place = log[0][1][:5]
    assert (radius, length, sides) == (0.5, 4, 6)
    assert color is ENEMY_LOOK.hull.dark
    assert place.at == pytest.approx([1, 2, 3])
    assert log[1][1][3] is WHITE
    assert log[1][1][4].at == pytest.approx([1, 2, 7])
    assert log[2][1] == ([1, 2, 7.8], "gun")


def test_back_band_lofts_an_open_strip_over_the_stations_between_span_ends():
    stations = [[0, 1, 1, 0], [4, 1, 1, 0]]
    builder, log = recorder()
    back_band(builder, stations, [1, 3], [1, 0, 0], lift=0.5)
    assert paths(log) == ["loft"]
    section, rings, color, paint, options = log[0][1]
    assert section is BAND_SECTION
    assert color == [1, 0, 0]
    assert paint is None
    assert options.open is True
    # The two rings are at z 1 and 3, each lifted 0.5 above the stations' top.
    assert [ring[0] for ring in rings] == pytest.approx([1, 3])
    assert [ring[1] for ring in rings] == pytest.approx([1.5, 1.5])


def test_edge_strip_sits_just_outside_the_edge_away_from_the_centre():
    strip = edge_strip([1, 0], [1, 2], 0.5)
    assert len(strip) == 4
    # The inner edge is the given edge, the outer one shifted 0.5 away from the origin (+x).
    assert strip[0] == pytest.approx([1, 0])
    assert strip[1] == pytest.approx([1, 2])
    assert strip[2][0] == pytest.approx(1.5)
    assert strip[3][0] == pytest.approx(1.5)


def test_edge_strip_flips_its_normal_to_point_outwards_for_any_edge_direction():
    forward = edge_strip([1, 0], [1, 2], 0.5)
    backward = edge_strip([1, 2], [1, 0], 0.5)
    # Both strips lie on the outer side (x > 1).
    assert forward[2][0] > 1 and backward[2][0] > 1


def test_nose_gun_default_radius_is_half_a_unit_thicker_than_zero():
    parts, log = recorder()
    nose_gun(parts, [0, 0, 0], 1)
    assert log[0][1][0] == pytest.approx(0.55)
