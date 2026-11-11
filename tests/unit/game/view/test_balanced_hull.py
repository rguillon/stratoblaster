# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/balanced_hull.py` (GFX-SHIP-01, D-327)."""

import pytest

from game.view import balanced_hull as hull
from game.view.balanced_hull import (
    STATIONS,
    TOP_POINTS,
    hull_section,
    hull_sections,
    smooth_max,
    smooth_stations,
    top_height,
)


def test_gfx_ship_01_the_smooth_maximum_rounds_the_joint_and_keeps_the_far_values() -> None:
    assert smooth_max(1, 0, 0.1) == pytest.approx(1)
    assert smooth_max(0.3, 0.3, 0.1) > 0.3
    assert smooth_max(0.3, 0.29, 0.1) >= 0.3


def test_gfx_ship_01_the_stations_are_kept_and_the_sizes_never_go_negative() -> None:
    rows = smooth_stations(STATIONS, 3)
    assert len(rows) == (len(STATIONS) - 1) * 3 + 1
    for k, station in enumerate(STATIONS):
        assert rows[k * 3] == pytest.approx(station)
    assert all(v >= 0 for row in rows for v in row[1:])


def test_gfx_ship_01_the_top_is_mirrored_and_meets_the_wings_top_at_the_chine_edge() -> None:
    station = STATIONS[6]
    edge = station[hull.CHINE_HALF_WIDTH]
    assert top_height(station, edge * 0.9999) == pytest.approx(hull.CHINE_EDGE, abs=1e-3)
    assert top_height(station, edge * 1.01) == 0
    for x in [0, 0.2, 0.42, 0.6]:
        assert top_height(station, x) == pytest.approx(top_height(station, -x))


def test_gfx_ship_01_every_section_has_the_same_ring_and_both_ends_close() -> None:
    """D-332: the nose and the tail end in a point: nothing comes out of the body's back."""
    sections = hull_sections()
    counts = {len(ring) for _z, ring in sections}
    assert counts == {TOP_POINTS + 2}
    for end in [sections[0][1], sections[-1][1]]:
        assert all(abs(p[0]) < 1e-9 and abs(p[1]) < 1e-9 for p in end)


def test_gfx_ship_01_a_section_runs_over_the_top_then_along_the_belly() -> None:
    _z, ring = hull_section(STATIONS[6])
    top = ring[:TOP_POINTS]
    assert top[0][0] > 0 > top[-1][0]
    assert all(p[1] >= 0 for p in top)
    assert all(p[1] < 0 for p in ring[TOP_POINTS:])


def test_gfx_ship_01_station_at_gives_each_station_and_blends_between() -> None:
    station = STATIONS[6]
    assert hull.station_at(station[hull.Z]) == pytest.approx(station)
    between = hull.station_at((STATIONS[6][hull.Z] + STATIONS[7][hull.Z]) / 2)
    assert STATIONS[7][hull.Z] < between[hull.Z] < STATIONS[6][hull.Z]
