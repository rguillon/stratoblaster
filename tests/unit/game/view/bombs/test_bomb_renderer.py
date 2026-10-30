"""Unit tests of `src/game/view/bombs/bomb_renderer.py`."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon

from game.config.bomb_look import BOMB_LOOK
from game.view.bombs import bomb_renderer
from game.view.bombs.bomb_renderer import create_bomb_renderer, flash_strength, wave_reach


@pytest.mark.parametrize(
    ("t", "expected"),
    [(0, 0), (1, 1), (0.5, 0.75), (-1, 0), (2, 1)],
)
def test_p11_r05_the_shockwave_is_fast_then_slows(t, expected):
    assert wave_reach(t) == pytest.approx(expected)


def test_p11_r05_the_shockwave_covers_more_ground_early_than_late():
    early = wave_reach(0.25) - wave_reach(0)
    late = wave_reach(1) - wave_reach(0.75)
    assert early > late


def test_p11_r05_the_flash_is_full_at_once_then_gone_after_its_time():
    assert flash_strength(0) == pytest.approx(1)
    assert flash_strength(BOMB_LOOK.flash.seconds) == pytest.approx(0)
    assert flash_strength(BOMB_LOOK.flash.seconds * 10) == 0
    assert 0 < flash_strength(BOMB_LOOK.flash.seconds / 2) < 1


@pytest.fixture
def renderer(monkeypatch):
    """The bomb renderer over Babylon stand-ins, with its two templates recorded."""
    stub_babylon(monkeypatch, bomb_renderer)
    templates = []

    def make(name, geo, scene):
        templates.append(MagicMock(name=name))
        return templates[-1]

    monkeypatch.setattr(bomb_renderer, "additive_template", make)
    scene = MagicMock(name="scene")
    return create_bomb_renderer(scene), templates


def test_p11_r05_no_bomb_hides_the_wave_and_the_flash(renderer):
    handle, (ring, glow) = renderer[0], renderer[1]
    handle["sync"](SimpleNamespace(bomb=None))
    ring.setEnabled.assert_called_with(False)
    glow.setEnabled.assert_called_with(False)


def test_p11_r05_a_bomb_grows_its_wave_from_where_the_ship_was(renderer):
    handle, (ring, glow) = renderer[0], renderer[1]
    bomb = SimpleNamespace(x=30.0, y=40.0, age=0.0, seconds=2.0)
    handle["sync"](SimpleNamespace(bomb=bomb))
    ring.setEnabled.assert_called_with(True)
    ring.position.set.assert_called_with(30.0, 40.0, BOMB_LOOK.depth)
    # Just launched: the wave is at least one unit wide, and fully visible.
    ring.scaling.set.assert_called_with(1, 1, 1)
    assert ring.visibility == pytest.approx(1)
    glow.position.set.assert_called_with(30.0, 40.0, BOMB_LOOK.depth + 0.5)
    glow.scaling.set.assert_called_with(BOMB_LOOK.flash.radius, BOMB_LOOK.flash.radius, 1)
    assert glow.visibility == pytest.approx(1)


def test_p11_r05_the_wave_spreads_and_fades_as_the_bomb_ages(renderer):
    handle, (ring, glow) = renderer[0], renderer[1]
    seconds = 2.0
    bomb = SimpleNamespace(x=0.0, y=0.0, age=seconds / 2, seconds=seconds)
    handle["sync"](SimpleNamespace(bomb=bomb))
    t = 0.5
    radius = BOMB_LOOK.wave.radius * wave_reach(t)
    ring.scaling.set.assert_called_with(radius, radius, 1)
    assert ring.visibility == pytest.approx(1 - t * t)
    assert glow.visibility == pytest.approx(flash_strength(seconds / 2))


def test_p11_r05_the_flash_is_hidden_once_it_has_faded(renderer):
    handle, (ring, glow) = renderer[0], renderer[1]
    bomb = SimpleNamespace(x=0.0, y=0.0, age=BOMB_LOOK.flash.seconds * 2, seconds=10.0)
    handle["sync"](SimpleNamespace(bomb=bomb))
    glow.setEnabled.assert_called_with(False)
    ring.setEnabled.assert_called_with(True)


def test_p11_r05_dispose_releases_both_templates(renderer):
    handle, (ring, glow) = renderer[0], renderer[1]
    handle["dispose"]()
    ring.dispose.assert_called_once()
    glow.dispose.assert_called_once()
