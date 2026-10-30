"""Unit tests of `src/game/view/shots/impact_flashes.py`."""

import math
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon

from game.view.shots import impact_flashes
from game.view.shots.impact_flashes import Flash, ImpactFlashes, flash_scale

LOOK = SimpleNamespace(segments=6, colors=[[1, 1, 1], [1, 0, 0]])


@pytest.fixture
def flashes(monkeypatch):
    stub_babylon(monkeypatch, impact_flashes)
    template = MagicMock(name="template")
    monkeypatch.setattr(impact_flashes, "additive_template", lambda *a: template)
    monkeypatch.setattr(impact_flashes, "NodePool", _Pool)
    return ImpactFlashes(MagicMock(), "blast", LOOK, 0.5, lambda impact: impact.r)


class _Pool:
    """A pool that gives back `count` plain mesh objects, enabled or not."""

    def __init__(self, create):
        self.create = create
        self.meshes = []

    def show(self, count):
        while len(self.meshes) < count:
            self.meshes.append(MagicMock(name="mesh"))
        return self.meshes[:count]

    def dispose(self):
        self.meshes.clear()


def test_p03_r01_the_flash_grows_then_shrinks():
    assert flash_scale(0, 1.0) == 0
    assert flash_scale(1.0, 1.0) == 0
    # Peaks a quarter of the way through (sin of pi times the root of the age).
    assert flash_scale(0.25, 1.0) == pytest.approx(1.0)
    assert flash_scale(0.5, 1.0) == pytest.approx(math.sin(math.pi * math.sqrt(0.5)))
    assert 0 < flash_scale(0.1, 1.0) < flash_scale(0.25, 1.0)
    assert flash_scale(0.9, 1.0) < flash_scale(0.5, 1.0)


def test_p03_r01_a_flash_is_a_position_radius_and_age():
    f = Flash(1.0, 2.0, 3.0, 0.5)
    assert (f.x, f.y, f.radius, f.age) == (1.0, 2.0, 3.0, 0.5)


def test_p03_r01_each_impact_starts_a_flash_at_its_point(flashes):
    impacts = [SimpleNamespace(x=5.0, y=6.0, r=2.0)]
    flashes.sync(impacts, 0.0)
    assert len(flashes.flashes) == 1
    f = flashes.flashes[0]
    assert (f.x, f.y, f.radius, f.age) == (5.0, 6.0, 2.0, 0)


def test_p03_r01_flashes_age_and_expire_after_their_duration(flashes):
    flashes.sync([SimpleNamespace(x=0, y=0, r=1)], 0.0)
    flashes.sync([], 0.25)
    assert len(flashes.flashes) == 1
    assert flashes.flashes[0].age == pytest.approx(0.25)
    flashes.sync([], 0.3)
    assert flashes.flashes == []


def test_p03_r01_a_new_flash_shows_at_a_minimum_size(flashes):
    flashes.sync([SimpleNamespace(x=0, y=0, r=10)], 0.0)
    mesh = flashes._pool.show(1)[0]
    size = 10 * max(0.3, flash_scale(0, 0.5))
    mesh.scaling.set.assert_called_with(size, size, 1)
    mesh.position.set.assert_called_with(0, 0, -1)


def test_p03_r01_dispose_releases_the_pool(flashes):
    flashes.sync([SimpleNamespace(x=0, y=0, r=1)], 0.0)
    flashes.dispose()
    assert flashes._pool.meshes == []
