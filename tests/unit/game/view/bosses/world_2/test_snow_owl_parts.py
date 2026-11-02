# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_2/snow_owl_parts.py`: its sensor eye."""

from typing import Any

from helpers.bosses_worlds_probe import drawn_at, geometry_size, muzzle_kinds

from game.view.bosses.world_2 import snow_owl_parts as module


def test_sign_is_minus_one_zero_or_one() -> None:
    assert [module._sign(-1), module._sign(0), module._sign(3)] == [-1, 0, 1]


def test_mb_snow_owl_03_the_eye_fires_its_laser_from_its_lens() -> None:
    assert muzzle_kinds(drawn_at(module.eye, [0.0, 0.0, 20.0])) == ["laser"]


def test_mb_snow_owl_03_no_eye_is_drawn_when_the_design_has_no_lens(monkeypatch: Any) -> None:
    monkeypatch.setattr(module, "OWL_EYE_LENS", [])
    result = drawn_at(module.eye, [0.0, 0.0, 20.0])
    assert result["muzzles"] == []
    assert geometry_size(result) == 0
