"""Unit tests of `src/game/view/shots/missile_exhaust.py`."""

import math
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon

from game.view.shots import missile_exhaust
from game.view.shots.missile_exhaust import (
    BACK,
    DEPTH,
    FLARE_LOOK,
    TRAIL_LOOK,
    create_missile_exhaust,
)


class Pool:
    """A pool that shows `count` meshes; the pools made are kept for the test to inspect."""

    made: list = []

    def __init__(self, create):
        self.create = create
        self.meshes = []
        Pool.made.append(self)

    def show(self, count):
        while len(self.meshes) < count:
            self.meshes.append(MagicMock(name="mesh"))
        return self.meshes[:count]

    def dispose(self):
        self.disposed = True


@pytest.fixture
def exhaust(monkeypatch):
    """The exhaust over Babylon stand-ins; `flares` and `trails` are the two pools, in order."""
    stub_babylon(monkeypatch, missile_exhaust)
    Pool.made = []
    monkeypatch.setattr(missile_exhaust, "NodePool", Pool)
    monkeypatch.setattr(
        missile_exhaust, "additive_template", lambda name, geo, scene: MagicMock(name=name)
    )
    handle = create_missile_exhaust(MagicMock())
    flares, trails = Pool.made
    return SimpleNamespace(handle=handle, flares=flares, trails=trails)


def test_p03_r03_the_flare_sits_at_the_nozzle_behind_the_missile(exhaust):
    shot = SimpleNamespace(x=0.0, y=100.0, heading=0.0, age=0.0, speed=200.0)
    exhaust.handle["sync"]([shot])
    # Heading 0 points to +Y: the nozzle lies `BACK` below the missile's centre.
    exhaust.flares.meshes[0].position.set.assert_called_with(0.0, 100.0 - BACK, DEPTH)


def test_p03_r03_the_trail_turns_with_the_heading_and_grows_from_the_launch(exhaust):
    shot = SimpleNamespace(x=5.0, y=5.0, heading=math.pi / 2, age=0.01, speed=100.0)
    exhaust.handle["sync"]([shot])
    trail = exhaust.trails.meshes[0]
    assert trail.rotation.z == pytest.approx(-math.pi / 2)
    trail.scaling.set.assert_called_with(TRAIL_LOOK.width, min(TRAIL_LOOK.length, 1.0), 1)


def test_p03_r03_the_flare_flickers_with_the_age_of_the_missile(exhaust):
    shot = SimpleNamespace(x=0.0, y=0.0, heading=0.0, age=0.5, speed=10.0)
    exhaust.handle["sync"]([shot])
    size = FLARE_LOOK.radius * (1 + FLARE_LOOK.flicker * math.sin(0.5 * FLARE_LOOK.flickerRate))
    exhaust.flares.meshes[0].scaling.set.assert_called_with(size, size, 1)


def test_p03_r03_a_missile_without_a_flare_gets_no_trail(exhaust):
    exhaust.handle["sync"]([None])
    exhaust.trails.meshes[0].position.set.assert_not_called()


def test_p03_r03_dispose_releases_both_pools(exhaust):
    exhaust.handle["dispose"]()
    assert exhaust.flares.disposed and exhaust.trails.disposed
