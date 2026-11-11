# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/balanced_hull.py` (GFX-SHIP-01, D-327)."""

import math

import pytest

from game.view import balanced_hull as hull
from game.view import balanced_ship as ship
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


def test_gfx_ship_01_the_shoulders_swell_out_of_the_back_without_a_dip() -> None:
    """Between the body's back and a nacelle shoulder, the fillet keeps the top from sagging."""
    station = STATIONS[7]
    back = top_height(station, 0)
    shoulder = top_height(station, hull.SHOULDER_X)
    lowest = min(top_height(station, x / 100) for x in range(int(hull.SHOULDER_X * 100) + 1))
    assert lowest >= min(back, shoulder) * 0.75


def test_gfx_ship_01_every_section_has_the_same_ring_the_nose_closes_the_tail_is_cut() -> None:
    """The nose ends in a point; the tail is cut off over the reactors' nozzles (and capped)."""
    sections = hull_sections()
    counts = {len(ring) for _z, ring in sections}
    assert counts == {TOP_POINTS + 2}
    assert all(abs(p[0]) < 1e-9 and abs(p[1]) < 1e-9 for p in sections[0][1])
    tail = sections[-1][1]
    assert max(p[0] for p in tail) > hull.SHOULDER_X


def test_gfx_ship_01_the_back_stands_over_the_intakes_and_nacelles() -> None:
    """D-327: from the intakes back, the shoulders stay well over the tubes inside them."""
    intake_top = ship.INTAKE_Y + max(r for _z, r in ship.INTAKE)
    nacelle_top = ship.REACTOR_Y + ship.REACTOR["radius"] * 1.1
    # The nacelles run from the intakes' back (their front) to the tail.
    nacelle_front = ship.INTAKE_Z + ship.INTAKE[0][0]
    for station in STATIONS[5:]:
        under = nacelle_top if station[hull.Z] <= nacelle_front else intake_top
        assert top_height(station, hull.SHOULDER_X) >= under + 0.05, station


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


def test_gfx_ship_01_an_armour_plate_lies_on_the_hull() -> None:
    """D-328: its top follows the hull a thickness over it; its underside sinks into the skin."""
    sections = hull.plate_sections([0.3, 0.55], [0.3, -0.5], 0.04, 5)
    assert sections[0][0] == pytest.approx(0.3)
    assert sections[-1][0] == pytest.approx(-0.5)
    for z, ring in sections:
        assert len(ring) == 10
        station = hull.station_at(z)
        for x, y in ring[:5]:
            assert y == pytest.approx(top_height(station, x) + 0.04)
        for x, y in ring[5:]:
            assert y < top_height(station, x)
        assert ring[0][0] == pytest.approx(0.55)
        assert ring[4][0] == pytest.approx(0.3)


def test_gfx_ship_01_the_booster_humps_rise_out_of_the_back_and_cover_their_engines() -> None:
    """D-328: the boosters are humps of the hull's skin, not tubes on it, their engines inside."""
    engine = ship.BOOSTER_ENGINE
    back_end = engine["z"] + engine["length"] / 2
    station = hull.station_at(-1.0)
    assert top_height(station, hull.BOOSTER_X) > top_height(station, 0) + 0.1
    for z in [back_end, -1.9, -1.99]:
        station = hull.station_at(z)
        for dx in [-0.06, 0, 0.06]:
            # The engine's top, round its axis.
            top = engine["y"] + (engine["radius"] ** 2 - dx * dx) ** 0.5
            assert top_height(station, hull.BOOSTER_X + dx) > top, (z, dx)


def test_gfx_ship_01_the_tail_face_wraps_all_four_engines() -> None:
    """D-328: one engine block: the hull runs to the nozzles, the engines just out behind it."""
    tail_z = STATIONS[-1][hull.Z]
    nacelle_end = ship.REACTOR_Z - ship.REACTOR["length"] / 2
    booster_end = ship.BOOSTER_ENGINE["z"] - ship.BOOSTER_ENGINE["length"] / 2
    for end in [nacelle_end, booster_end]:
        assert 0 < tail_z - end <= 0.2


def test_gfx_trim_the_nacelles_stay_under_the_hulls_edge_seen_from_above() -> None:
    """D-330: aft, the chine is wider than the nacelles, so the trim runs unbroken."""
    widest = ship.REACTOR_OFFSET_X + ship.REACTOR["radius"]
    # The nacelle is at its widest from 0.3 of its length ahead of its middle (`build_reactor`).
    full = ship.REACTOR_Z + ship.REACTOR["length"] * 0.3
    for z, _ring in hull_sections():
        if z <= full:
            assert hull.station_at(z)[hull.CHINE_HALF_WIDTH] >= widest + 0.04, z


def test_gfx_trim_the_tails_lean_out_no_further_than_the_hulls_edge() -> None:
    """D-330: seen from above, the canted tails stay inside the hull's outline."""
    span = max(x for x, _z in ship.TAIL)
    root_x = 0.38
    tip_x = root_x + span * math.sin(ship.TAIL_CANT)
    for _x, z in ship.TAIL:
        assert tip_x < hull.station_at(z)[hull.CHINE_HALF_WIDTH] - 0.03
