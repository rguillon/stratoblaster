# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/balanced_cockpit.py` (GFX-SHIP-01, D-354)."""

import pytest

from game.view import balanced_cockpit as cockpit
from game.view.balanced_hull import STATIONS, Z, station_at, top_height


def test_gfx_ship_01_the_canopy_sits_on_the_deck_its_skin_closing_under_the_sill() -> None:
    """D-354: each section an arch on the hull's top, two points just under it, no gap."""
    for z, ring in cockpit.canopy_sections():
        assert len(ring) == cockpit.ARCH_POINTS + 2
        half = ring[0][0]
        sill = top_height(station_at(z), half)
        assert ring[0][1] == pytest.approx(sill)
        assert ring[cockpit.ARCH_POINTS - 1][1] == pytest.approx(sill)
        assert all(p[1] >= sill - 1e-9 for p in ring[: cockpit.ARCH_POINTS])
        assert all(p[1] < sill for p in ring[cockpit.ARCH_POINTS :])


def test_gfx_ship_01_the_canopy_rises_from_a_raked_windscreen_and_falls_into_the_spine() -> None:
    """D-354: low at both ends, its peak ahead of its middle, the windscreen the steeper end."""
    rows = cockpit.CANOPY_ROWS
    heights = [r[2] for r in rows]
    assert heights[0] == 0
    assert heights[-1] == 0
    peak = heights.index(max(heights))
    middle = (rows[0][0] + rows[-1][0]) / 2
    assert rows[peak][0] > middle
    front_rake = max(heights) / (rows[0][0] - rows[peak][0])
    back_fall = max(heights) / (rows[peak][0] - rows[-1][0])
    assert front_rake > back_fall
    # It stands in the body, behind the longer nose.
    assert STATIONS[0][Z] - rows[0][0] > 1.2


def test_gfx_ship_01_the_cockpit_inside_shows_under_the_glass() -> None:
    """D-354: the helmet and the seat fit under the canopy; the bow lies along its arch."""
    helmet = cockpit.HELMET
    top = cockpit.floor_height(helmet["z"]) + helmet["y"] + helmet["radius"]
    half, height = cockpit.canopy_at(helmet["z"])
    sill = cockpit.sill_height(helmet["z"], half)
    assert top < sill + height
    seat_z = cockpit.SEAT_ZS[0]
    half, height = cockpit.canopy_at(seat_z)
    head = cockpit.floor_height(seat_z) + cockpit.SEAT["headHeight"]
    assert head < cockpit.sill_height(seat_z, half) + height
    segments = cockpit.bow_segments()
    assert len(segments) == cockpit.BOW_SEGMENTS
    total = sum(s[3] for s in segments)
    half, height = cockpit.canopy_at(cockpit.BOW["z"])
    # About half an ellipse's perimeter round the windscreen.
    assert total > 2 * height + half


def test_gfx_ship_01_the_sill_rails_run_along_both_sides() -> None:
    for side in [1.0, -1.0]:
        sections = cockpit.rail_sections(side)
        assert len(sections) == len(cockpit.canopy_rows())
        for _z, ring in sections:
            assert all(p[0] * side > 0 for p in ring)
