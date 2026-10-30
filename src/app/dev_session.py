"""The dev viewers of the app (D-199): the viewer the menu flow shows on its `dev-viewer` screen,
built when it opens and dropped when it closes; the mouse wheel over it.
"""

from org.transcrypt.stubs.browser import __pragma__

from app.dev_viewer import DevViewer
from config.dev_viewer import DEV_VIEWER_CONFIG as CFG

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from app.dev_catalog import DevItem  # noqa: E402

__pragma__("noskip")


def wheel_steps(total: float, step: float, most: int) -> int:
    """Whole steps of `step` in a wheel delta `total` (towards zero), at most `most` either way."""
    if step <= 0:
        return 0
    steps = int(abs(total) // step)
    steps = min(steps, most)
    return -steps if total < 0 else steps


class DevSession:
    """Runs the dev viewer the flow shows (see the module doc). `status_root`: the element whose
    `.dev-status` line the viewer's status is written into (None: not written). `command(action)`
    sends a menu command (the wheel moves through the items as the arrows do)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        engine: Any,
        game: Any,
        catalog: dict[str, list[DevItem]],
        environment: bool,
        status_root: Any,
        command: Any,
    ) -> None:
        self._engine = engine
        self._game = game
        self._catalog = catalog
        self._environment = environment
        self._status_root = status_root
        self._command = command
        self.viewer: DevViewer | None = None
        self._wheel = 0.0

    @property
    def active(self) -> bool:
        """Whether a dev viewer is shown."""
        return self.viewer is not None

    def sync(self, state: Any) -> None:
        """Opens, changes or closes the viewer as the flow's state says."""
        name = state.dev_viewer
        if name is None:
            self._drop()
            return
        if self.viewer is not None and self.viewer.viewer != name:
            self._drop()
        if self.viewer is None:
            items = self._catalog[name]
            self.viewer = DevViewer(self._engine, self._game, name, items, self._environment)
        self.viewer.show(state.selection, state.dev_close_up)

    def wheel(self, delta_y: float) -> None:
        """The wheel turned by `delta_y` pixels: the levels viewer scrubs; the others show the next
        items (down) or the ones before (up), one per `wheel_step`."""
        viewer = self.viewer
        if viewer is None:
            return
        if viewer.viewer == "levels":
            viewer.scrub(delta_y)
            return
        self._wheel += delta_y
        steps = wheel_steps(self._wheel, CFG.wheel_step, int(CFG.max_wheel_steps))
        if steps == 0:
            return
        self._wheel = 0.0
        action = "right" if steps > 0 else "left"
        for _ in range(abs(steps)):
            self._command(action)

    def turn(self, dx: float, dy: float) -> None:
        """A drag over the viewer, by (`dx`, `dy`) screen pixels, turns its model."""
        if self.viewer is not None:
            self.viewer.turn(dx, dy)

    def frame(self, dt: float) -> None:
        """Moves the viewer on by `dt` seconds, and shows its status."""
        viewer = self.viewer
        if viewer is None:
            return
        viewer.frame(dt)
        if self._status_root is None:
            return
        # Read again each frame: the overlay makes a new line each time the item changes.
        line = self._status_root.querySelector(".dev-status")
        status = viewer.status
        if line and line.textContent != status:
            line.textContent = status

    def render(self) -> bool:
        """Draws the viewer's scene; False when there is none to draw yet."""
        scene = self.viewer.scene if self.viewer is not None else None
        if scene is None:
            return False
        scene.render()
        return True

    def _drop(self) -> None:
        if self.viewer is not None:
            self.viewer.dispose()
        self.viewer = None
        self._wheel = 0.0

    def dispose(self) -> None:
        self._drop()
