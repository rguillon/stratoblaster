"""The e2e test API (ENG-52): `window.__GAME_TEST__`, installed by `main.py` in e2e builds only.

`main.py` imports this module inside `__pragma__("ifdef", "e2e")`, so the production bundle has
none of it (`make build` checks the name is absent). The snapshots are plain JavaScript objects
with camelCase key names (`selectedId`, `levelResult`...): the e2e tests read them from
JavaScript, and Playwright copies them out of the page.

- `getState()`: the menus, the level being played (`app/game_play_state.py`), the audio and the
  perf numbers;
- `sendAction(action)`: a menu action as an input device would send it (P01-R12; `pause` and
  `resume`, P12-R12), or `bomb`, as the bomb key (P11-R08);
- `step(frames, render)`: runs `frames` frames of 1/60 s at once, then renders once unless
  `render` is false. The app has no render loop in e2e builds: nothing moves between two calls;
- `advance(seconds)`: steps by `seconds`, rounded up to whole frames;
- `readability(share)`: how readable the level's frame is (P14-R08), a promise; null off the game
  screen.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from input.menu_action import is_menu_action
from render.babylon import js_object, js_set

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


def _checkpoint(checkpoint: Any) -> Any:
    """Where a Continue starts from (P07-R08, P11-R04), or None."""
    if checkpoint is None:
        return None
    result = js_object()
    js_set(result, "progress", checkpoint.progress)
    js_set(result, "bossesPassed", checkpoint.bosses_passed)
    js_set(result, "score", checkpoint.score)
    return result


def level_result_state(result: Any) -> Any:
    """The "Level complete" / "Game over" result (P06-R03, P11-R03), or None."""
    if result is None:
        return None
    state = js_object()
    js_set(state, "levelId", result.level_id)
    js_set(state, "destroyed", result.destroyed)
    js_set(state, "spawned", result.spawned)
    js_set(state, "outcome", result.outcome)
    js_set(state, "score", result.score)
    if result.new_high_score is not None:
        js_set(state, "newHighScore", result.new_high_score)
    js_set(state, "checkpoint", _checkpoint(result.checkpoint))
    return state


def _volumes(volumes: Any) -> Any:
    result = js_object()
    js_set(result, "music", volumes.music)
    js_set(result, "sfx", volumes.sfx)
    return result


def _perf(numbers: Any) -> Any:
    """What the perf monitor measured (P13-R01), in ms."""
    result = js_object()
    js_set(result, "longFrames", numbers.long_frames)
    js_set(result, "longestFrame", numbers.longest_frame)
    js_set(result, "frames", numbers.frames)
    js_set(result, "lastLoad", numbers.last_load)
    js_set(result, "longestLoadStep", numbers.longest_load_step)
    return result


def game_test_state(app: Any) -> Any:
    """What `__GAME_TEST__.getState()` returns for the running `app` (`RunningApp`)."""
    menu = app.menu
    flow = menu.flow.state
    audio = app.audio.state
    play = app.game()
    state = js_object()
    js_set(state, "screen", flow.screen)
    js_set(state, "selection", flow.selection)
    js_set(state, "selectedId", flow.selected_id)
    js_set(state, "highlightedShipId", flow.highlighted_ship_id)
    js_set(state, "chosenShipId", flow.chosen_ship_id)
    js_set(state, "chosenLevelId", flow.chosen_level_id)
    js_set(state, "transitioning", flow.transitioning)
    js_set(state, "levelResult", level_result_state(flow.level_result))
    js_set(state, "choice", flow.choice)
    js_set(state, "attempt", flow.attempt)
    js_set(state, "paused", flow.paused)
    js_set(state, "leaving", flow.leaving)
    js_set(state, "volumes", _volumes(flow.volumes))
    js_set(state, "music", audio.music)
    js_set(state, "sounds", list(audio.sounds))
    js_set(state, "audio", audio.context)
    js_set(state, "highScore", menu.high_score)
    js_set(state, "loadingProgress", list(app.loading_progress))
    js_set(state, "game", play.state if play is not None else None)
    js_set(state, "perf", _perf(app.perf.numbers))
    return state


def send_test_action(app: Any, action: str) -> None:
    """`__GAME_TEST__.sendAction`: `bomb` sets a bomb off (P11-R08); any other action is a menu
    action (P01-R12)."""
    if action == "bomb":
        app.controls.bomb()
        return
    if not is_menu_action(action):
        raise ValueError('Unknown menu action "' + str(action) + '"')
    app.command(action)


def step_test_frames(app: Any, frames: Any, render: Any) -> None:
    """`__GAME_TEST__.step`: `render` left out (undefined in JavaScript) renders."""
    if not (frames >= 0 and int(frames) == frames):
        raise ValueError("Cannot step by " + str(frames) + " frames")
    app.step(frames, render is not False)


def frames_in(seconds: float, step_seconds: float) -> int:
    """Whole frames of `step_seconds` that last at least `seconds`."""
    if not seconds >= 0:
        raise ValueError("Cannot advance by " + str(seconds) + " s")
    return int(math.ceil(seconds / step_seconds - 1e-9))


def measure_readability(app: Any, bright_share: float) -> Any:
    """`__GAME_TEST__.readability`: a promise of the report (P14-R08), or of null off a level."""
    if not (bright_share >= 0 and bright_share <= 1):
        raise ValueError("Cannot measure with a share of " + str(bright_share))
    play = app.game()
    if play is None:
        return _resolved(None)
    return play.readability(bright_share)


def _resolved(value: Any) -> Any:
    """A promise of `value`."""
    __pragma__("js", "{}", "return Promise.resolve(value);")
    return value


def install_test_api(target: Any, app: Any) -> Any:
    """Installs `__GAME_TEST__` on `target` (the window) for `app`. Returns the API."""
    api = js_object()

    def get_state() -> Any:
        return game_test_state(app)

    def send_action(action: str) -> None:
        send_test_action(app, action)

    def step(frames: Any, render: Any) -> None:
        step_test_frames(app, frames, render)

    def advance(seconds: float) -> None:
        app.step(frames_in(seconds, app.clock.step_seconds), True)

    def readability(bright_share: float) -> Any:
        return measure_readability(app, bright_share)

    js_set(api, "getState", get_state)
    js_set(api, "sendAction", send_action)
    js_set(api, "step", step)
    js_set(api, "advance", advance)
    js_set(api, "readability", readability)
    js_set(target, "__GAME_TEST__", api)
    return api
