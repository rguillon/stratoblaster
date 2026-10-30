"""Unit tests of `src/debug/test_api.py` (ENG-52: the e2e test API, `window.__GAME_TEST__`)."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers import js_shims

from debug import test_api
from debug.test_api import (
    frames_in,
    game_test_state,
    install_test_api,
    level_result_state,
    send_test_action,
    step_test_frames,
)


@pytest.fixture(autouse=True)
def js_twins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(test_api, "js_object", js_shims.js_object)
    monkeypatch.setattr(test_api, "js_set", js_shims.js_set)
    monkeypatch.setattr(test_api, "_resolved", lambda value: ("resolved", value))


class FakeApp:
    """What the test API reads from and sends to `RunningApp`."""

    def __init__(self, play: Any = None, result: Any = None) -> None:
        flow = SimpleNamespace(
            screen="level-select",
            selection=2,
            selected_id="1-3",
            highlighted_ship_id="heavy",
            chosen_ship_id="heavy",
            chosen_level_id=None,
            transitioning=False,
            level_result=result,
            choice=0,
            attempt=1,
            paused=False,
            leaving=False,
            volumes=SimpleNamespace(music=6, sfx=8),
        )
        self.menu = SimpleNamespace(flow=SimpleNamespace(state=flow), high_score=1200)
        self.audio = SimpleNamespace(
            state=SimpleNamespace(music="menu", sounds=["menu-move"], context="running")
        )
        self.perf = SimpleNamespace(
            numbers=SimpleNamespace(
                long_frames=1, longest_frame=60.0, frames=90, last_load=None, longest_load_step=None
            )
        )
        self.loading_progress = [0, 0.5, 1]
        self.clock = SimpleNamespace(step_seconds=1 / 60)
        self.controls = SimpleNamespace(bomb=self._bomb)
        self.play = play
        self.commands: list[str] = []
        self.steps: list[tuple[int, bool]] = []
        self.bombs = 0

    def _bomb(self) -> None:
        self.bombs += 1

    def game(self) -> Any:
        return self.play

    def command(self, action: str) -> None:
        self.commands.append(action)

    def step(self, frames: int, render: bool) -> None:
        self.steps.append((frames, render))


def test_eng_52_the_state_has_the_menus_audio_high_score_loading_and_perf_in_camel_case() -> None:
    state = game_test_state(FakeApp())
    assert state["screen"] == "level-select"
    assert state["selection"] == 2
    assert state["selectedId"] == "1-3"
    assert state["highlightedShipId"] == "heavy"
    assert state["chosenShipId"] == "heavy"
    assert state["chosenLevelId"] is None
    assert state["levelResult"] is None
    assert state["volumes"] == {"music": 6, "sfx": 8}
    assert state["music"] == "menu"
    assert state["sounds"] == ["menu-move"]
    assert state["audio"] == "running"
    assert state["highScore"] == 1200
    assert state["loadingProgress"] == [0, 0.5, 1]
    assert state["game"] is None
    assert state["perf"] == {
        "longFrames": 1,
        "longestFrame": 60.0,
        "frames": 90,
        "lastLoad": None,
        "longestLoadStep": None,
    }


def test_eng_52_the_state_copies_the_lists_so_the_app_keeps_its_own() -> None:
    app = FakeApp()
    state = game_test_state(app)
    state["sounds"].append("x")
    state["loadingProgress"].append(2)
    assert app.audio.state.sounds == ["menu-move"]
    assert app.loading_progress == [0, 0.5, 1]


def test_eng_52_the_state_has_the_level_being_played() -> None:
    app = FakeApp(play=SimpleNamespace(state={"levelId": "1-1"}))
    assert game_test_state(app)["game"] == {"levelId": "1-1"}


def test_p11_r03_p11_r04_the_level_result_has_its_high_score_and_checkpoint() -> None:
    checkpoint = SimpleNamespace(progress=0.5, bosses_passed=1, score=3000)
    result = SimpleNamespace(
        level_id="1-1",
        destroyed=4,
        spawned=9,
        outcome="over",
        score=3500,
        new_high_score=True,
        checkpoint=checkpoint,
    )
    assert level_result_state(result) == {
        "levelId": "1-1",
        "destroyed": 4,
        "spawned": 9,
        "outcome": "over",
        "score": 3500,
        "newHighScore": True,
        "checkpoint": {"progress": 0.5, "bossesPassed": 1, "score": 3000},
    }


def test_p06_r03_a_result_without_high_score_or_checkpoint_leaves_them_out() -> None:
    result = SimpleNamespace(
        level_id="1-2",
        destroyed=0,
        spawned=0,
        outcome="complete",
        score=0,
        new_high_score=None,
        checkpoint=None,
    )
    state = level_result_state(result)
    assert "newHighScore" not in state
    assert state["checkpoint"] is None


def test_p01_r12_p11_r08_send_action_sends_menu_actions_and_sets_bombs_off() -> None:
    app = FakeApp()
    send_test_action(app, "confirm")
    send_test_action(app, "pause")
    send_test_action(app, "bomb")
    assert app.commands == ["confirm", "pause"]
    assert app.bombs == 1


def test_eng_52_send_action_rejects_an_unknown_action() -> None:
    with pytest.raises(ValueError, match="jump"):
        send_test_action(FakeApp(), "jump")


def test_eng_52_step_renders_unless_render_is_false() -> None:
    app = FakeApp()
    step_test_frames(app, 3, None)
    step_test_frames(app, 1, False)
    step_test_frames(app, 0, True)
    assert app.steps == [(3, True), (1, False), (0, True)]


@pytest.mark.parametrize("frames", [-1, 1.5])
def test_eng_52_step_rejects_negative_or_partial_frames(frames: float) -> None:
    with pytest.raises(ValueError, match="Cannot step"):
        step_test_frames(FakeApp(), frames, True)


def test_eng_52_advance_rounds_up_to_whole_frames() -> None:
    assert frames_in(1, 1 / 60) == 60
    assert frames_in(0.01, 1 / 60) == 1
    assert frames_in(0, 1 / 60) == 0
    with pytest.raises(ValueError, match="Cannot advance"):
        frames_in(-1, 1 / 60)


def test_eng_52_install_puts_the_api_on_the_target() -> None:
    play = SimpleNamespace(state=None, readability=lambda share: ("report", share))
    app = FakeApp(play=play)
    window: dict[str, Any] = {}
    api = install_test_api(window, app)
    assert window["__GAME_TEST__"] is api
    assert api["getState"]()["screen"] == "level-select"
    api["sendAction"]("down")
    api["step"](2, None)
    api["advance"](0.5)
    assert app.commands == ["down"]
    assert app.steps == [(2, True), (30, True)]
    assert api["readability"](0.02) == ("report", 0.02)
    with pytest.raises(ValueError, match="share"):
        api["readability"](2)


def test_p14_r08_readability_is_a_promise_of_null_off_a_level() -> None:
    api = install_test_api({}, FakeApp())
    assert api["readability"](0.5) == ("resolved", None)
