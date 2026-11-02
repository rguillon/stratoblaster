# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_3/toucan_model.py`: its head, cheek guns and crest."""

from typing import Any

from helpers.bosses_worlds_probe import muzzle_kinds
from helpers.view_probes import drawn

from game.view.bosses.world_3 import toucan_model as module


def test_the_head_has_its_cheek_guns_and_its_crest_emitter() -> None:
    kinds = muzzle_kinds(drawn(module.draw_head))
    assert kinds == ["gun"] * len(module.TOUCAN_CHEEK_GUNS) + ["ring"]


def test_the_head_has_no_crest_emitter_when_the_design_has_no_ring_muzzle(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(module, "TOUCAN_CREST", [])
    assert muzzle_kinds(drawn(module.draw_head)) == ["gun"] * len(module.TOUCAN_CHEEK_GUNS)
