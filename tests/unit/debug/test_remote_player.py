# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/debug/remote_player.py` (D-266: the AI player of `make serve-ai`)."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers import js_shims

from debug import play_scene as play_scene_module
from debug import remote_player
from debug.remote_player import (
    AI_PATH,
    AI_SECONDS,
    RemotePlayer,
    install_remote_player,
    post_json,
    remote_reading,
)


@pytest.fixture(autouse=True)
def js_twins(monkeypatch: pytest.MonkeyPatch) -> None:
    for module in (play_scene_module, remote_player):
        monkeypatch.setattr(module, "js_object", js_shims.js_object)
        monkeypatch.setattr(module, "js_set", js_shims.js_set)
    monkeypatch.setattr(remote_player, "play_scene", lambda run: {"of": run.phase})


class FakeControls:
    def __init__(self) -> None:
        self.keys: list[tuple[str, bool]] = []

    def key(self, code: str, down: bool) -> None:
        self.keys.append((code, down))


class FakeApp:
    """What the remote player reads of and sends to `RunningApp`."""

    def __init__(self, phase: str | None = "playing", paused: bool = False) -> None:
        self.paused = paused
        self.phase = phase
        self.controls = FakeControls()
        self.menu = SimpleNamespace(flow=SimpleNamespace(state=self))
        self.attempt = 2

    def game(self) -> Any:
        if self.phase is None:
            return None
        run = SimpleNamespace(
            phase=self.phase,
            result=SimpleNamespace(level_id="2-3"),
            track=SimpleNamespace(time=12.5, duration=300.0),
        )
        return SimpleNamespace(run=run)


class FakeServer:
    """`post`: keeps each question, to answer it later."""

    def __init__(self) -> None:
        self.asked: list[tuple[str, Any, Any]] = []

    def __call__(self, path: str, body: Any, on_reply: Any) -> None:
        self.asked.append((path, body, on_reply))

    def answer(self, keys: Any) -> None:
        self.asked.pop(0)[2](keys)


def test_d_266_the_reading_is_the_level_its_attempt_time_and_scene() -> None:
    assert remote_reading(FakeApp()) == {
        "level": "2-3",
        "attempt": 2,
        "time": 12.5,
        "duration": 300.0,
        "scene": {"of": "playing"},
    }
    assert remote_reading(FakeApp("clearing"))["scene"] == {"of": "clearing"}


def test_d_266_nothing_is_read_out_of_a_level_paused_or_over() -> None:
    assert remote_reading(FakeApp(None)) is None
    assert remote_reading(FakeApp(paused=True)) is None
    assert remote_reading(FakeApp("over")) is None
    assert remote_reading(FakeApp("complete")) is None


def test_d_266_it_asks_once_at_a_time_and_holds_the_keys_answered() -> None:
    app = FakeApp()
    server = FakeServer()
    player = RemotePlayer(app, server)
    player.tick()
    player.tick()  # still waiting: no second question
    assert len(server.asked) == 1
    assert server.asked[0][0] == AI_PATH
    server.answer(["ArrowUp", "Space"])
    assert app.controls.keys == [("ArrowUp", True), ("Space", True)]
    app.controls.keys.clear()
    player.tick()
    server.answer(["ArrowLeft", "Space"])
    # The arrow let go, the new one pressed, the one still held sent down again.
    assert app.controls.keys == [("ArrowUp", False), ("ArrowLeft", True), ("Space", True)]


def test_d_266_out_of_a_level_or_without_an_answer_it_lets_every_key_go() -> None:
    app = FakeApp()
    server = FakeServer()
    player = RemotePlayer(app, server)
    player.tick()
    server.answer(["Space"])
    player.tick()
    server.answer(None)  # the server is gone
    assert app.controls.keys[-1] == ("Space", False)
    player.tick()
    app.phase = "over"  # the answer comes after the level ended
    server.answer(["Space"])
    assert app.controls.keys[-1] == ("Space", False)
    app.controls.keys.clear()
    player.tick()  # over: nothing asked, nothing held
    assert server.asked == []
    assert app.controls.keys == []


def test_d_266_install_asks_every_four_frames() -> None:
    started: list[tuple[Any, float]] = []
    server = FakeServer()
    player = install_remote_player(
        FakeApp(), lambda tick, seconds: started.append((tick, seconds)), server
    )
    assert isinstance(player, RemotePlayer)
    assert started[0][1] == AI_SECONDS == pytest.approx(4 / 60)
    started[0][0]()
    assert len(server.asked) == 1


def test_d_266_posting_is_javascript_only() -> None:
    """`fetch` runs only in the browser: CPython runs its empty placeholder."""
    assert post_json(AI_PATH, {}, lambda keys: keys) is None
