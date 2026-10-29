"""The e2e test API of the `bosses/` page, ported from `debug/boss-viewer-test-api.ts` (ENG-52,
P07-R09), installed as `window.__BOSSES_TEST__` in e2e builds only."""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any, Protocol  # noqa: E402

from debug.viewer_test_api import ViewerStepHooks  # noqa: E402

__pragma__("noskip")

from debug.viewer_test_api import define_test_global, step_frames  # noqa: E402

__pragma__("skip")


class BossViewerHooks(ViewerStepHooks, Protocol):
    """The hooks of the `bosses/` page: the frame and render hooks, and the state it reports."""

    def state(self) -> Any:
        """What `getState()` returns (a plain JavaScript object, P07-R09)."""
        ...


__pragma__("noskip")


class BossViewerTestApi:
    """The e2e test API of the `bosses/` page (ENG-52, P07-R09)."""

    def __init__(self, hooks: BossViewerHooks) -> None:
        # The state hook itself, as the TypeScript object literal has it.
        self.getState = hooks.state

        def step(frames: int) -> None:
            step_frames(hooks, frames)

        self.step = step


def install_boss_viewer_test_api(target: Any, hooks: BossViewerHooks) -> BossViewerTestApi:
    """Installs `__BOSSES_TEST__` on `target` (the window). Only call it when `__E2E__` is true."""
    api = BossViewerTestApi(hooks)
    define_test_global(target, "__BOSSES_TEST__", api)
    return api
