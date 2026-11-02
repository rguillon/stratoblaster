# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_4/foundry_ark_parts.py`: rail cannons, crucibles."""

from typing import Any

import pytest
from helpers.bosses_worlds_probe import (
    design_muzzles,
    drawn_at,
    geometry_size,
    muzzle_kinds,
    turret_drawings,
)
from helpers.view_probes import probe_builder, recorder

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.world_4 import foundry_ark_parts as module
from game.view.bosses.world_4.foundry_ark_model import build_foundry_ark


def test_neon_or_reads_the_registered_neon_else_the_fallback(monkeypatch: Any) -> None:
    assert module._neon_or("foundry-ark", [1, 1, 1]) == BOSS_LOOK.neon["foundry-ark"]
    monkeypatch.setitem(BOSS_LOOK.neon, "foundry-ark", None)
    assert module._neon_or("foundry-ark", [1, 1, 1]) == [1, 1, 1]


@pytest.mark.parametrize("piece", ["rail-left", "rail-right"])
def test_fb_foundry_ark_03_a_rail_cannon_fires_its_laser_from_the_design_muzzle(
    monkeypatch: Any, piece: str
) -> None:
    capture = probe_builder(monkeypatch, build_foundry_ark)
    cannon = turret_drawings(capture)[piece]
    assert muzzle_kinds(cannon) == ["laser"]
    assert cannon["muzzles"][0][0] == pytest.approx(
        design_muzzles(capture.design, piece, "laser")[0]
    )
    # Its coils glow as the charge builds.
    assert len(cannon["parts"].charge.geometry.positions) > 0


def test_fb_foundry_ark_03_no_rail_cannon_is_drawn_when_the_design_has_no_laser(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(module, "ARK_RAIL", [])
    for x in [-40.0, 40.0]:
        assert geometry_size(drawn_at(module.rail_cannon, [x, 0.0, 10.0])) == 0


def _lip_x(x: float) -> float:
    """Draw a crucible at `x`; return the x of its pouring lip (the first box on its hull)."""
    parts, log = recorder()
    module.crucible(parts, [x, 0.0, 0.0])
    boxes = [args for path, args, _kw in log if path == "hull.box"]
    at: float = boxes[0][2].at[0]
    return at


def test_a_crucible_pours_on_its_inboard_side() -> None:
    assert _lip_x(-20.0) == pytest.approx(-7.5)
    assert _lip_x(20.0) == pytest.approx(7.5)


def test_a_crucible_on_the_centre_line_has_its_lip_over_its_centre() -> None:
    assert _lip_x(0.0) == 0.0
