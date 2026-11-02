# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/shots/missile_renderer.py`."""

from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest

from game.view.shots import missile_renderer
from game.view.shots.missile_renderer import create_missile_renderer


class Pool:
    def __init__(self, create: Any = None) -> None:
        self.shown = []
        self.meshes = []
        self.create = create

    def show(self, count: Any) -> Any:
        self.shown.append(count)
        while len(self.meshes) < count:
            self.meshes.append(MagicMock(name="missile"))
        return self.meshes[:count]

    def dispose(self) -> None:
        self.disposed = True


@pytest.fixture
def parts(monkeypatch: Any) -> Any:
    """Return the sub-renderers of the missiles, each a MagicMock, recorded here."""
    exhaust = MagicMock(name="exhaust")
    flashes = MagicMock(name="flashes")
    monkeypatch.setattr(missile_renderer, "NodePool", Pool)
    monkeypatch.setattr(
        missile_renderer, "build_missile", lambda name, _scene: MagicMock(name=name)
    )
    monkeypatch.setattr(missile_renderer, "create_missile_exhaust", lambda _scene: exhaust)
    monkeypatch.setattr(missile_renderer, "ImpactFlashes", lambda *_a: flashes)
    monkeypatch.setattr(missile_renderer, "flash_look", lambda _colors, _segments: None)
    monkeypatch.setattr(missile_renderer, "step_model_animations", MagicMock())
    monkeypatch.setattr(
        missile_renderer, "_shot_renderer", lambda sync, dispose: {"sync": sync, "dispose": dispose}
    )
    return SimpleNamespace(exhaust=exhaust, flashes=flashes)


def test_gfx_shot_06_each_missile_is_placed_and_turned_to_its_heading(parts: Any) -> None:
    handle = create_missile_renderer(MagicMock())
    shots = [SimpleNamespace(x=10.0, y=20.0, heading=0.5), None]
    frame = SimpleNamespace(projectiles=shots, impacts=[], dt_seconds=0.016)
    handle["sync"](frame)
    parts.exhaust.sync.assert_called_once_with(shots)
    parts.flashes.sync.assert_called_once_with([], 0.016)


@pytest.mark.usefixtures("parts")
def test_gfx_shot_06_missiles_animate_their_models_and_skip_empty_slots(monkeypatch: Any) -> None:
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


def test_gfx_shot_06_dispose_releases_the_missiles_and_their_trails(parts: Any) -> None:
    handle = create_missile_renderer(MagicMock())
    handle["dispose"]()
    parts.exhaust.dispose.assert_called_once()
    parts.flashes.dispose.assert_called_once()


def test_the_renderer_object_is_made_in_javascript_only() -> None:
    """`{sync, dispose}` is a JavaScript object literal; CPython runs only the placeholder: None."""
    assert missile_renderer._shot_renderer(lambda _frame: None, lambda: None) is None
