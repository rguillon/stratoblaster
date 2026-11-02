# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_4/magma_salamander_parts.py`: neon and tail."""

from typing import Any

import pytest

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.world_4 import magma_salamander_parts as module


def test_neon_or_reads_the_registered_neon_else_the_fallback(monkeypatch: Any) -> None:
    assert module._neon_or("magma-salamander", [1, 1, 1]) == BOSS_LOOK.neon["magma-salamander"]
    monkeypatch.setitem(BOSS_LOOK.neon, "magma-salamander", None)
    assert module._neon_or("magma-salamander", [1, 1, 1]) == [1, 1, 1]


def test_sign_is_minus_one_zero_or_one() -> None:
    assert [module._sign(-2), module._sign(0), module._sign(2)] == [-1, 0, 1]


def test_the_tail_runs_from_its_root_through_its_knuckle_to_its_stinger() -> None:
    root, knuckle, tip = module.tail_points()
    tail = module.SALAMANDER_TAIL
    stinger = module.SALAMANDER_STINGER[0]
    assert root == boss_point(tail.root[0], tail.root[1], 4)
    assert knuckle == boss_point(tail.knuckle[0], tail.knuckle[1], 4)
    assert tip == pytest.approx(boss_point(stinger[0], stinger[1], stinger[2]))


def test_without_a_stinger_muzzle_the_tail_ends_at_its_knuckle(monkeypatch: Any) -> None:
    monkeypatch.setattr(module, "SALAMANDER_STINGER", [])
    _root, knuckle, tip = module.tail_points()
    assert tip == knuckle
