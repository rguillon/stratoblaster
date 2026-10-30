"""Unit tests of `src/game/sim/enemies/splitter.py`."""

import math

import pytest
from helpers.enemy_steps import run
from helpers.fakes import FakeContext

from core.systems.enemy_motion import Path
from game.sim.enemies.hornet import Hornet
from game.sim.enemies.splitter import Splitter


def _path() -> Path:
    return Path([[200, 700], [200, 400], [200, 100]])


def test_p05_r10_a_splitter_follows_its_path_and_fires_while_on_the_playfield() -> None:
    ctx = FakeContext()
    splitter = Splitter(_path())
    run(splitter, ctx, 2.0)
    assert splitter.y < 700
    assert ctx.bullets


def test_p05_r10_a_destroyed_splitter_releases_three_pods_round_its_core() -> None:
    ctx = FakeContext()
    splitter = Splitter(_path())
    splitter.x, splitter.y = 200.0, 300.0
    splitter.on_destroyed(ctx)
    assert len(ctx.spawned) == 3
    assert all(isinstance(pod, Hornet) for pod in ctx.spawned)
    headings = sorted(pod.heading % (2 * math.pi) for pod in ctx.spawned)
    assert headings[1] - headings[0] == pytest.approx(2 * math.pi / 3, rel=1e-6)
