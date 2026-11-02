# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_3/mangrove_croc_model.py`: its hull and ring dome."""

from typing import Any

import pytest
from helpers.bosses_worlds_probe import muzzle_kinds
from helpers.view_probes import drawn

from game.view.bosses.world_3 import mangrove_croc_model as module


def test_top_at_follows_the_hull_between_its_stations() -> None:
    first = module.HULL[0]
    second = module.HULL[1]
    assert module.top_at(first[0]) == first[3]
    middle = (first[0] + second[0]) / 2
    assert module.top_at(middle) == pytest.approx((first[3] + second[3]) / 2)


def test_top_at_past_the_nose_is_the_last_station_height() -> None:
    last = module.HULL[len(module.HULL) - 1]
    assert module.top_at(last[0] + 10) == last[3]


def test_the_ring_dome_on_its_back_is_where_its_rings_leave_from() -> None:
    assert muzzle_kinds(drawn(module.draw_back)) == ["ring"]


def test_its_back_has_no_dome_when_the_design_has_no_ring_muzzle(monkeypatch: Any) -> None:
    monkeypatch.setattr(module, "CROC_DOME", [])
    result = drawn(module.draw_back)
    assert result["muzzles"] == []
    # The scutes, moss and vent are still laid on its back.
    assert len(result["parts"].hull.geometry.positions) > 0
