# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_3/canopy_spider_model.py`: the crown emitter."""

from typing import Any

from helpers.bosses_worlds_probe import muzzle_kinds
from helpers.view_probes import drawn

from game.view.bosses.world_3 import canopy_spider_model as module


def test_the_crown_emitter_is_where_the_core_spirals_leave_from() -> None:
    assert muzzle_kinds(drawn(module.draw_crown)) == ["ring"]


def test_only_the_hip_sockets_are_drawn_when_the_design_has_no_crown(monkeypatch: Any) -> None:
    monkeypatch.setattr(module, "SPIDER_CROWN", [])
    result = drawn(module.draw_crown)
    assert result["muzzles"] == []
    assert len(result["parts"].hull.geometry.positions) > 0
