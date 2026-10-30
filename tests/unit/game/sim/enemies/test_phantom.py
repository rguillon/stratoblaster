"""Unit tests of `src/game/sim/enemies/phantom.py`."""

from helpers.enemy_steps import area, run
from helpers.fakes import FakeContext

from game.config.enemies_veteran import VETERAN_CONFIG
from game.sim.enemy_kinds import ENEMY_KINDS

PHANTOM = next(kind for kind in ENEMY_KINDS if kind.id == "phantom")
SOLID = VETERAN_CONFIG.phantom.solidOpacity


def test_p05_r17_a_phantom_is_cloaked_below_its_solid_opacity_and_shots_pass_through_it() -> None:
    (phantom,) = PHANTOM.spawn(area(width=400, height=600))
    phantom.opacity = 0.0
    assert phantom.cloaked is True
    assert phantom._hit_targets() == []


def test_p05_r17_a_phantom_solid_enough_can_be_hit() -> None:
    (phantom,) = PHANTOM.spawn(area(width=400, height=600))
    phantom.opacity = SOLID + 0.01
    assert phantom.cloaked is False
    assert phantom._hit_targets() != []


def test_p05_r17_a_phantom_runs_its_fade_cycle_with_its_opacity_in_range() -> None:
    ctx = FakeContext()
    (phantom,) = PHANTOM.spawn(area(width=400, height=600))
    run(phantom, ctx, 12.0)
    assert 0 <= phantom.opacity <= 1
