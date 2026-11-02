# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_2/glacier_colossus_model.py`: its heat stack."""

from typing import Any

import pytest
from helpers.bosses_worlds_probe import geometry_size, muzzle_kinds
from helpers.view_probes import drawn

from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.world_2 import glacier_colossus_model as module


def test_the_heat_stack_is_where_the_core_rings_leave_from() -> None:
    result = drawn(module.draw_stack)
    ring = module.COLOSSUS_STACK[0]
    assert muzzle_kinds(result) == ["ring"]
    assert result["muzzles"][0][0] == pytest.approx(boss_point(ring[0], ring[1], ring[2]))


def test_no_heat_stack_is_drawn_when_the_design_has_no_ring_muzzle(monkeypatch: Any) -> None:
    monkeypatch.setattr(module, "COLOSSUS_STACK", [])
    result = drawn(module.draw_stack)
    assert result["muzzles"] == []
    assert geometry_size(result) == 0
