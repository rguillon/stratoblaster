# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_2/avalanche_arms.py`: the drills (MB-AVALANCHE-03)."""

from typing import Any

from helpers.bosses_worlds_probe import drawn_at, muzzle_kinds

from game.view.bosses.world_2 import avalanche_arms as module


def test_sign_is_minus_one_zero_or_one() -> None:
    assert [module._sign(-0.5), module._sign(0), module._sign(4)] == [-1, 0, 1]


def test_mb_avalanche_03_a_drill_carries_its_gun_on_its_outer_side() -> None:
    for x in [-24.0, 24.0]:
        assert muzzle_kinds(drawn_at(module.drill, [x, 0.0, 30.0])) == ["gun"]


def test_mb_avalanche_03_a_drill_has_no_barrel_when_the_design_gives_it_no_gun(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(module, "AVALANCHE_DRILL_GUN", [])
    result = drawn_at(module.drill, [24.0, 0.0, 30.0])
    assert result["muzzles"] == []
    # The rest of the drill (housing, bit, frost) is still drawn.
    assert len(result["parts"].hull.geometry.positions) > 0
