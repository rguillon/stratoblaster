# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_3/dam_breaker_model.py`: the pump house's stack."""

from typing import Any

import pytest
from helpers.bosses_worlds_probe import geometry_size, muzzle_kinds
from helpers.view_probes import drawn

from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.world_3 import dam_breaker_model as module


def test_the_stack_top_is_where_the_core_rings_leave_from() -> None:
    result = drawn(module.draw_stack)
    top = module.DAM_STACK[0]
    assert muzzle_kinds(result) == ["ring"]
    assert result["muzzles"][0][0] == pytest.approx(boss_point(top[0], top[1], top[2]))


def test_no_stack_is_drawn_when_the_design_has_no_ring_muzzle(monkeypatch: Any) -> None:
    monkeypatch.setattr(module, "DAM_STACK", [])
    assert geometry_size(drawn(module.draw_stack)) == 0
