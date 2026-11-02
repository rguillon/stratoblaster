# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_4/obsidian_golem_model.py`: its furnace stack."""

from typing import Any

from helpers.bosses_worlds_probe import geometry_size, muzzle_kinds
from helpers.view_probes import drawn

from game.view.bosses.world_4 import obsidian_golem_model as module


def test_the_furnace_stack_is_where_the_core_rings_leave_from() -> None:
    assert muzzle_kinds(drawn(module._draw_stack)) == ["ring"]


def test_no_furnace_stack_is_drawn_when_the_design_has_no_ring_muzzle(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(module, "GOLEM_STACK", [])
    assert geometry_size(drawn(module._draw_stack)) == 0
