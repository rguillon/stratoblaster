# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_4/ember_herald_parts.py`: its neon and lances."""

from typing import Any

from helpers.bosses_worlds_probe import geometry_size, muzzle_kinds
from helpers.view_probes import drawn

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.world_4 import ember_herald_parts as module


def test_neon_or_reads_the_registered_neon_else_the_fallback(monkeypatch: Any) -> None:
    assert module._neon_or("ember-herald", [1, 1, 1]) == BOSS_LOOK.neon["ember-herald"]
    monkeypatch.setitem(BOSS_LOOK.neon, "ember-herald", None)
    assert module._neon_or("ember-herald", [1, 1, 1]) == [1, 1, 1]


def test_an_ember_lance_points_out_to_its_muzzle() -> None:
    result = drawn(lambda p: module.ember_lance(p, [[0, 40, 12]], [0.0, 12.0, -40.0]))
    assert len(result["muzzles"]) == 1
    assert len(result["parts"].hull.geometry.positions) > 0


def test_an_ember_lance_without_muzzles_is_not_drawn() -> None:
    result = drawn(lambda p: module.ember_lance(p, [], [0.0, 12.0, -40.0]))
    assert muzzle_kinds(result) == []
    assert geometry_size(result) == 0
