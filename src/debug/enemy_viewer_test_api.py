"""The e2e test API of the `enemies/` page, ported from `debug/enemy-viewer-test-api.ts` (ENG-52),
installed as `window.__ENEMIES_TEST__` in e2e builds only."""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any, Protocol  # noqa: E402

from debug.viewer_test_api import ViewerStepHooks  # noqa: E402

__pragma__("noskip")

from debug.viewer_test_api import define_test_global, step_frames  # noqa: E402

__pragma__("skip")


class EnemyViewerHooks(ViewerStepHooks, Protocol):
    """The hooks of the `enemies/` page: the frame and render hooks, and the state it reports."""

    def state(self) -> Any:
        """What `getState()` returns (a plain JavaScript object)."""
        ...


__pragma__("noskip")


class EnemyViewerTestApi:
    """The e2e test API of the `enemies/` page (ENG-52)."""

    def __init__(self, hooks: EnemyViewerHooks) -> None:
        # The state hook itself, as the TypeScript object literal has it.
        self.getState = hooks.state

        def step(frames: int) -> None:
            step_frames(hooks, frames)

        self.step = step


def install_enemy_viewer_test_api(target: Any, hooks: EnemyViewerHooks) -> EnemyViewerTestApi:
    """Installs `__ENEMIES_TEST__` on `target` (the window). Only call it when `__E2E__` is true."""
    api = EnemyViewerTestApi(hooks)
    define_test_global(target, "__ENEMIES_TEST__", api)
    return api
