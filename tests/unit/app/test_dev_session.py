"""Unit tests of `src/app/dev_session.py` (D-199): the dev viewer the menu shows, and the wheel."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.dom import FakeDocument

from app import dev_session
from app.dev_session import DevSession, wheel_steps
from config.dev_viewer import DEV_VIEWER_CONFIG as CFG


class FakeViewer:
    made: list["FakeViewer"] = []

    def __init__(self, engine: Any, game: Any, viewer: str, items: Any, environment: bool) -> None:
        self.viewer = viewer
        self.items = items
        self.shown: tuple[int, bool] | None = None
        self.scrubbed: list[float] = []
        self.frames: list[float] = []
        self.disposed = False
        self.status = "1:00 / 4:00"
        self.scene: Any = None
        FakeViewer.made.append(self)

    def show(self, index: int, toggle: bool) -> None:
        self.shown = (index, toggle)

    def turn(self, dx: float, dy: float) -> None:
        self.turned = (dx, dy)

    def scrub(self, delta: float) -> None:
        self.scrubbed.append(delta)

    def frame(self, dt: float) -> None:
        self.frames.append(dt)

    def dispose(self) -> None:
        self.disposed = True


@pytest.fixture(autouse=True)
def fake_viewer(monkeypatch: pytest.MonkeyPatch) -> None:
    FakeViewer.made = []
    monkeypatch.setattr(dev_session, "DevViewer", FakeViewer)


def state(viewer: str | None, selection: int = 0, toggle: bool = True) -> SimpleNamespace:
    return SimpleNamespace(dev_viewer=viewer, selection=selection, dev_close_up=toggle)


def session(root: Any = None) -> tuple[DevSession, list[str]]:
    commands: list[str] = []
    catalog = {"ships": ["a", "b"], "levels": ["1-1"]}
    return DevSession("engine", "game", catalog, True, root, commands.append), commands


def test_d199_the_wheel_counts_whole_steps_capped_either_way() -> None:
    assert wheel_steps(250, 100, 3) == 2
    assert wheel_steps(-99, 100, 3) == 0
    assert wheel_steps(-1000, 100, 3) == -3
    assert wheel_steps(500, 0, 3) == 0


def test_d199_the_viewer_opens_follows_the_menu_and_closes() -> None:
    s, _ = session()
    assert not s.active
    s.sync(state("ships", 1, False))
    viewer = FakeViewer.made[0]
    assert s.active
    assert (viewer.viewer, viewer.items, viewer.shown) == ("ships", ["a", "b"], (1, False))
    s.sync(state("ships", 0))
    assert len(FakeViewer.made) == 1
    s.sync(state("levels"))
    assert viewer.disposed
    assert FakeViewer.made[1].viewer == "levels"
    s.sync(state(None))
    assert FakeViewer.made[1].disposed
    assert not s.active


def test_d199_the_wheel_moves_through_the_models_as_the_arrows_do() -> None:
    s, commands = session()
    s.wheel(100)
    s.sync(state("ships"))
    s.wheel(CFG.wheel_step / 2)
    assert commands == []
    s.wheel(CFG.wheel_step / 2)
    assert commands == ["right"]
    s.wheel(-CFG.wheel_step * 10)
    assert commands == ["right"] + ["left"] * int(CFG.max_wheel_steps)


def test_d199_the_wheel_scrubs_the_levels_viewer() -> None:
    s, commands = session()
    s.sync(state("levels"))
    s.wheel(120)
    assert FakeViewer.made[0].scrubbed == [120]
    assert commands == []


def test_d199_each_frame_moves_the_viewer_and_writes_its_status_line() -> None:
    doc = FakeDocument()
    root = doc.createElement("div")
    line = doc.createElement("div")
    line.className = "dev-status"
    root.append(line)
    s, _ = session(root)
    s.frame(0.1)
    s.sync(state("levels"))
    s.frame(0.1)
    assert FakeViewer.made[0].frames == [0.1]
    assert line.textContent == "1:00 / 4:00"


def test_d199_the_viewer_is_drawn_once_its_scene_is_built() -> None:
    s, _ = session()
    assert not s.render()
    s.sync(state("ships"))
    assert not s.render()
    drawn: list[bool] = []
    FakeViewer.made[0].scene = SimpleNamespace(render=lambda: drawn.append(True))
    assert s.render()
    assert drawn == [True]
    s.frame(0)
    s.dispose()
    assert FakeViewer.made[0].disposed


def test_d199_a_drag_turns_the_viewer_s_model() -> None:
    s, _ = session()
    s.turn(3, 4)
    s.sync(state("ships"))
    s.turn(5, -2)
    assert FakeViewer.made[0].turned == (5, -2)
