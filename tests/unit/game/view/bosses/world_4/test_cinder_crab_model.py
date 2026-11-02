# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_4/cinder_crab_model.py`: its carapace and dome."""

from typing import Any

import pytest
from helpers.bosses_worlds_probe import muzzle_kinds
from helpers.view_probes import drawn

from game.view.bosses.world_4 import cinder_crab_model as module


def test_station_at_interpolates_the_carapace_between_its_stations() -> None:
    first = module.CARAPACE[0]
    second = module.CARAPACE[1]
    middle = (first[0] + second[0]) / 2
    assert module._station_at(first[0], 3) == first[3]
    assert module._station_at(middle, 3) == pytest.approx((first[3] + second[3]) / 2)


def test_station_at_past_the_last_station_is_its_value() -> None:
    last = module.CARAPACE[len(module.CARAPACE) - 1]
    assert module._station_at(last[0] + 10, 3) == last[3]
    assert module._station_at(last[0] + 10, 1) == last[1]


def test_the_dome_on_its_back_is_where_the_core_rings_leave_from() -> None:
    assert "ring" in muzzle_kinds(drawn(module._draw_back))


def test_its_back_has_no_dome_when_the_design_has_no_ring_muzzle(monkeypatch: Any) -> None:
    monkeypatch.setattr(module, "CRAB_DOME", [])
    result = drawn(module._draw_back)
    assert "ring" not in muzzle_kinds(result)
    # Soot, bolts and the vent are still laid on the carapace.
    assert len(result["parts"].hull.geometry.positions) > 0
