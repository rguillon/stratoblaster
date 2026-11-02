# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_2/avalanche_model.py`: the rock hopper."""

from typing import Any

import pytest
from helpers.bosses_worlds_probe import drawn_at, muzzle_kinds

from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.world_2 import avalanche_model as module


def test_mb_avalanche_03_the_hopper_fires_from_its_chute_lip() -> None:
    result = drawn_at(module.hopper, [0.0, 0.0, -20.0])
    chute = module.AVALANCHE_CHUTE[0]
    assert muzzle_kinds(result) == ["gun"]
    assert result["muzzles"][0][0] == pytest.approx(boss_point(chute[0], chute[1], chute[2]))


def test_mb_avalanche_03_the_hopper_has_no_chute_when_the_design_gives_it_none(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(module, "AVALANCHE_CHUTE", [])
    result = drawn_at(module.hopper, [0.0, 0.0, -20.0])
    assert result["muzzles"] == []
    # The chute's charge light goes with it; the bin and its rocks stay.
    assert result["parts"].charge.geometry.positions == []
    assert len(result["parts"].hull.geometry.positions) > 0
