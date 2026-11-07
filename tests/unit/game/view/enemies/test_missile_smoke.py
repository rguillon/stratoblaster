# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/missile_smoke.py`: the missiles' smoke (GFX-SHOT-15)."""

import math
from types import SimpleNamespace
from typing import Any

import pytest

from game.view.enemies.missile_smoke import LOOK, MissileSmoke, tail_of

SMOKE = LOOK.smoke


def _missile(**fields: Any) -> SimpleNamespace:
    state = {"x": 50.0, "y": 60.0, "heading": 0.0, "radius": LOOK.baseRadius, "height": 0.0}
    state.update(fields)
    return SimpleNamespace(**state)


def test_gfx_shot_15_a_missile_s_tail_is_behind_it_along_its_heading() -> None:
    back = LOOK.length / 2
    assert tail_of(_missile()) == pytest.approx([50, 60 - back, -0.5])
    # WPN-09: pointing straight up out of its silo, its tail is under it, nearer the plane.
    up = tail_of(_missile(height=10.0, pitch=math.pi / 2))
    assert up == pytest.approx([50, 60, -0.5 - 10 + back])


def test_gfx_shot_15_puffs_are_left_behind_each_missile_and_fade_out() -> None:
    smoke = MissileSmoke()
    missiles = [_missile(), _missile(x=10.0)]
    born = smoke.step(missiles, SMOKE.every)
    assert len(born) == 2
    # Each fades in from nothing, then out.
    assert all(spot.a == 0 for spot in born)
    spots = smoke.step([], 0.02)
    assert len(spots) == 2
    assert all(0 < spot.a <= SMOKE.alpha for spot in spots)
    assert all(spot.r == spot.g == spot.b for spot in spots)
    # Once their life is over, the puffs are gone.
    assert smoke.step([], SMOKE.life[1] + 0.01) == []


def test_gfx_shot_15_the_puffs_are_capped() -> None:
    smoke = MissileSmoke()
    many = [_missile(x=float(k)) for k in range(SMOKE.most + 5)]
    assert len(smoke.step(many, SMOKE.every)) == SMOKE.most
