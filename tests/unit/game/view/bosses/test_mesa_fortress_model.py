# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/mesa_fortress_model.py`: the Mesa Fortress's fan cannon."""

import math
from typing import Any

import pytest
from helpers.bosses_top_turrets import check_turret, drawn_turrets

from game.view.bosses.mesa_fortress_model import FAN_AT, _fan_point, build_mesa_fortress


def test_fb_mesa_fortress_03_its_fan_cannon_fans_five_barrels_forward_from_its_brow(
    monkeypatch: Any,
) -> None:
    turrets = drawn_turrets(monkeypatch, build_mesa_fortress)
    assert sorted(turrets) == ["core"]
    check_turret(turrets["core"])
    muzzles = [m[0] for m in turrets["core"][1]["muzzles"]]
    assert len(muzzles) == 5
    # Fanned out: from one side to the other, the middle one straight ahead.
    xs = [m[0] for m in muzzles]
    assert xs == sorted(xs)
    assert xs[2] == pytest.approx(FAN_AT[0])


def test_a_fan_point_is_out_along_its_barrel_from_the_pivot() -> None:
    assert _fan_point(0, 10) == pytest.approx([FAN_AT[0], FAN_AT[1] + 2.6, FAN_AT[2] + 14])
    side = _fan_point(math.pi / 2, 10)
    assert side[0] == pytest.approx(FAN_AT[0] + 10)
