# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_4/obsidian_golem_parts.py`: cannons and emitter."""

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
from game.view.bosses.world_4 import obsidian_golem_parts as module
from game.view.bosses.world_4.obsidian_golem_model import build_obsidian_golem


def test_neon_or_reads_the_registered_neon_else_the_fallback(monkeypatch: Any) -> None:
    assert module._neon_or("obsidian-golem", [1, 1, 1]) == BOSS_LOOK.neon["obsidian-golem"]
    monkeypatch.setitem(BOSS_LOOK.neon, "obsidian-golem", None)
    assert module._neon_or("obsidian-golem", [1, 1, 1]) == [1, 1, 1]


def test_sign_is_minus_one_zero_or_one() -> None:
    assert [module._sign(-2), module._sign(0), module._sign(2)] == [-1, 0, 1]


@pytest.mark.parametrize("piece", ["cannon-left", "cannon-right"])
def test_fb_obsidian_golem_04_a_shoulder_cannon_has_two_barrels_at_the_design_muzzles(
    monkeypatch: Any, piece: str
) -> None:
    capture = probe_builder(monkeypatch, build_obsidian_golem)
    cannon = turret_drawings(capture)[piece]
    assert muzzle_kinds(cannon) == ["gun", "gun"]
    assert [at for at, _kind in cannon["muzzles"]] == [
        pytest.approx(at) for at in design_muzzles(capture.design, piece, "gun")
    ]


def test_fb_obsidian_golem_05_the_chest_emitter_fires_its_laser_from_its_lens() -> None:
    assert muzzle_kinds(drawn_at(module.emitter, [0.0, 0.0, 40.0])) == ["laser"]


def test_fb_obsidian_golem_05_no_emitter_is_drawn_when_the_design_has_no_lens(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(module, "GOLEM_LENS", [])
    assert geometry_size(drawn_at(module.emitter, [0.0, 0.0, 40.0])) == 0
