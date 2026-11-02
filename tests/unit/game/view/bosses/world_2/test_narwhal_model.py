# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_2/narwhal_model.py`: its neon and deck gun."""

from typing import Any

from helpers.bosses_worlds_probe import fresh_copy, muzzle_kinds, turret_drawings
from helpers.view_probes import probe_builder

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.world_2 import narwhal_model as module


def test_the_narwhal_uses_its_registered_neon() -> None:
    assert BOSS_LOOK.neon.narwhal == module.N


def test_the_narwhal_falls_back_to_teal_when_the_look_has_no_neon_for_it(
    monkeypatch: Any,
) -> None:
    monkeypatch.delitem(BOSS_LOOK.neon, "narwhal")
    assert fresh_copy(module).N == [0.05, 0.95, 0.75]


def test_fb_narwhal_03_the_deck_gun_is_the_core_turret_with_two_barrels(
    monkeypatch: Any,
) -> None:
    capture = probe_builder(monkeypatch, module.build_narwhal)
    gun = turret_drawings(capture)["core"]
    assert muzzle_kinds(gun) == ["gun", "gun"]
    assert len(gun["parts"].hull.geometry.positions) > 0
