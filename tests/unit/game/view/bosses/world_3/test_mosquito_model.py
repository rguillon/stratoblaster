# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_3/mosquito_model.py`: its blood sac."""

from typing import Any

from helpers.bosses_worlds_probe import geometry_size, muzzle_kinds
from helpers.view_probes import drawn

from game.view.bosses.world_3 import mosquito_model as module


def test_mb_mosquito_02_the_blood_sac_is_where_its_last_stage_rings_leave_from() -> None:
    assert muzzle_kinds(drawn(module.draw_sac)) == ["ring"]


def test_mb_mosquito_02_no_sac_is_drawn_when_the_design_has_no_ring_muzzle(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(module, "MOSQUITO_SAC", [])
    assert geometry_size(drawn(module.draw_sac)) == 0
