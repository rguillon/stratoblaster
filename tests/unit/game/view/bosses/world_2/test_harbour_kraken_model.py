# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_2/harbour_kraken_model.py`: the crane pedestals."""

from typing import Any
from unittest.mock import MagicMock

import pytest

from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.world_2 import harbour_kraken_model as module
from game.view.enemies.enemy_shapes import SIDES


def _pedestals(monkeypatch: Any) -> list[Any]:
    """Draw the core with only its crane pedestals; return where they stand."""
    for name in ["draw_hull", "draw_bridge", "draw_bow", "draw_stern", "hatch_covers"]:
        monkeypatch.setattr(module, name, lambda _p: None)
    feet: list[Any] = []
    monkeypatch.setattr(module, "pedestal", lambda _p, at: feet.append(at))
    module.draw_core(MagicMock())
    return feet


def _on_deck(x: float, y: float) -> list[float]:
    at = boss_point(x, y)
    return [at[0], at[1] + module.DECK_Y, at[2]]


def test_fb_harbour_kraken_03_a_pedestal_stands_under_each_crane_shoulder(
    monkeypatch: Any,
) -> None:
    expected = [
        _on_deck(s * module.CRANE_REST[end][0][0], module.CRANE_REST[end][0][1])
        for end in ["fore", "aft"]
        for s in SIDES
    ]
    assert _pedestals(monkeypatch) == [pytest.approx(at) for at in expected]


def test_the_pedestals_stand_on_the_centre_line_when_the_cranes_have_no_rest(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(module, "CRANE_REST", {"fore": [], "aft": []})
    assert _pedestals(monkeypatch) == [pytest.approx(_on_deck(0, 0))] * 4
