# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_4/magma_salamander_model.py`: the vent on its back."""

from typing import Any

from helpers.bosses_worlds_probe import muzzle_kinds
from helpers.view_probes import drawn

from game.view.bosses.world_4 import magma_salamander_model as module


def test_sign_is_minus_one_zero_or_one() -> None:
    assert [module._sign(-2), module._sign(0), module._sign(2)] == [-1, 0, 1]


def test_the_magma_vent_on_its_back_is_where_its_rings_leave_from() -> None:
    assert muzzle_kinds(drawn(module._draw_back)) == ["ring"]


def test_its_back_has_no_vent_when_the_design_has_no_ring_muzzle(monkeypatch: Any) -> None:
    monkeypatch.setattr(module, "SALAMANDER_VENT", [])
    result = drawn(module._draw_back)
    assert result["muzzles"] == []
    # The fins' sockets, its reactors and the magma vein along its back stay.
    assert len(result["parts"].hull.geometry.positions) > 0
    assert len(result["parts"].vein.geometry.positions) > 0
