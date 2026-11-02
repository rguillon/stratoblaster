# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/phantom.py`."""

from typing import Any

import pytest
from helpers.enemy_steps import area, run, run_until
from helpers.fakes import FakeContext

from game.config.enemies_veteran import VETERAN_CONFIG
from game.sim.enemies.phantom import Phantom
from game.sim.enemy_kinds import ENEMY_KINDS

PHANTOM = next(kind for kind in ENEMY_KINDS if kind.id == "phantom")
SOLID = VETERAN_CONFIG.phantom.solidOpacity


def test_enm_phantom_12_a_faded_phantom_is_cloaked_and_shots_pass_through_it() -> None:
    (phantom,) = PHANTOM.spawn(area(width=400, height=600))
    phantom.opacity = 0.0
    assert phantom.cloaked is True
    assert phantom._hit_targets() == []


def test_enm_phantom_12_a_phantom_solid_enough_can_be_hit() -> None:
    (phantom,) = PHANTOM.spawn(area(width=400, height=600))
    phantom.opacity = SOLID + 0.01
    assert phantom.cloaked is False
    assert phantom._hit_targets() != []


def test_enm_phantom_09_a_phantom_runs_its_fade_cycle_with_its_opacity_in_range() -> None:
    ctx = FakeContext()
    (phantom,) = PHANTOM.spawn(area(width=400, height=600))
    run(phantom, ctx, 12.0)
    assert 0 <= phantom.opacity <= 1


def _draws(values: list[float]) -> Any:
    """Return random draws that give `values` in turn."""
    left = list(values)

    def draw() -> float:
        return left.pop(0)

    return draw


def test_enm_phantom_09_a_phantom_reappears_away_from_where_it_faded() -> None:
    ctx = FakeContext()
    # The middle of its places (draws of 0.5) is where it fades out; the next try is far enough.
    phantom = Phantom(200, 426, 426)
    run_until(phantom, ctx, lambda: phantom.state == "hidden", limit=5.0)
    ctx.random = _draws([0.5, 0.5, 0.0, 0.0])
    run_until(phantom, ctx, lambda: phantom.state == "fadeIn", limit=5.0)
    cfg = VETERAN_CONFIG.phantom
    assert (phantom.x, phantom.y) == pytest.approx((cfg.placeX[0] * 400, cfg.placeY[0] * 600))
