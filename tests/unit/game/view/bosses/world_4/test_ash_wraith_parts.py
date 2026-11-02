# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_4/ash_wraith_parts.py`: its neon and eye cannon."""

from typing import Any

import pytest
from helpers.bosses_worlds_probe import (
    design_muzzles,
    drawn_at,
    muzzle_kinds,
    turret_drawings,
)
from helpers.view_probes import probe_builder

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.world_4 import ash_wraith_parts as module
from game.view.bosses.world_4.ash_wraith_model import build_ash_wraith


def test_sign_is_minus_one_zero_or_one() -> None:
    assert [module._sign(-2), module._sign(0), module._sign(2)] == [-1, 0, 1]


def test_neon_or_reads_the_registered_neon_else_the_fallback(monkeypatch: Any) -> None:
    assert module._neon_or("ash-wraith", [1, 1, 1]) == BOSS_LOOK.neon["ash-wraith"]
    monkeypatch.setitem(BOSS_LOOK.neon, "ash-wraith", None)
    assert module._neon_or("ash-wraith", [1, 1, 1]) == [1, 1, 1]


def test_mb_ash_wraith_04_the_eye_cannon_fires_its_laser_from_the_design_lens(
    monkeypatch: Any,
) -> None:
    capture = probe_builder(monkeypatch, build_ash_wraith)
    eye = turret_drawings(capture)["eye"]
    assert muzzle_kinds(eye) == ["laser"]
    assert eye["muzzles"][0][0] == pytest.approx(design_muzzles(capture.design, "eye", "laser")[0])


def test_mb_ash_wraith_04_without_a_lens_the_eye_fires_from_its_pivot(monkeypatch: Any) -> None:
    monkeypatch.setattr(module, "WRAITH_EYE_LENS", [])
    eye = drawn_at(module.eye_turret, [0.0, 6.0, 30.0])
    assert eye["muzzles"] == [[[0.0, 6.0, 30.0], "laser"]]
