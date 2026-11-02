# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_4/cinder_crab_parts.py`: its sides and mortar."""

from typing import Any

from helpers.bosses_worlds_probe import geometry_size, muzzle_kinds
from helpers.view_probes import drawn

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.world_4 import cinder_crab_parts as module


def test_sign_is_minus_one_zero_or_one() -> None:
    assert [module._sign(-2), module._sign(0), module._sign(2)] == [-1, 0, 1]


def test_neon_or_reads_the_registered_neon_else_the_fallback(monkeypatch: Any) -> None:
    assert module._neon_or("cinder-crab", [1, 1, 1]) == BOSS_LOOK.neon["cinder-crab"]
    monkeypatch.setitem(BOSS_LOOK.neon, "cinder-crab", None)
    assert module._neon_or("cinder-crab", [1, 1, 1]) == [1, 1, 1]


def test_a_claw_on_the_centre_line_is_drawn_as_a_left_one() -> None:
    assert [module.side_at([-5, 0, 0]), module.side_at([0, 0, 0]), module.side_at([5, 0, 0])] == [
        -1,
        1,
        1,
    ]


def test_mb_cinder_crab_04_the_back_mortar_fires_from_its_mouth() -> None:
    assert muzzle_kinds(drawn(lambda p: module.mortar(p, [0.0, 0.0, -10.0], 8.0))) == ["gun"]


def test_mb_cinder_crab_04_no_mortar_is_drawn_when_the_design_has_none(monkeypatch: Any) -> None:
    monkeypatch.setattr(module, "CRAB_MORTAR", [])
    assert geometry_size(drawn(lambda p: module.mortar(p, [0.0, 0.0, -10.0], 8.0))) == 0
