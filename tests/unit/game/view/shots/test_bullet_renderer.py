"""Unit tests of `src/game/view/shots/bullet_renderer.py`."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon

from game.config.shot_look import SHOT_LOOK
from game.view.shots import bullet_renderer
from game.view.shots.bullet_renderer import create_bullet_renderer

LOOK = SHOT_LOOK.bullet
SPARK_LOOK = SHOT_LOOK.impact.bullet


class Pool:
    """A pool that shows `count` meshes; the pools made are kept for the test."""

    made: list = []

    def __init__(self, create):
        self.meshes = []
        self.disposed = False
        Pool.made.append(self)

    def show(self, count):
        while len(self.meshes) < count:
            self.meshes.append(MagicMock(name="mesh"))
        return self.meshes[:count]

    def dispose(self):
        self.disposed = True


@pytest.fixture
def renderer(monkeypatch):
    """The minigun renderer over Babylon stand-ins. `bullets` and `sparks` are its two pools."""
    stub_babylon(monkeypatch, bullet_renderer)
    Pool.made = []
    monkeypatch.setattr(bullet_renderer, "NodePool", Pool)
    monkeypatch.setattr(bullet_renderer, "additive_template", lambda *a: MagicMock())
    spark_source = MagicMock(name="sparks")
    spark_source.step.return_value = []
    monkeypatch.setattr(bullet_renderer, "SparkBursts", lambda look, rng: spark_source)
    handle = create_bullet_renderer(MagicMock())
    bullets, sparks = Pool.made
    return SimpleNamespace(handle=handle, bullets=bullets, sparks=sparks, source=spark_source)


def frame(projectiles=(), impacts=(), dt=0.0):
    return SimpleNamespace(projectiles=list(projectiles), impacts=list(impacts), dt_seconds=dt)


def test_p03_r01_a_bullet_sits_at_its_position_and_faces_its_heading(renderer):
    shot = SimpleNamespace(x=2.0, y=3.0, heading=0.4, age=1.0, speed=100.0)
    renderer.handle["sync"](frame([shot]))
    mesh = renderer.bullets.meshes[0]
    mesh.position.set.assert_called_with(2.0, 3.0, LOOK.depth)
    assert mesh.rotation.z == pytest.approx(-0.4)


def test_p03_r01_a_new_bullet_grows_out_of_the_muzzle_at_its_width(renderer):
    shot = SimpleNamespace(x=0.0, y=0.0, heading=0.0, age=0.0, speed=500.0)
    renderer.handle["sync"](frame([shot]))
    # Just fired: the streak is only as long as its width (no flicker at x = 0).
    renderer.bullets.meshes[0].scaling.set.assert_called_with(LOOK.width, LOOK.width, 1)


def test_p03_r01_an_old_bullet_keeps_the_length_of_the_look(renderer):
    shot = SimpleNamespace(x=0.0, y=0.0, heading=0.0, age=100.0, speed=500.0)
    renderer.handle["sync"](frame([shot]))
    length = renderer.bullets.meshes[0].scaling.set.call_args.args[1]
    assert length == pytest.approx(LOOK.length)


def test_p03_r01_each_impact_throws_sparks_where_it_hit(renderer):
    impacts = [SimpleNamespace(x=1.0, y=2.0), SimpleNamespace(x=3.0, y=4.0)]
    renderer.handle["sync"](frame(impacts=impacts, dt=0.016))
    assert renderer.source.emit.call_args_list == [((1.0, 2.0),), ((3.0, 4.0),)]
    renderer.source.step.assert_called_with(0.016)


def test_p03_r01_a_spark_is_a_thinner_streak_scaled_by_its_brightness(renderer):
    spark = SimpleNamespace(x=1.0, y=2.0, heading=0.3, length_=10.0, brightness=0.5)
    renderer.source.step.return_value = [spark]
    renderer.handle["sync"](frame())
    mesh = renderer.sparks.meshes[0]
    width = SPARK_LOOK.width * 0.5
    mesh.position.set.assert_called_with(1.0, 2.0, -1)
    assert mesh.rotation.z == pytest.approx(-0.3)
    mesh.scaling.set.assert_called_with(width, max(width, 10.0 / 2), 1)


def test_p03_r01_dispose_releases_the_pools_and_templates(renderer):
    renderer.handle["dispose"]()
    assert renderer.bullets.disposed and renderer.sparks.disposed
