"""Unit tests of `src/game/sim/enemies/orbiter.py`."""

from helpers.enemy_steps import area, run, run_until
from helpers.fakes import FakeContext

from core.entities.jointed_enemy import EnemyPartSpec
from game.sim.elite_kinds import ELITE_KINDS
from game.sim.enemies.orbiter import Orbiter

ORBITER = next(kind for kind in ELITE_KINDS if kind.id == "orbiter")


def test_p05_r20_an_orbiter_spawns_as_one_enemy_that_comes_in_to_its_stop_height() -> None:
    (orbiter,) = ORBITER.spawn(area(width=400, height=600))
    assert isinstance(orbiter, Orbiter)
    run_until(orbiter, FakeContext(), lambda: orbiter.state == "stay", limit=30.0)
    assert orbiter.state == "stay"


def test_p05_r20_an_orbiter_fires_its_ring_and_its_drones_while_it_stays() -> None:
    ctx = FakeContext()
    orbiter = Orbiter(200, 300, 300)
    run_until(orbiter, ctx, lambda: orbiter.state == "stay", limit=30.0)
    run(orbiter, ctx, 3.0)
    assert ctx.bullets


def test_p05_r20_an_orbiter_leaves_upward_or_downward_once_it_has_stayed() -> None:
    ctx = FakeContext()
    orbiter = Orbiter(200, 300, 300)
    run_until(orbiter, ctx, lambda: orbiter.state == "exit", limit=120.0)
    y = orbiter.y
    run(orbiter, ctx, 1.0)
    assert orbiter.y != y


def test_p05_r20_an_orbiter_builds_its_drones_as_part_specs_not_config_records() -> None:
    # In the browser a raw record leaves `joint` undefined, not None: the drones then hang on no
    # joint and the Orbiter cannot spawn.
    orbiter = Orbiter(200, 300, 300)
    assert len(orbiter.parts) == 3
    for part in orbiter.parts:
        assert isinstance(part.spec, EnemyPartSpec)
        assert part.spec.joint is None
        assert part.spec.orbits
