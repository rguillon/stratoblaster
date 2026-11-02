# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_4/ember_herald_model.py`: the lances' muzzles."""

from typing import Any

from game.config.record import record
from game.view.bosses.world_4 import ember_herald_model as module


def test_a_lance_takes_its_muzzles_from_the_design() -> None:
    assert module._gun_muzzles("lance-1") == module.EMBER_HERALD.guns["lance-1"].gun


def test_a_piece_without_guns_has_no_muzzles(monkeypatch: Any) -> None:
    monkeypatch.setitem(module.EMBER_HERALD.guns, "lance-unarmed", record({"turret": [0, 0]}))
    monkeypatch.setitem(module.EMBER_HERALD.guns, "lance-missing", None)
    assert module._gun_muzzles("lance-unarmed") == []
    assert module._gun_muzzles("lance-missing") == []
