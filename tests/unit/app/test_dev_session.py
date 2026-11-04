# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/dev_session.py` (D-199): the dev viewer the menu shows, and the wheel."""

from types import SimpleNamespace
from typing import Any, ClassVar

import pytest
from helpers.dom import FakeDocument

from app import dev_session
from app.dev_session import DevSession


class FakePlayer:
    """A fake `DevAudioViewer`: what it was shown and whether it was dropped."""

    made: ClassVar[list["FakePlayer"]] = []

    def __init__(self, audio: Any, viewer: str, items: Any) -> None:
        self.audio = audio
        self.viewer = viewer
        self.items = items
        self.shown: list[tuple[int, bool]] = []
        self.holds: list[bool] = []
        self.frames: list[float] = []
        self.disposed = False
        self.status = "Playing: hit"
        FakePlayer.made.append(self)

    def show(self, index: int, toggle: bool) -> None:
        self.shown.append((index, toggle))

    def hold(self, held: bool) -> None:
        self.holds.append(held)

    def frame(self, dt: float) -> None:
        self.frames.append(dt)

    def dispose(self) -> None:
        self.disposed = True


class FakeViewer:
    made: ClassVar[list["FakeViewer"]] = []

    def __init__(
        self, _engine: Any, _game: Any, viewer: str, items: Any, _environment: bool
    ) -> None:
        self.viewer = viewer
        self.items = items
        self.shown: tuple[int, bool] | None = None
        self.scrubbed: list[float] = []
        self.zoomed: list[float] = []
        self.frames: list[float] = []
        self.disposed = False
        self.status = "1:00 / 4:00"
        self.scene: Any = None
        FakeViewer.made.append(self)

    def show(self, index: int, toggle: bool, mode: int = 0) -> None:
        self.shown = (index, toggle)
        self.mode = mode

    def turn(self, dx: float, dy: float) -> None:
        self.turned = (dx, dy)

    def scrub(self, delta: float) -> None:
        self.scrubbed.append(delta)

    def zoom(self, delta: float) -> None:
        self.zoomed.append(delta)

    def frame(self, dt: float) -> None:
        self.frames.append(dt)

    def break_part(self) -> None:
        self.broken = getattr(self, "broken", 0) + 1

    def dispose(self) -> None:
        self.disposed = True


@pytest.fixture(autouse=True)
def fake_viewer(monkeypatch: pytest.MonkeyPatch) -> None:
    FakeViewer.made = []
    FakePlayer.made = []
    monkeypatch.setattr(dev_session, "DevViewer", FakeViewer)
    monkeypatch.setattr(dev_session, "DevAudioViewer", FakePlayer)


def state(
    viewer: str | None, selection: int = 0, toggle: bool = True, mode: int = 0
) -> SimpleNamespace:
    return SimpleNamespace(
        dev_viewer=viewer, selection=selection, dev_close_up=toggle, dev_mode=mode
    )


def session(root: Any = None) -> DevSession:
    catalog = {
        "ships": ["a", "b"],
        "levels": ["1-1"],
        "bosses": ["warden"],
        "sounds": ["hit"],
        "music": ["menu"],
    }
    return DevSession("engine", "game", catalog, True, root, "audio")


def test_dev_menu_21_the_viewer_is_shown_the_view_the_menu_picked() -> None:
    s = session()
    s.sync(state("ships", 0, mode=2))
    assert FakeViewer.made[0].mode == 2


def test_d199_the_viewer_opens_follows_the_menu_and_closes() -> None:
    """DEV-MENU-02."""
    s = session()
    assert not s.active
    s.sync(state("ships", 1, toggle=False))
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


def test_d208_the_wheel_zooms_the_model_viewers() -> None:
    """DEV-MENU-11."""
    s = session()
    s.wheel(100)
    s.sync(state("ships"))
    s.wheel(-120)
    assert FakeViewer.made[0].zoomed == [-120]
    assert FakeViewer.made[0].scrubbed == []


def test_d199_the_wheel_scrubs_the_levels_viewer() -> None:
    s = session()
    s.sync(state("levels"))
    s.wheel(120)
    assert FakeViewer.made[0].scrubbed == [120]
    assert FakeViewer.made[0].zoomed == []


def test_d199_each_frame_moves_the_viewer_and_writes_its_status_line() -> None:
    """DEV-MENU-05."""
    doc = FakeDocument()
    root = doc.createElement("div")
    line = doc.createElement("div")
    line.className = "dev-status"
    root.append(line)
    s = session(root)
    s.frame(0.1)
    s.sync(state("levels"))
    s.frame(0.1)
    assert FakeViewer.made[0].frames == [0.1]
    assert line.textContent == "1:00 / 4:00"


def test_d199_the_viewer_is_drawn_once_its_scene_is_built() -> None:
    s = session()
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
    """DEV-MENU-10."""
    s = session()
    s.turn(3, 4)
    s.sync(state("ships"))
    s.turn(5, -2)
    assert FakeViewer.made[0].turned == (5, -2)


class FakeTarget:
    """An event target: its listeners by event type."""

    def __init__(self) -> None:
        self.listeners: dict[str, list[Any]] = {}

    def addEventListener(self, kind: str, listener: Any) -> None:
        self.listeners.setdefault(kind, []).append(listener)

    def removeEventListener(self, kind: str, listener: Any) -> None:
        self.listeners[kind].remove(listener)

    def press(self, code: str) -> SimpleNamespace:
        stopped: list[bool] = []
        event = {"type": "keydown"}
        key = type("Key", (), {"code": code, "__getitem__": lambda _s, k: event[k]})()
        key.preventDefault = lambda: stopped.append(True)
        for listener in self.listeners.get("keydown", []):
            listener(key)
        return SimpleNamespace(stopped=bool(stopped))


def test_k_breaks_a_part_in_the_bosses_viewer_only() -> None:
    """DEV-MENU-14."""
    target = FakeTarget()
    s = session()
    s.listen(target)
    s.sync(state("bosses"))
    assert target.press("KeyK").stopped
    assert FakeViewer.made[0].broken == 1
    assert not target.press("KeyJ").stopped
    s.sync(state("ships"))
    assert not target.press("KeyK").stopped
    assert not hasattr(FakeViewer.made[1], "broken")


def test_the_keys_are_no_longer_heard_once_disposed() -> None:
    target = FakeTarget()
    s = session()
    s.listen(target)
    s.dispose()
    assert target.listeners == {"keydown": [], "keyup": []}
    session().listen(None)


def test_dev_menu_14_k_is_used_on_its_release_without_breaking_another_part() -> None:
    s = session()
    s.sync(state("bosses"))
    assert s.key("KeyK", False) is True
    assert not hasattr(FakeViewer.made[0], "broken")
    assert s.key("KeyK", True) is True
    assert FakeViewer.made[0].broken == 1


class StatusLine:
    """The overlay's status line: each text written into it."""

    def __init__(self) -> None:
        self._text = ""
        self.writes: list[str] = []

    @property
    def textContent(self) -> str:
        return self._text

    @textContent.setter
    def textContent(self, value: str) -> None:
        self._text = value
        self.writes.append(value)


def overlay(line: StatusLine | None) -> SimpleNamespace:
    """Return the overlay root, whose `.dev-status` line is `line` (None: it has none)."""
    return SimpleNamespace(
        querySelector=lambda selector: line if selector == ".dev-status" else None
    )


def test_d199_the_status_line_is_written_only_when_it_changes() -> None:
    """Also DEV-MENU-05: without a status line in the overlay, nothing is written."""
    line = StatusLine()
    s = session(overlay(line))
    s.sync(state("levels"))
    s.frame(0.1)
    s.frame(0.1)
    assert line.writes == ["1:00 / 4:00"]
    FakeViewer.made[0].status = "2:00 / 4:00"
    s.frame(0.1)
    assert line.writes == ["1:00 / 4:00", "2:00 / 4:00"]
    lineless = session(overlay(None))
    lineless.sync(state("levels"))
    lineless.frame(0.1)
    assert FakeViewer.made[1].frames == [0.1]


# DEV-MENU-19, DEV-MENU-20: the sounds and music viewers play, they draw nothing.


def test_dev_menu_19_an_audio_viewer_opens_follows_the_menu_and_closes() -> None:
    s = session()
    s.sync(state("sounds", 0, toggle=True))
    player = FakePlayer.made[0]
    assert (player.audio, player.viewer, player.items) == ("audio", "sounds", ["hit"])
    assert not s.active
    assert not s.render()
    s.sync(state("sounds", 0, toggle=False))
    assert player.shown == [(0, True), (0, False)]
    assert len(FakePlayer.made) == 1
    s.sync(state("music"))
    assert player.disposed
    assert FakePlayer.made[1].viewer == "music"
    s.sync(state(None))
    assert FakePlayer.made[1].disposed
    assert s.player is None


def test_dev_menu_19_an_audio_viewer_replaces_a_scene_viewer_and_the_other_way_round() -> None:
    s = session()
    s.sync(state("ships"))
    s.sync(state("sounds"))
    assert FakeViewer.made[0].disposed
    assert s.viewer is None
    s.sync(state("ships"))
    assert FakePlayer.made[0].disposed
    assert s.player is None
    assert FakeViewer.made[1].viewer == "ships"
    s.sync(state("sounds"))
    s.dispose()
    assert FakePlayer.made[1].disposed


def test_dev_menu_19_an_audio_viewer_writes_its_status_each_frame() -> None:
    doc = FakeDocument()
    root = doc.createElement("div")
    line = doc.createElement("div")
    line.className = "dev-status"
    root.append(line)
    s = session(root)
    s.hold(True)
    s.sync(state("sounds"))
    s.frame(0.1)
    assert line.textContent == "Playing: hit"
    assert FakePlayer.made[0].frames == [0.1]
    s.hold(True)
    s.hold(False)
    assert FakePlayer.made[0].holds == [True, False]
    s.wheel(10)
    s.turn(1, 1)
    assert not s.key("KeyK", True)


def test_dev_menu_19_without_a_status_root_the_status_is_not_written() -> None:
    s = session()
    s.sync(state("sounds"))
    s.frame(0.1)
    assert FakePlayer.made[0].shown == [(0, True)]
