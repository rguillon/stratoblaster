"""Unit tests of `src/game/view/shots/missile_renderer.py`."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from game.view.shots import missile_renderer
from game.view.shots.missile_renderer import create_missile_renderer


class Pool:
    def __init__(self, create=None):
        self.shown = []
        self.meshes = []
        self.create = create

    def show(self, count):
        self.shown.append(count)
        while len(self.meshes) < count:
            self.meshes.append(MagicMock(name="missile"))
        return self.meshes[:count]

    def dispose(self):
        self.disposed = True


@pytest.fixture
def parts(monkeypatch):
    """The sub-renderers of the missiles, each a MagicMock, recorded here."""
    exhaust = MagicMock(name="exhaust")
    flashes = MagicMock(name="flashes")
    monkeypatch.setattr(missile_renderer, "NodePool", Pool)
    monkeypatch.setattr(missile_renderer, "build_missile", lambda name, scene: MagicMock(name=name))
    monkeypatch.setattr(missile_renderer, "create_missile_exhaust", lambda scene: exhaust)
    monkeypatch.setattr(missile_renderer, "ImpactFlashes", lambda *a: flashes)
    monkeypatch.setattr(missile_renderer, "flash_look", lambda colors, segments: None)
    monkeypatch.setattr(missile_renderer, "step_model_animations", MagicMock())
    monkeypatch.setattr(
        missile_renderer, "_shot_renderer", lambda sync, dispose: {"sync": sync, "dispose": dispose}
    )
    return SimpleNamespace(exhaust=exhaust, flashes=flashes)


def test_p03_r03_each_missile_is_placed_and_turned_to_its_heading(parts):
    handle = create_missile_renderer(MagicMock())
    shots = [SimpleNamespace(x=10.0, y=20.0, heading=0.5), None]
    frame = SimpleNamespace(projectiles=shots, impacts=[], dt_seconds=0.016)
    handle["sync"](frame)
    parts.exhaust.sync.assert_called_once_with(shots)
    parts.flashes.sync.assert_called_once_with([], 0.016)


def test_p03_r03_missiles_animate_their_models_and_skip_empty_slots(parts, monkeypatch):
    animate = MagicMock()
    monkeypatch.setattr(missile_renderer, "step_model_animations", animate)
    handle = create_missile_renderer(MagicMock())
    frame = SimpleNamespace(
        projectiles=[SimpleNamespace(x=1.0, y=2.0, heading=0.0), None],
        impacts=[],
        dt_seconds=0.5,
    )
    handle["sync"](frame)
    # Only the live missile is animated.
    assert animate.call_count == 1
    assert animate.call_args.args[1] == 0.5


def test_p03_r03_dispose_releases_the_missiles_and_their_trails(parts):
    handle = create_missile_renderer(MagicMock())
    handle["dispose"]()
    parts.exhaust.dispose.assert_called_once()
    parts.flashes.dispose.assert_called_once()
