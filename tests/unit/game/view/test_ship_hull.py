# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/ship_hull.py` (GFX-SHIP-01, D-327, D-336)."""

import pytest

from game.view import ship_hull as hull
from game.view.ship_hull import (
    STATIONS,
    TOP_POINTS,
    hull_section,
    hull_sections,
    smooth_stations,
    top_height,
    top_ring,
    underside_height,
)


def test_gfx_ship_01_the_stations_are_kept_and_the_sizes_never_go_negative() -> None:
    rows = smooth_stations(STATIONS, 3)
    assert len(rows) == (len(STATIONS) - 1) * 3 + 1
    for k, station in enumerate(STATIONS):
        assert rows[k * 3] == pytest.approx(station)
    assert all(v >= 0 for row in rows for v in row[1:])


def test_gfx_ship_01_the_top_is_mirrored_and_meets_the_wings_top_at_the_chine_edge() -> None:
    station = STATIONS[7]
    edge = station[hull.CHINE_HALF_WIDTH]
    assert top_height(station, edge * 0.9999) == pytest.approx(hull.CHINE_EDGE, abs=1e-3)
    assert top_height(station, edge * 1.01) == 0
    for x in [0, 0.1, 0.2, 0.42, 0.6]:
        assert top_height(station, x) == pytest.approx(top_height(station, -x))


def test_gfx_ship_01_the_top_is_facets_rising_to_a_spine() -> None:
    """D-336: flat strake, bevelled shoulder, deck, spine ridge: highest in the middle."""
    station = STATIONS[7]
    ring = top_ring(station)
    assert len(ring) == TOP_POINTS
    heights = [p[1] for p in ring[: TOP_POINTS // 2 + 1]]
    assert heights == sorted(heights)
    assert ring[TOP_POINTS // 2] == pytest.approx([
        0,
        station[hull.BODY_HEIGHT] + station[hull.SPINE],
    ])
    # The strake is flat, at the wings' top face.
    assert ring[0][1] == pytest.approx(ring[1][1])


def test_gfx_ship_01_every_section_has_the_same_ring_the_nose_closes_the_back_is_square() -> None:
    """D-332: the nose ends in a point; D-356: the back is cut square, its strakes at full width."""
    sections = hull_sections()
    counts = {len(ring) for _z, ring in sections}
    assert counts == {TOP_POINTS + 6}
    assert all(abs(p[0]) < 1e-9 and abs(p[1]) < 1e-9 for p in sections[0][1])
    back = STATIONS[-1]
    assert back[hull.BODY_HALF_WIDTH] > 0.2
    assert back[hull.CHINE_HALF_WIDTH] == pytest.approx(
        max(s[hull.CHINE_HALF_WIDTH] for s in STATIONS)
    )


def test_gfx_ship_01_a_section_runs_over_the_top_then_along_the_belly() -> None:
    _z, ring = hull_section(STATIONS[7])
    top = ring[:TOP_POINTS]
    assert top[0][0] > 0 > top[-1][0]
    assert all(p[1] >= 0 for p in top)
    assert all(p[1] < 0 for p in ring[TOP_POINTS:])
    under = ring[TOP_POINTS:]
    assert under[0][0] < 0 < under[-1][0]


def test_gfx_ship_01_station_at_gives_each_station_and_blends_between() -> None:
    station = STATIONS[6]
    assert hull.station_at(station[hull.Z]) == pytest.approx(station)
    between = hull.station_at((STATIONS[6][hull.Z] + STATIONS[7][hull.Z]) / 2)
    assert STATIONS[7][hull.Z] < between[hull.Z] < STATIONS[6][hull.Z]


def test_gfx_ship_01_the_underside_runs_from_the_belly_out_to_the_chine_edge() -> None:
    """D-349: flat under the belly, rising along the flanks to the chine's edge."""
    station = STATIONS[7]
    assert underside_height(station, 0) == pytest.approx(-station[hull.BELLY_DEPTH])
    edge = station[hull.CHINE_HALF_WIDTH]
    assert underside_height(station, edge) == pytest.approx(-hull.chine_edge(station))
    assert underside_height(station, 0.2) == pytest.approx(underside_height(station, -0.2))
    assert (
        underside_height(station, 0)
        < underside_height(station, 0.2)
        < underside_height(station, edge)
    )


def test_gfx_ship_01_past_the_hulls_ends_and_chines_the_last_sizes_hold() -> None:
    """Behind the back the back's sizes; past the chine its edge's height under it."""
    back = STATIONS[-1]
    assert hull.station_at(back[hull.Z] - 1) == pytest.approx(back)
    assert hull.station_at(STATIONS[0][hull.Z] + 1) == pytest.approx(STATIONS[0])
    station = STATIONS[7]
    beyond = station[hull.CHINE_HALF_WIDTH] + 0.1
    assert underside_height(station, beyond) == pytest.approx(-hull.chine_edge(station))
    assert top_height(station, beyond) == 0
    # Out along the chine's flat, its edge's height.
    chine = station[hull.CHINE_HALF_WIDTH] - 0.01
    assert top_height(station, chine) == pytest.approx(hull.chine_edge(station))
