# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/debug/remote_player.py` (D-291: the AI player of `make serve-ai`)."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers import js_shims

from debug import play_scene as play_scene_module
from debug import remote_player
from debug.remote_player import (
    AI_PATH,
    RELEASE_SECONDS,
    STEPS_PER_DECISION,
    RemotePlayer,
    ask_json,
    install_remote_player,
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
    """`ask`: answers each question with the next of `answers` (None when there is none left)."""

    def __init__(self, *answers: Any) -> None:
        self.asked: list[tuple[str, Any]] = []
        self._answers = list(answers)

    def __call__(self, path: str, body: Any) -> Any:
        self.asked.append((path, body))
        return self._answers.pop(0) if self._answers else None


def _steps(player: RemotePlayer, count: int) -> None:
    for _ in range(count):
        player.step()


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


def test_d_268_it_asks_after_every_fourth_step_and_holds_the_keys_answered() -> None:
    app = FakeApp()
    server = FakeServer([["ArrowUp", "Space"], []], [["ArrowLeft", "Space"], ["KeyE"]])
    player = RemotePlayer(app, server)
    _steps(player, STEPS_PER_DECISION - 1)
    assert server.asked == []
    player.step()
    assert server.asked == [(AI_PATH, remote_reading(app))]
    assert app.controls.keys == [("ArrowUp", True), ("Space", True)]
    app.controls.keys.clear()
    _steps(player, STEPS_PER_DECISION)
    # The arrow let go, the new one pressed, the one still held sent down again.
    # And the switch key tapped: down and up, one press.
    assert app.controls.keys == [
        ("ArrowUp", False),
        ("ArrowLeft", True),
        ("Space", True),
        ("KeyE", True),
        ("KeyE", False),
    ]


def test_d_268_without_an_answer_or_out_of_a_level_it_lets_every_key_go() -> None:
    app = FakeApp()
    server = FakeServer([["Space"], []])
    player = RemotePlayer(app, server)
    _steps(player, STEPS_PER_DECISION)
    _steps(player, STEPS_PER_DECISION)  # the server is gone
    assert app.controls.keys[-1] == ("Space", False)
    app.phase = "over"
    _steps(player, STEPS_PER_DECISION)  # over: nothing asked
    assert len(server.asked) == 2


def test_d_268_out_of_a_level_the_tick_lets_go() -> None:
    app = FakeApp()
    player = RemotePlayer(app, FakeServer([["Space"], []]))
    _steps(player, STEPS_PER_DECISION)
    player.tick()  # still playing: kept
    assert app.controls.keys == [("Space", True)]
    app.paused = True
    player.tick()
    assert app.controls.keys[-1] == ("Space", False)


def test_d_268_install_watches_the_steps_and_ticks() -> None:
    app = FakeApp()
    watchers: list[Any] = []
    app.watch_steps = watchers.append  # type: ignore[attr-defined]
    started: list[tuple[Any, float]] = []
    server = FakeServer([["Space"], []])
    player = install_remote_player(
        app, lambda tick, seconds: started.append((tick, seconds)), server
    )
    assert isinstance(player, RemotePlayer)
    for _ in range(STEPS_PER_DECISION):
        watchers[0]("run")
    assert app.controls.keys == [("Space", True)]
    assert started[0][1] == RELEASE_SECONDS
    app.paused = True
    started[0][0]()
    assert app.controls.keys[-1] == ("Space", False)


def test_d_268_asking_is_javascript_only() -> None:
    """The request runs only in the browser: CPython runs its placeholder."""
    assert ask_json(AI_PATH, {}) is None
