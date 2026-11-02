# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_4/furnace_drake_model.py`: the furnace heart."""

from typing import Any

from helpers.bosses_worlds_probe import geometry_size, muzzle_kinds
from helpers.view_probes import drawn

from game.view.bosses.world_4 import furnace_drake_model as module


def test_the_furnace_heart_is_where_its_spirals_leave_from() -> None:
    assert muzzle_kinds(drawn(module._draw_heart)) == ["ring"]


def test_no_furnace_heart_is_drawn_when_the_design_has_no_ring_muzzle(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(module, "DRAKE_HEART", [])
    assert geometry_size(drawn(module._draw_heart)) == 0
