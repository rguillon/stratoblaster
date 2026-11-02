# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_3/toucan_parts.py`: the beak's laser."""

from typing import Any

from helpers.bosses_worlds_probe import muzzle_kinds
from helpers.view_probes import drawn

from game.view.bosses.world_3 import toucan_parts as module


def test_the_beak_fires_its_laser_from_its_tip() -> None:
    assert muzzle_kinds(drawn(module.beak)) == ["laser"]


def test_the_beak_has_no_laser_when_the_design_has_no_beak_tip(monkeypatch: Any) -> None:
    monkeypatch.setattr(module, "TOUCAN_BEAK_TIP", [])
    result = drawn(module.beak)
    assert result["muzzles"] == []
    # The beak itself is still drawn.
    assert len(result["parts"].hull.geometry.positions) > 0
