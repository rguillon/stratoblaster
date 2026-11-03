# Copyright (c) 2026 Renaud Guillon
"""Unit tests of the Narwhal's hull (`narwhal_hull.py`): its flanks and the spans of its body."""

import pytest

from game.view.bosses.world_2 import narwhal_hull as module


def test_the_hull_is_widest_amidships_and_narrows_at_its_stern_and_bow() -> None:
    # FB-NARWHAL-02: the gill slits down the flanks follow the hull's half width.
    assert module.half_width(0) == pytest.approx(17.6, abs=0.05)
    assert module.half_width(-50) == pytest.approx(10.875)
    assert module.half_width(40) == pytest.approx(13.58, abs=0.01)


def test_a_span_of_the_hull_starts_and_ends_at_its_bounds_with_the_stations_between() -> None:
    # FB-NARWHAL-06 (D-254): the caps over the regions are lofted from the hull's own stations.
    stations, first = module.hull_span(-41.2, -8)
    assert [st[0] for st in stations] == [-41.2, -40, -16, -8]
    assert first == 1
    stations, first = module.hull_span(module.SPINE_SPAN[0], module.SPINE_SPAN[1] + 0.2)
    assert [st[0] for st in stations] == [-8, 10, 30, 40.2]
    assert first == 3


def test_the_deck_under_the_armour_lies_just_over_the_caps_bottom() -> None:
    # BOSS-52: the frame floor (the armour's lowest point + 0.6) must clear the core's deck.
    assert module.CAP_BOTTOM < module.DECK < module.CAP_BOTTOM + 0.6
