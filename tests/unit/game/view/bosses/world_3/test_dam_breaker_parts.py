# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_3/dam_breaker_parts.py`: the sluice cannons."""

from typing import Any

from helpers.bosses_worlds_probe import drawn_at, geometry_size, muzzle_kinds

from game.view.bosses.world_3 import dam_breaker_parts as module


def test_fb_dam_breaker_03_a_sluice_lets_its_sludge_out_of_its_lip() -> None:
    for x in [-30.0, 30.0]:
        assert muzzle_kinds(drawn_at(module.sluice, [x, 0.0, 10.0])) == ["gun"]


def test_fb_dam_breaker_03_no_sluice_is_drawn_when_the_design_has_no_spout(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(module, "DAM_SPOUT", [])
    for x in [-30.0, 30.0]:
        assert geometry_size(drawn_at(module.sluice, [x, 0.0, 10.0])) == 0
