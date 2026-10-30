"""The e2e test API of a viewer page, ported from `debug/viewer-test-api.ts` (ENG-52): one frame of
the page and its rendering, installed on `window` in e2e builds only."""

from org.transcrypt.stubs.browser import __pragma__, window

__pragma__("skip")
from typing import Any, Protocol  # noqa: E402


class ViewerStepHooks(Protocol):
    """What a viewer page's e2e test API drives: one frame of the page, and its rendering."""

    def frame(self, dt: float) -> None:
        """Advances the page by one frame of `dt` seconds, without rendering."""
        ...

    def render(self) -> None:
        """Renders the scene the page shows."""
        ...


__pragma__("noskip")


def throw_range_error(message: str) -> None:
    """Throws a JavaScript `RangeError` (the TypeScript test API throws one)."""
    __pragma__("js", "{}", "throw new RangeError(message);")


def throw_type_error(message: str) -> None:
    """Throws a JavaScript `TypeError`."""
    __pragma__("js", "{}", "throw new TypeError(message);")


def new_js_object() -> Any:
    """A plain JavaScript object `{}`. A Transcrypt dict literal is not one: the test API's
    results are read from JavaScript, so they are built with this.
    """
    __pragma__("js", "{}", "return {};")
    return None


def js_descriptor(value: Any) -> Any:
    """A plain JavaScript property descriptor `{ value, configurable: true }`."""
    __pragma__("js", "{}", "return {value: value, configurable: true};")
    return None


def define_test_global(target: Any, global_name: str, value: Any) -> None:
    """Installs `value` as `target[global_name]` (non-writable, configurable), as the TypeScript
    `Object.defineProperty` does.
    """
    window.Object.defineProperty(target, global_name, js_descriptor(value))


def check_frames(frames: Any) -> None:
    """Throws a RangeError unless `frames` is a non-negative whole number."""
    if not window.Number.isInteger(frames) or frames < 0:
        throw_range_error("Cannot step by " + str(frames) + " frames")


def step_frames(hooks: ViewerStepHooks, frames: int) -> None:
    """Advances a viewer page by `frames` frames of 1/60 s, then renders once (ENG-52). Viewer
    pages have no render loop in e2e builds: nothing moves between two calls.
    """
    check_frames(frames)
    for _ in range(frames):
        hooks.frame(1 / 60)
    hooks.render()


class ViewerTestApi:
    """The e2e test API of a viewer page that reports no state (`player_shots/`)."""

    def __init__(self, hooks: ViewerStepHooks) -> None:
        def step(frames: int) -> None:
            step_frames(hooks, frames)

        # A plain function property, as the TypeScript object literal has it: detaching it keeps
        # working.
        self.step = step


def install_viewer_test_api(
    target: Any,
    global_name: str,
    hooks: ViewerStepHooks,
) -> ViewerTestApi:
    """Installs a `ViewerTestApi` as `target[global_name]` (the window). Only call it when
    `__E2E__` is true.
    """
    api = ViewerTestApi(hooks)
    define_test_global(target, global_name, api)
    return api
