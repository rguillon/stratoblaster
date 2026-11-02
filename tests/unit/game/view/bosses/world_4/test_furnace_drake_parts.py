# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_4/furnace_drake_parts.py`: its neon and jaw."""

from typing import Any

from helpers.bosses_worlds_probe import drawn_at, muzzle_kinds

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.world_4 import furnace_drake_parts as module


def test_neon_or_reads_the_registered_neon_else_the_fallback(monkeypatch: Any) -> None:
    assert module._neon_or("furnace-drake", [1, 1, 1]) == BOSS_LOOK.neon["furnace-drake"]
    monkeypatch.setitem(BOSS_LOOK.neon, "furnace-drake", None)
    assert module._neon_or("furnace-drake", [1, 1, 1]) == [1, 1, 1]


def test_sign_is_minus_one_zero_or_one() -> None:
    assert [module._sign(-2), module._sign(0), module._sign(2)] == [-1, 0, 1]


def test_the_jaw_has_its_flame_nozzle_in_its_throat() -> None:
    assert muzzle_kinds(drawn_at(module.jaw, [0.0, 0.0, 30.0])) != []


def test_the_jaw_has_no_nozzle_when_the_design_has_no_maw(monkeypatch: Any) -> None:
    monkeypatch.setattr(module, "DRAKE_MAW", [])
    result = drawn_at(module.jaw, [0.0, 0.0, 30.0])
    assert result["muzzles"] == []
    # The neck and skull are still drawn.
    assert len(result["parts"].flesh.geometry.positions) > 0
