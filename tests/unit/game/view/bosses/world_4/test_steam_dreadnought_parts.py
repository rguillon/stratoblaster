# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_4/steam_dreadnought_parts.py`: stacks and turrets."""

from typing import Any

import pytest
from helpers.bosses_worlds_probe import (
    design_muzzles,
    drawn_at,
    geometry_size,
    muzzle_kinds,
    turret_drawings,
)
from helpers.view_probes import probe_builder

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.world_4 import steam_dreadnought_parts as module
from game.view.bosses.world_4.steam_dreadnought_model import build_steam_dreadnought


def test_neon_or_reads_the_registered_neon_else_the_fallback(monkeypatch: Any) -> None:
    assert module._neon_or("steam-dreadnought", [1, 1, 1]) == BOSS_LOOK.neon["steam-dreadnought"]
    monkeypatch.setitem(BOSS_LOOK.neon, "steam-dreadnought", None)
    assert module._neon_or("steam-dreadnought", [1, 1, 1]) == [1, 1, 1]


def test_sign_is_minus_one_zero_or_one() -> None:
    assert [module._sign(-2), module._sign(0), module._sign(2)] == [-1, 0, 1]


def test_a_part_on_the_centre_line_is_drawn_as_a_left_one() -> None:
    assert [module.side_at([-5, 0, 0]), module.side_at([0, 0, 0]), module.side_at([5, 0, 0])] == [
        -1,
        1,
        1,
    ]


def test_fb_steam_dreadnought_03_no_smokestack_is_drawn_when_the_design_has_no_ring_muzzle(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(module, "DREAD_STACK", [])
    for x in [-20.0, 20.0]:
        assert geometry_size(drawn_at(module.smokestack, [x, 0.0, 0.0])) == 0


@pytest.mark.parametrize("piece", ["turret-left", "turret-right"])
def test_fb_steam_dreadnought_04_a_broadside_turret_has_twin_barrels_at_the_design_muzzles(
    monkeypatch: Any, piece: str
) -> None:
    capture = probe_builder(monkeypatch, build_steam_dreadnought)
    turret = turret_drawings(capture)[piece]
    assert muzzle_kinds(turret) == ["gun", "gun"]
    assert [at for at, _kind in turret["muzzles"]] == [
        pytest.approx(at) for at in design_muzzles(capture.design, piece, "gun")
    ]
