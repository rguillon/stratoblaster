"""The e2e test API of the game (ENG-52), ported from `debug/test-api.ts`, installed as
`window.__GAME_TEST__` in e2e builds only.

Results are plain JavaScript objects with the TypeScript key names (`highScore`, `loadingProgress`,
`sendAction`...): the test scripts read them from JavaScript. The `perf` numbers are copied into
camelCase keys here, the TypeScript shape, whatever the Python attribute names are.
"""

from org.transcrypt.stubs.browser import __pragma__, window

__pragma__("skip")
from typing import Any, Protocol  # noqa: E402

from ui.perf_overlay import PerfNumbers  # noqa: E402

__pragma__("noskip")

from debug.viewer_test_api import (  # noqa: E402
    check_frames,
    define_test_global,
    new_js_object,
    throw_range_error,
    throw_type_error,
)
from input.menu_action import is_menu_action  # noqa: E402
from ui.screens.elements import array_from  # noqa: E402


class GameTestAudio:
    """What the test API reads of the audio (P12-R12): `music`, `sounds` and the `context` state."""

    def __init__(self, music: str | None, sounds: list[str], context: str) -> None:
        self.music = music
        self.sounds = sounds
        self.context = context


__pragma__("skip")


class GameTestHooks(Protocol):
    """What the test API reads from and sends to the running app."""

    # Frames per second of `step`.
    step_hz: float

    def state(self) -> Any:
        """The state of the app, as a plain JavaScript object without the keys the test API adds
        itself (`loadingProgress`, `game`, `highScore`, `music`, `sounds`, `audio`, `perf`).
        """
        ...

    def audio(self) -> GameTestAudio: ...

    def high_score(self) -> int: ...

    def loading_progress(self) -> list[float]: ...

    def game(self) -> Any:
        """The level being played (a plain JavaScript object), or undefined."""
        ...

    def send(self, action: str) -> None: ...

    def bomb(self) -> None: ...

    def step(self, frames: int, render: bool) -> None: ...

    def perf(self) -> PerfNumbers: ...

    def readability(self, bright_share: float) -> Any:
        """How readable the level's frame is (P14-R08), a promise; null off the game screen."""
        ...


__pragma__("noskip")


def _perf_to_js(numbers: PerfNumbers) -> Any:
    """`PerfNumbers` as the TypeScript object: camelCase keys, null for a missing time."""
    result = new_js_object()
    result.longFrames = numbers.long_frames
    result.longestFrame = numbers.longest_frame
    result.frames = numbers.frames
    result.lastLoad = numbers.last_load
    result.longestLoadStep = numbers.longest_load_step
    return result


class GameTestApi:
    """The e2e test API (ENG-52): `getState`, `sendAction`, `step`, `advance` and `readability`.
    Each is a plain function property, as the TypeScript object literal has it.
    """

    def __init__(self, hooks: GameTestHooks) -> None:
        def get_state() -> Any:
            result = window.Object.assign(new_js_object(), hooks.state())
            audio = hooks.audio()
            result.music = audio.music
            result.sounds = array_from(audio.sounds)
            result.audio = audio.context
            result.highScore = hooks.high_score()
            result.loadingProgress = array_from(hooks.loading_progress())
            game = hooks.game()
            result.game = game or None
            result.perf = _perf_to_js(hooks.perf())
            return result

        def send_action(action: str) -> None:
            if action == "bomb":
                hooks.bomb()
                return
            if not is_menu_action(action):
                throw_type_error('Unknown menu action "' + str(action) + '"')
            hooks.send(action)

        def step(frames: int, render: bool = True) -> None:
            check_frames(frames)
            hooks.step(frames, render)

        def advance(seconds: float) -> None:
            if not (seconds >= 0):
                throw_range_error("Cannot advance by " + str(seconds) + " s")
            hooks.step(window.Math.ceil(seconds * hooks.step_hz - 1e-9), True)

        def readability(bright_share: float) -> Any:
            if not (bright_share >= 0 and bright_share <= 1):
                throw_range_error("Cannot measure with a share of " + str(bright_share))
            return hooks.readability(bright_share)

        self.getState = get_state
        self.sendAction = send_action
        self.step = step
        self.advance = advance
        self.readability = readability


def install_test_api(target: Any, hooks: GameTestHooks) -> GameTestApi:
    """Installs `__GAME_TEST__` on `target` (the window). Only call it when `__E2E__` is true."""
    api = GameTestApi(hooks)
    define_test_global(target, "__GAME_TEST__", api)
    return api
