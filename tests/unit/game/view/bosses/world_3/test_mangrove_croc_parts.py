# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_3/mangrove_croc_parts.py`: its jaw cannon."""

from typing import Any

from helpers.bosses_worlds_probe import drawn_at, geometry_size, muzzle_kinds

from game.view.bosses.world_3 import mangrove_croc_parts as module


def test_mb_mangrove_croc_03_the_jaw_cannon_fires_between_the_jaws() -> None:
    assert muzzle_kinds(drawn_at(module.jaw_cannon, [0.0, 0.0, 30.0])) == ["gun"]


def test_mb_mangrove_croc_03_no_jaw_cannon_is_drawn_when_the_design_has_none(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(module, "CROC_JAW_CANNON", [])
    assert geometry_size(drawn_at(module.jaw_cannon, [0.0, 0.0, 30.0])) == 0
