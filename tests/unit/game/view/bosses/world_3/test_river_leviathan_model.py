# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_3/river_leviathan_model.py`: its crest and snout."""

from typing import Any

from helpers.bosses_worlds_probe import geometry_size, muzzle_kinds
from helpers.view_probes import drawn

from game.view.bosses.world_3 import river_leviathan_model as module


def test_fb_river_leviathan_03_the_crest_emitter_is_where_the_core_spirals_leave_from() -> None:
    assert muzzle_kinds(drawn(module.draw_crest)) == ["ring"]


def test_fb_river_leviathan_03_no_crest_is_drawn_when_the_design_has_no_ring_muzzle(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(module, "LEVIATHAN_CREST", [])
    assert geometry_size(drawn(module.draw_crest)) == 0


def test_the_snout_has_its_laser_lens_and_its_fang_guns() -> None:
    kinds = muzzle_kinds(drawn(module.draw_snout))
    assert kinds == ["laser"] + ["gun"] * len(module.LEVIATHAN_FANGS)


def test_the_snout_keeps_its_fang_guns_when_the_design_has_no_lens(monkeypatch: Any) -> None:
    monkeypatch.setattr(module, "LEVIATHAN_LENS", [])
    assert muzzle_kinds(drawn(module.draw_snout)) == ["gun"] * len(module.LEVIATHAN_FANGS)
