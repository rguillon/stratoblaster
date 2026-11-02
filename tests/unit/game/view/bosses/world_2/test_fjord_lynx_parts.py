# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_2/fjord_lynx_parts.py`: its neon and turrets."""

from typing import Any
from unittest.mock import MagicMock

import pytest
from helpers.bosses_worlds_probe import fresh_copy, muzzle_kinds, turret_drawings
from helpers.view_probes import probe_builder

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.world_2 import fjord_lynx_parts as module
from game.view.bosses.world_2.fjord_lynx_model import build_fjord_lynx


def test_the_lynx_uses_its_registered_neon() -> None:
    assert BOSS_LOOK.neon["fjord-lynx"] == module.CYAN


def test_the_lynx_falls_back_to_cyan_when_the_look_has_no_neon_for_it(
    monkeypatch: Any,
) -> None:
    monkeypatch.setitem(BOSS_LOOK.neon, "fjord-lynx", None)
    assert fresh_copy(module).CYAN == [0.55, 0.95, 1.0]


def test_sign_is_minus_one_zero_or_one() -> None:
    assert [module._sign(-1), module._sign(0), module._sign(1)] == [-1, 0, 1]


def test_each_turret_of_the_lynx_has_its_barrels(monkeypatch: Any) -> None:
    capture = probe_builder(monkeypatch, build_fjord_lynx)
    turrets = turret_drawings(capture)
    assert muzzle_kinds(turrets["core"]) == ["gun"]
    assert muzzle_kinds(turrets["paw-left"]) == ["gun", "gun"]
    assert muzzle_kinds(turrets["paw-right"]) == ["gun", "gun"]


@pytest.mark.parametrize(("x", "hatch"), [(-20.0, 1), (20.0, -1)])
def test_a_paw_turret_puts_its_hatch_on_the_outer_side(
    monkeypatch: Any, x: float, hatch: int
) -> None:
    specs: list[Any] = []
    monkeypatch.setattr(module, "turret", lambda _p, _at, spec: specs.append(spec))
    module.paw_turret(MagicMock(), [x, 0.0, 10.0])
    assert specs[0].hatch == hatch
    assert specs[0].barrels == 2
