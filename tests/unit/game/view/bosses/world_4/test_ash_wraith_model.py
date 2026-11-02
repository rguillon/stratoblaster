# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_4/ash_wraith_model.py`: the ash vent on its back."""

from typing import Any

from helpers.bosses_worlds_probe import geometry_size, muzzle_kinds
from helpers.view_probes import drawn

from game.view.bosses.world_4 import ash_wraith_model as module


def test_the_ash_vent_is_where_the_core_spirals_leave_from() -> None:
    assert muzzle_kinds(drawn(module._draw_vent)) == ["ring"]


def test_no_ash_vent_is_drawn_when_the_design_has_no_ring_muzzle(monkeypatch: Any) -> None:
    monkeypatch.setattr(module, "WRAITH_VENT", [])
    assert geometry_size(drawn(module._draw_vent)) == 0
