# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_4/caldera_throne_parts.py`: its magma cannons."""

import math
from typing import Any

import pytest
from helpers.bosses_worlds_probe import design_muzzles, muzzle_kinds, turret_drawings
from helpers.view_probes import probe_builder

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.world_4 import caldera_throne_parts as module
from game.view.bosses.world_4.caldera_throne_model import build_caldera_throne


def test_neon_or_reads_the_registered_neon_else_the_fallback(monkeypatch: Any) -> None:
    assert module._neon_or("caldera-throne", [1, 1, 1]) == BOSS_LOOK.neon["caldera-throne"]
    monkeypatch.setitem(BOSS_LOOK.neon, "caldera-throne", None)
    assert module._neon_or("caldera-throne", [1, 1, 1]) == [1, 1, 1]


def test_a_barrel_placement_lies_along_z() -> None:
    place = module._along_z(1, 2, 3)
    assert place.at == [1, 2, 3]
    assert (place.yaw, place.pitch, place.roll) == (0, math.pi / 2, 0)


@pytest.mark.parametrize("piece", ["magma-left", "magma-right"])
def test_fb_caldera_throne_03_a_magma_cannon_fires_its_laser_from_the_design_muzzle(
    monkeypatch: Any, piece: str
) -> None:
    capture = probe_builder(monkeypatch, build_caldera_throne)
    cannon = turret_drawings(capture)[piece]
    assert muzzle_kinds(cannon) == ["laser"]
    assert cannon["muzzles"][0][0] == pytest.approx(
        design_muzzles(capture.design, piece, "laser")[0]
    )
    # Its lens glows as the laser charges.
    assert len(cannon["parts"].charge.geometry.positions) > 0
