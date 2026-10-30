"""Unit tests of `src/game/sim/enemies/gnat.py`."""

import pytest
from helpers.enemy_steps import run
from helpers.fakes import FakeContext

from core.systems.enemy_motion import Path
from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.gnat import Gnat

CFG = ENEMY_CONFIG.gnat


def _path() -> Path:
    return Path([[100, 0], [100, 200], [100, 400]])


def test_p05_r01_a_gnat_waits_out_its_delay_before_it_moves() -> None:
    gnat = Gnat(_path(), 1.0)
    run(gnat, FakeContext(), 0.5)
    assert gnat.y == 0


def test_p05_r01_a_gnat_follows_its_path_at_its_speed_after_the_delay() -> None:
    gnat = Gnat(_path(), 0.0)
    run(gnat, FakeContext(), 1.0)
    assert gnat.y == pytest.approx(CFG.speed, rel=1e-2)
    assert gnat.x == pytest.approx(100)


def test_p05_r01_a_gnat_is_done_once_it_reaches_the_end_of_its_path() -> None:
    gnat = Gnat(_path(), 0.0)
    run(gnat, FakeContext(), 60.0)
    assert gnat.gone is True


def test_p05_r01_a_gnat_does_not_fire() -> None:
    ctx = FakeContext()
    run(Gnat(_path(), 0.0), ctx, 3.0)
    assert ctx.bullets == [] and ctx.missiles == []
