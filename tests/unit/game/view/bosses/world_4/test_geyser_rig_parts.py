# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_4/geyser_rig_parts.py`: its steam vents."""

from typing import Any

import pytest
from helpers.bosses_worlds_probe import drawn_at, muzzle_kinds

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.world_4 import geyser_rig_parts as module


def test_neon_or_reads_the_registered_neon_else_the_fallback(monkeypatch: Any) -> None:
    assert module._neon_or("geyser-rig", [1, 1, 1]) == BOSS_LOOK.neon["geyser-rig"]
    monkeypatch.setitem(BOSS_LOOK.neon, "geyser-rig", None)
    assert module._neon_or("geyser-rig", [1, 1, 1]) == [1, 1, 1]


def test_sign_is_minus_one_zero_or_one() -> None:
    assert [module._sign(-2), module._sign(0), module._sign(2)] == [-1, 0, 1]


def test_fb_geyser_rig_04_a_steam_vent_fires_its_rings_from_the_design_mouth() -> None:
    vent = drawn_at(module.steam_vent, [30.0, 0.0, 0.0])
    top = module.RIG_VENT_TOP[0]
    assert muzzle_kinds(vent) == ["ring"]
    assert vent["muzzles"][0][0] == pytest.approx(boss_point(top[0], top[1], top[2]))


def test_fb_geyser_rig_04_without_a_design_mouth_the_vent_tops_out_24_over_its_centre(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(module, "RIG_VENT_TOP", [])
    vent = drawn_at(module.steam_vent, [30.0, 0.0, 5.0])
    assert vent["muzzles"] == [[[30.0, 24.0, 5.0], "ring"]]
