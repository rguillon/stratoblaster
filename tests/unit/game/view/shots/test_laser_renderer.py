"""Unit tests of `src/game/view/shots/laser_renderer.py`."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from helpers.babylon_stub import stub_babylon

from game.config.shot_look import SHOT_LOOK
from game.view.shots import laser_renderer
from game.view.shots.laser_renderer import (
    LOOK,
    create_laser_renderer,
    place_bars,
    place_contacts,
    place_muzzle,
    place_sparks,
)


class Pool:
    """A pool that shows `count` meshes, recording the count it was asked for."""

    def __init__(self):
        self.shown = []
        self.meshes = []

    def show(self, count):
        self.shown.append(count)
        while len(self.meshes) < count:
            self.meshes.append(MagicMock(name="mesh"))
        return self.meshes[:count]

    def dispose(self):
        self.disposed = True


def seg(y0, y1, x=0.0, width=8.0, hit=False):
    return SimpleNamespace(x=x, y0=y0, y1=y1, width=width, hit=hit)


def test_p03_r02_one_bar_per_segment_of_the_beam_from_y0_to_y1():
    pool = Pool()
    place_bars(pool, [seg(0, 10, x=3.0, width=8.0), seg(10, 30, x=4.0, width=4.0)], 1.0)
    assert pool.shown == [2]
    first, second = pool.meshes
    first.position.set.assert_called_with(3.0, 0, 0)
    first.scaling.set.assert_called_with(8.0 * LOOK.glowWidth, 10, 1)
    second.position.set.assert_called_with(4.0, 10, 0)
    second.scaling.set.assert_called_with(4.0 * LOOK.glowWidth, 20, 1)


def test_p03_r02_the_bar_wobbles_with_the_flicker():
    pool = Pool()
    place_bars(pool, [seg(0, 10, width=8.0)], 1.5)
    pool.meshes[0].scaling.set.assert_called_with(8.0 * LOOK.glowWidth * 1.5, 10, 1)


def test_p03_r02_a_contact_glows_only_where_the_beam_stops_on_a_target():
    pool = Pool()
    place_contacts(pool, [seg(0, 10), seg(10, 20, hit=True, width=16.0)], 1.0)
    assert pool.shown == [1]
    mesh = pool.meshes[0]
    mesh.position.set.assert_called_with(0.0, 20, -0.5)
    radius = LOOK.contact.radius * (0.5 + 16.0 / 16)
    mesh.scaling.set.assert_called_with(radius, radius, 1)


def test_p03_r02_no_target_no_contact_glow():
    pool = Pool()
    place_contacts(pool, [seg(0, 10)], 1.0)
    assert pool.shown == [0]


def test_p03_r02_the_muzzle_glows_where_the_beam_leaves_the_ship(monkeypatch):
    monkeypatch.setattr(laser_renderer, "flicker", lambda t, a, hz: 0.0)
    pool = Pool()
    place_muzzle(pool, [seg(5, 30, x=2.0, width=6.0)], 1.0)
    mesh = pool.meshes[0]
    mesh.position.set.assert_called_with(2.0, 5, -0.6)
    r = LOOK.muzzle.radius * (LOOK.muzzle.baseScale + 6.0 / LOOK.muzzle.widthDivisor)
    mesh.scaling.set.assert_called_with(r, r * LOOK.muzzle.stretch, 1)


def test_p03_r02_no_beam_no_muzzle_glow():
    pool = Pool()
    place_muzzle(pool, [], 0.0)
    assert pool.shown == [0]


def test_p03_r02_particles_are_small_discs_along_the_beam():
    pool = Pool()
    place_sparks(pool, [SimpleNamespace(x=1.0, y=2.0, radius=0.5)])
    mesh = pool.meshes[0]
    mesh.position.set.assert_called_with(1.0, 2.0, -0.2)
    mesh.scaling.set.assert_called_with(0.5, 1.0, 1)


def test_p03_r02_the_laser_renderer_draws_a_frame_and_disposes(monkeypatch):
    stub_babylon(monkeypatch, laser_renderer)
    templates = []

    def make(name, geo, scene):
        templates.append(MagicMock(name=name))
        return templates[-1]

    monkeypatch.setattr(laser_renderer, "additive_template", make)
    monkeypatch.setattr(laser_renderer, "NodePool", lambda create: Pool())
    handle = create_laser_renderer(MagicMock())
    frame = SimpleNamespace(
        beam=[seg(0, 40, hit=True)],
        dt_seconds=0.02,
    )
    handle["sync"](frame)
    assert len(templates) == 4
    handle["dispose"]()
    assert all(t.dispose.called for t in templates)
    assert SHOT_LOOK.laser is LOOK
